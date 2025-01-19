import abc
import datetime
import json
import os
import pathlib
import sys
import typing as tp

import aiofiles
import dotenv
import hvac  # type: ignore
import yaml
from hvac.exceptions import VaultError  # type: ignore

from . import _types, attributes, exceptions, hashtools


if sys.version_info >= (3, 11):
    import tomllib as toml
else:
    import toml

import configparser


class ConfigType(metaclass=abc.ABCMeta):  # pragma: no cover

    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def hash(self) -> int:
        pass

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower().removeprefix(hashtools.ATTR_SAULT))


class VaultConfigType(ConfigType):

    def __init__(
        self,
        root_attribute: attributes.AttributeType,
        path: pathlib.PurePath,
    ) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def load_from_vault(
        cls,
        token: str,
        ip: str,
        path: pathlib.PurePath,
    ) -> "VaultConfigType":
        pass

    @classmethod
    @abc.abstractmethod
    async def load_from_vault_async(
        cls,
        token: str,
        ip: str,
        path: pathlib.PurePath,
    ) -> "VaultConfigType":
        raise NotImplementedError()

    def __repr__(self) -> str:
        return repr(self._root)


class VaultConfig(VaultConfigType):
    _root: tp.Final[attributes.VaultAttribute]
    _path: tp.Final[pathlib.PurePath]

    def __init__(
        self,
        root_attribute: attributes.VaultAttribute,
        path: pathlib.PurePath,
    ) -> None:
        self._root = root_attribute
        self._path = path
        self._hash = hashtools.compute_conf_hash(root_attribute)

    @property
    def hash(self) -> int:
        return self._hash

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_vault(
        cls,
        token: str,
        ip: str,
        path: pathlib.PurePath,
    ) -> "VaultConfig":
        try:
            client = hvac.Client(url=ip, token=token)
            response = client.secrets.kv.v2.read_secret_version(path=path, raise_on_deleted_version=True)
        except VaultError as exc:
            raise exceptions.RxConfError(f"Unable to retrieve Vault data from path={path}") from exc

        return cls(
            root_attribute=cls._process_data(response["data"]["data"]),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_vault_async(
        cls,
        token: str,
        ip: str,
        path: pathlib.PurePath,
    ) -> "VaultConfig":
        raise NotImplementedError("Async vault loading is not supported yet. Use sync method instead.")

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attributes.VaultAttribute:
        if isinstance(data, dict):
            return attributes.VaultAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, list):
            return attributes.VaultAttribute(
                value=[
                    (
                        cls._process_data(item)
                        if not isinstance(item, dict)
                        else attributes.VaultAttribute(value={k.lower(): cls._process_data(v) for k, v in item.items()})
                    )
                    for item in data
                ]
            )
        if isinstance(data, (bool, int, str, float, type(None))):
            return attributes.VaultAttribute(value=data)
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> int:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash


