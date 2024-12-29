import datetime
import json
import os
import sys
import typing as tp
from abc import ABCMeta, abstractmethod
from pathlib import PurePath

import aiofiles
import dotenv
import yaml

from rxconf import hashtools, types


if sys.version_info >= (3, 11):
    import tomllib as toml
else:
    import toml

import configparser

import rxconf
from rxconf import attributes as attrs
from rxconf import exceptions


class ConfigType(metaclass=ABCMeta):  # pragma: no cover

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def __getattr__(self, item: str) -> tp.Any:
        raise NotImplementedError()

    @property
    @abstractmethod
    def hash(self) -> int:
        pass


class FileConfigType(ConfigType, metaclass=ABCMeta):  # pragma: no cover

    def __init__(self, root_attribute: attrs.AttributeType, path: PurePath, *args, **kwargs) -> None:
        pass

    @property
    @abstractmethod
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        pass

    @classmethod
    @abstractmethod
    def load_from_path(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "FileConfigType":
        pass

    @classmethod
    @abstractmethod
    async def load_from_path_async(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "FileConfigType":
        pass

    def __repr__(self) -> str:
        return repr(self._root)


class YamlConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".yaml", ".yml"})
    _root: tp.Final[rxconf.YamlAttribute]
    _path: tp.Final[PurePath]

    def __init__(
        self: "YamlConfig",
        root_attribute: rxconf.YamlAttribute,
        path: PurePath,
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
    def _load_yaml_data(cls, content: str, path: tp.Union[str, PurePath]) -> tp.Dict:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise exceptions.BrokenConfigSchemaError(f"Error while parsing yaml config: {path}") from exc

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "YamlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), encoding=encoding) as file:
            yaml_data = cls._load_yaml_data(file.read(), path)

        return cls(
            root_attribute=cls._process_data(yaml_data) if yaml_data is not None else attrs.YamlAttribute(value={}),
            path=path if isinstance(path, PurePath) else PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "YamlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), mode="r", encoding=encoding) as file:
            content = await file.read()
            yaml_data = cls._load_yaml_data(content, path)

        return cls(
            root_attribute=cls._process_data(yaml_data) if yaml_data is not None else attrs.YamlAttribute(value={}),
            path=path if isinstance(path, PurePath) else PurePath(path),
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> int:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attrs.YamlAttribute:
        if isinstance(data, dict):
            return attrs.YamlAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, list):
            return attrs.YamlAttribute(
                value=[
                    (
                        cls._process_data(item)
                        if not isinstance(item, dict)
                        else attrs.YamlAttribute(value={k.lower(): cls._process_data(v) for k, v in item.items()})
                    )
                    for item in data
                ]
            )
        if isinstance(data, set):
            return attrs.YamlAttribute(value={cls._process_data(item) for item in data})  # pragma: no cover
        if isinstance(data, (bool, int, str, float, type(None), datetime.date, datetime.datetime)):
            return attrs.YamlAttribute(value=data)
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class JsonConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".json"})
    _root: tp.Final[rxconf.JsonAttribute]
    _path: tp.Final[PurePath]

    def __init__(
        self: "JsonConfig",
        root_attribute: rxconf.JsonAttribute,
        path: PurePath,
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
    def _load_json_data(cls, content: str, path: tp.Union[str, PurePath]) -> tp.Dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise exceptions.BrokenConfigSchemaError(f"Error while parsing json config: {path}") from exc

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "JsonConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), encoding=encoding) as file:
            content = file.read()
            json_data = cls._load_json_data(content, path)

        return cls(
            root_attribute=cls._process_data(json_data), path=path if isinstance(path, PurePath) else PurePath(path)
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "JsonConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), mode="r", encoding=encoding) as file:
            content = await file.read()
            json_data = cls._load_json_data(content, path)

        return cls(
            root_attribute=cls._process_data(json_data) if json_data is not None else attrs.JsonAttribute(value={}),
            path=path if isinstance(path, PurePath) else PurePath(path)
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attrs.JsonAttribute:
        if isinstance(data, dict):
            return attrs.JsonAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, list):
            return attrs.JsonAttribute(
                value=[
                    (
                        cls._process_data(item)
                        if not isinstance(item, dict)
                        else attrs.JsonAttribute(value={k.lower(): cls._process_data(v) for k, v in item.items()})
                    )
                    for item in data
                ]
            )
        if isinstance(data, (bool, int, str, float, type(None))):
            return attrs.JsonAttribute(value=data)
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class TomlConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".toml"})
    _root: tp.Final[rxconf.TomlAttribute]
    _path: tp.Final[PurePath]

    def __init__(
        self: "TomlConfig",
        root_attribute: rxconf.TomlAttribute,
        path: PurePath,
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
    def _load_toml_data(cls, content: str, path: tp.Union[str, PurePath]) -> tp.Dict:
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
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "TomlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), "r", encoding=encoding) as file:
            content = file.read()
            toml_data = cls._load_toml_data(content, path)

        return cls(
            root_attribute=cls._process_data(toml_data), path=path if isinstance(path, PurePath) else PurePath(path)
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "TomlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), "r", encoding=encoding) as file:
            content = await file.read()
            toml_data = cls._load_toml_data(content, path)

        return cls(
            root_attribute=cls._process_data(toml_data), path=path if isinstance(path, PurePath) else PurePath(path)
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attrs.TomlAttribute:
        if isinstance(data, dict):
            return attrs.TomlAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, list):
            return attrs.TomlAttribute(
                value=[
                    (
                        cls._process_data(item)
                        if not isinstance(item, dict)
                        else attrs.TomlAttribute(value={
                            k.lower(): cls._process_data(v) for k, v in item.items()
                        })
                    )
                    for item in data
                ]
            )
        if isinstance(data, (bool, int, str, float, datetime.date, datetime.datetime)):
            return attrs.TomlAttribute(value=data)
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class IniConfig(FileConfigType):
    _allowed_extensions: tp.Final[frozenset] = frozenset({".ini"})
    _root: tp.Final[rxconf.IniAttribute]
    _path: tp.Final[PurePath]

    def __init__(
        self: "IniConfig",
        root_attribute: rxconf.IniAttribute,
        path: PurePath,
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
    def _load_ini_data(cls, content: str, path: tp.Union[str, PurePath]) -> tp.Dict:
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
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "IniConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), mode="r", encoding=encoding) as file:
            content = file.read()
            ini_data = cls._load_ini_data(content, path)

        return cls(
            root_attribute=cls._process_data(ini_data),
            path=path if isinstance(path, PurePath) else PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, PurePath],
        encoding: str,
    ) -> "IniConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        async with aiofiles.open(str(path), mode="r", encoding=encoding) as file:
            content = await file.read()
            ini_data = cls._load_ini_data(content, path)

        return cls(
            root_attribute=cls._process_data(ini_data),
            path=path if isinstance(path, PurePath) else PurePath(path),
        )

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attrs.IniAttribute:
        if isinstance(data, dict):
            return attrs.IniAttribute(value={k.lower(): cls._process_data(v) for k, v in data.items()})
        if isinstance(data, str):
            return attrs.IniAttribute(value=types.map_primitive(data))
        raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class EnvConfig(ConfigType):

    _root: tp.Final[rxconf.EnvAttribute]

    def __init__(self: "EnvConfig", root_attribute: rxconf.EnvAttribute) -> None:
        self._root = root_attribute
        self._hash = hashtools.compute_conf_hash(root_attribute)

    def __repr__(self) -> str:
        return repr(self._root)

    @exceptions.handle_unknown_exception
    def __eq__(self, other: ConfigType) -> bool:
        if not isinstance(other, ConfigType):
            raise TypeError("ConfigType is comparable only to ConfigType")
        return self._hash == other.hash

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

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
    def _process_data(cls, data: tp.Dict[str, str]) -> attrs.EnvAttribute:
        processed_data = {k.lower(): attrs.EnvAttribute(value=types.map_primitive(v)) for k, v in data.items()}
        return attrs.EnvAttribute(value=processed_data)


class DotenvConfig(FileConfigType, EnvConfig):

    _allowed_extensions: tp.Final[frozenset] = frozenset({".env"})
    _path: tp.Final[PurePath]

    def __init__(
        self: "DotenvConfig",
        root_attribute: rxconf.EnvAttribute,
        path: PurePath,
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
        path: tp.Union[str, PurePath] = ".env",
        encoding: str = "utf-8",
    ) -> FileConfigType:
        dotenv_values = dotenv.dotenv_values(dotenv_path=path, encoding=encoding)
        processed_values = {
            key.lower(): value
            for key, value in dotenv_values.items()
            if value is not None
        }
        root_attribute = cls._process_data(processed_values)
        return cls(
            root_attribute=root_attribute,
            path=path if isinstance(path, PurePath) else PurePath(path),
        )

    @classmethod
    @exceptions.handle_unknown_exception
    async def load_from_path_async(
        cls,
        path: tp.Union[str, PurePath] = ".env",
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