class FileConfigType(ConfigType, metaclass=abc.ABCMeta):  # pragma: no cover

    def __init__(self, root_attribute: attributes.AttributeType, path: pathlib.PurePath, *args, **kwargs) -> None:
        pass

    @property
    @abc.abstractmethod
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        pass

    @classmethod
    @abc.abstractmethod
    def load_from_path(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "FileConfigType":
        pass

    @classmethod
    @abc.abstractmethod
    async def load_from_path_async(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "FileConfigType":
        pass

    def __repr__(self) -> str:
        return repr(self._root)


class YamlConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".yaml", ".yml"})
    _root: tp.Final[attributes.YamlAttribute]
    _path: tp.Final[pathlib.PurePath]

    def __init__(
        self: "YamlConfig",
        root_attribute: attributes.YamlAttribute,
        path: pathlib.PurePath,
    ) -> None:
        self._root = root_attribute
        self._path = path
        self._hash = hashtools.compute_conf_hash(root_attribute)

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @property
    def hash(self) -> int:
        return self._hash

    @classmethod
    def _load_yaml_data(cls, content: str, path: tp.Union[str, pathlib.PurePath]) -> tp.Dict:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise exceptions.BrokenConfigSchemaError(f"Error while parsing yaml config: {path}") from exc

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "YamlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), encoding=encoding) as file:
            yaml_data = cls._load_yaml_data(file.read(), path)

        return cls(
            root_attribute=(
                cls._process_data(yaml_data) if yaml_data is not None else attributes.YamlAttribute(value={})
            ),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "YamlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), mode="r", encoding=encoding) as file:
            content = await file.read()
            yaml_data = cls._load_yaml_data(content, path)

        return cls(
            root_attribute=(
                cls._process_data(yaml_data) if yaml_data is not None else attributes.YamlAttribute(value={})
            ),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> int:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attributes.YamlAttribute:
        if isinstance(data, dict):
            return attributes.YamlAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, list):
            return attributes.YamlAttribute(
                value=[
                    (
                        cls._process_data(item)
                        if not isinstance(item, dict)
                        else attributes.YamlAttribute(value={k.lower(): cls._process_data(v) for k, v in item.items()})
                    )
                    for item in data
                ]
            )
        if isinstance(data, set):
            return attributes.YamlAttribute(value={cls._process_data(item) for item in data})  # pragma: no cover
        if isinstance(data, (bool, int, str, float, type(None), datetime.date, datetime.datetime)):
            return attributes.YamlAttribute(value=data)
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class JsonConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".json"})
    _root: tp.Final[attributes.JsonAttribute]
    _path: tp.Final[pathlib.PurePath]

    def __init__(
        self: "JsonConfig",
        root_attribute: attributes.JsonAttribute,
        path: pathlib.PurePath,
    ) -> None:
        self._root = root_attribute
        self._path = path
        self._hash = hashtools.compute_conf_hash(root_attribute)

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @property
    def hash(self) -> int:
        return self._hash

    @classmethod
    def _load_json_data(cls, content: str, path: tp.Union[str, pathlib.PurePath]) -> tp.Dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise exceptions.BrokenConfigSchemaError(f"Error while parsing json config: {path}") from exc

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "JsonConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), encoding=encoding) as file:
            content = file.read()
            json_data = cls._load_json_data(content, path)

        return cls(
            root_attribute=cls._process_data(json_data),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "JsonConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), mode="r", encoding=encoding) as file:
            content = await file.read()
            json_data = cls._load_json_data(content, path)

        return cls(
            root_attribute=(
                cls._process_data(json_data) if json_data is not None else attributes.JsonAttribute(value={})
            ),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attributes.JsonAttribute:
        if isinstance(data, dict):
            return attributes.JsonAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, list):
            return attributes.JsonAttribute(
                value=[
                    (
                        cls._process_data(item)
                        if not isinstance(item, dict)
                        else attributes.JsonAttribute(value={k.lower(): cls._process_data(v) for k, v in item.items()})
                    )
                    for item in data
                ]
            )
        if isinstance(data, (bool, int, str, float, type(None))):
            return attributes.JsonAttribute(value=data)
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class TomlConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".toml"})
    _root: tp.Final[attributes.TomlAttribute]
    _path: tp.Final[pathlib.PurePath]

    def __init__(
        self: "TomlConfig",
        root_attribute: attributes.TomlAttribute,
        path: pathlib.PurePath,
    ) -> None:
        self._root = root_attribute
        self._path = path
        self._hash = hashtools.compute_conf_hash(root_attribute)

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @property
    def hash(self) -> int:
        return self._hash

    @classmethod
    def _load_toml_data(cls, content: str, path: tp.Union[str, pathlib.PurePath]) -> tp.Dict:
        toml_decode_exc = (
            toml.TOMLDecodeError  # type: ignore[attr-defined]
            if sys.version_info >= (3, 11)
            else toml.TomlDecodeError  # type: ignore[attr-defined]
        )
        try:
            if sys.version_info >= (3, 11):
                return toml.loads(content)
            return toml.loads(content)  # pragma: no cover
        except toml_decode_exc as exc:
            raise exceptions.BrokenConfigSchemaError(f"Error while parsing toml config: {path}") from exc

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "TomlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), "r", encoding=encoding) as file:
            content = file.read()
            toml_data = cls._load_toml_data(content, path)

        return cls(
            root_attribute=cls._process_data(toml_data),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "TomlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), "r", encoding=encoding) as file:
            content = await file.read()
            toml_data = cls._load_toml_data(content, path)

        return cls(
            root_attribute=cls._process_data(toml_data),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attributes.TomlAttribute:
        if isinstance(data, dict):
            return attributes.TomlAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, list):
            return attributes.TomlAttribute(
                value=[
                    (
                        cls._process_data(item)
                        if not isinstance(item, dict)
                        else attributes.TomlAttribute(value={k.lower(): cls._process_data(v) for k, v in item.items()})
                    )
                    for item in data
                ]
            )
        if isinstance(data, (bool, int, str, float, datetime.date, datetime.datetime)):
            return attributes.TomlAttribute(value=data)
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class IniConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".ini"})
    _root: tp.Final[attributes.IniAttribute]
    _path: tp.Final[pathlib.PurePath]

    def __init__(
        self: "IniConfig",
        root_attribute: attributes.IniAttribute,
        path: pathlib.PurePath,
    ) -> None:
        self._root = root_attribute
        self._path = path
        self._hash = hashtools.compute_conf_hash(root_attribute)

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @property
    def hash(self) -> int:
        return self._hash

    @classmethod
    def _load_ini_data(cls, content: str, path: tp.Union[str, pathlib.PurePath]) -> tp.Dict:
        config = configparser.ConfigParser()
        try:
            config.read_string(content)
        except configparser.Error as exc:
            raise exceptions.BrokenConfigSchemaError(f"Error while parsing ini config: {path}") from exc

        ini_data: tp.Dict[tp.Any, tp.Any] = {}
        for section in config.sections():
            keys = section.split(".")
            current_level = ini_data
            for key in keys[:-1]:
                if key not in current_level:
                    current_level[key] = {}
                current_level = current_level[key]
            current_level[keys[-1]] = dict(config.items(section))
        return ini_data

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "IniConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), mode="r", encoding=encoding) as file:
            content = file.read()
            ini_data = cls._load_ini_data(content, path)

        return cls(
            root_attribute=cls._process_data(ini_data),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> "IniConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), mode="r", encoding=encoding) as file:
            content = await file.read()
            ini_data = cls._load_ini_data(content, path)

        return cls(
            root_attribute=cls._process_data(ini_data),
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attributes.IniAttribute:
        if isinstance(data, dict):
            return attributes.IniAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, str):
            return attributes.IniAttribute(value=_types.map_primitive(data))
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class EnvConfig(ConfigType):

    _root: tp.Final[attributes.EnvAttribute]

    def __init__(self: "EnvConfig", root_attribute: attributes.EnvAttribute) -> None:
        self._root = root_attribute
        self._hash = hashtools.compute_conf_hash(root_attribute)

    def __repr__(self) -> str:
        return repr(self._root)

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_environment(
        cls,
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "EnvConfig":
        if prefix and remove_prefix:
            env_vars = {
                k.lower().removeprefix(prefix.lower()).lstrip("_"): v
                for k, v in os.environ.items()
                if k.lower().startswith(prefix.lower())
            }
        elif prefix:
            env_vars = {k.lower(): v for k, v in os.environ.items() if k.lower().startswith(prefix.lower())}
        else:
            env_vars = {k.lower(): v for k, v in os.environ.items()}
        root_attribute = cls._process_data(env_vars)
        return cls(root_attribute=root_attribute)

    @property
    def hash(self) -> int:
        return self._hash

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Dict[str, str]) -> attributes.EnvAttribute:
        processed_data = {k.lower(): attributes.EnvAttribute(value=_types.map_primitive(v)) for k, v in data.items()}
        return attributes.EnvAttribute(value=processed_data)


class DotenvConfig(FileConfigType, EnvConfig):

    _allowed_extensions: tp.Final[frozenset] = frozenset({".env"})
    _path: tp.Final[pathlib.PurePath]

    def __init__(
        self: "DotenvConfig",
        root_attribute: attributes.EnvAttribute,
        path: pathlib.PurePath,
    ) -> None:
        self._root = root_attribute  # type: ignore
        self._path = path
        self._hash = hashtools.compute_conf_hash(root_attribute)

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @property
    def hash(self) -> int:
        return self._hash

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(
        cls,
        path: tp.Union[str, pathlib.PurePath] = ".env",
        encoding: str = "utf-8",
    ) -> FileConfigType:
        dotenv_values = dotenv.dotenv_values(dotenv_path=path, encoding=encoding)
        processed_values = {key.lower(): value for key, value in dotenv_values.items() if value is not None}
        root_attribute = cls._process_data(processed_values)
        return cls(
            root_attribute=root_attribute,
            path=path if isinstance(path, pathlib.PurePath) else pathlib.PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, pathlib.PurePath] = ".env",
        encoding: str = "utf-8",
    ) -> "FileConfigType":
        return cls.load_from_path(
            path=path,
            encoding=encoding,
        )


BASE_FILE_CONFIG_TYPES: tp.Final[tp.Tuple[tp.Type[FileConfigType], ...]] = (
    YamlConfig,
    JsonConfig,
    TomlConfig,
    IniConfig,
    DotenvConfig,
)
