import datetime
import json
import os
import sys
import typing as tp
from abc import ABCMeta, abstractmethod
from pathlib import PurePath

import yaml
from dotenv import load_dotenv

from rxconf import types


if sys.version_info >= (3, 11):
    import tomllib as toml
else:
    import toml

import rxconf
from rxconf import attributes as attrs
from rxconf import exceptions


class ConfigType(metaclass=ABCMeta):  # pragma: no cover

    @abstractmethod
    def __getattr__(self, item: str) -> tp.Any:
        raise NotImplementedError()


class FileConfigType(ConfigType, metaclass=ABCMeta):  # pragma: no cover

    def __init__(
        self: "FileConfigType",
        root_attribute: rxconf.AttributeType,
        path: PurePath,
    ) -> None:
        pass

    @property
    @abstractmethod
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        pass

    @classmethod
    @abstractmethod
    def load_from_path(cls, path: tp.Union[str, PurePath]) -> "FileConfigType":
        pass

    def __repr__(self) -> str:
        return self._root.__repr__()


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

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(cls, path: tp.Union[str, PurePath]) -> "YamlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path)) as file:
            try:
                yaml_data = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                raise exceptions.BrokenConfigSchemaError(
                    f"Error while parsing yaml config: {path}"
                ) from exc

        return cls(
            root_attribute=cls._process_data(yaml_data),
            path=path if isinstance(path, PurePath) else PurePath(path)
        )

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attrs.YamlAttribute:
        if isinstance(data, tp.Dict):
            return attrs.YamlAttribute(
                value={k.lower(): cls._process_data(v) for k, v in data.items()}
            )
        elif isinstance(data, tp.List):
            return attrs.YamlAttribute(
                value=[
                    cls._process_data(item) if not isinstance(item, dict) else attrs.YamlAttribute(
                        value={k.lower(): cls._process_data(v) for k, v in item.items()}
                    ) for item in data
                ]
            )
        elif isinstance(data, tp.Set):
            return attrs.YamlAttribute(  # pragma: no cover
                value={cls._process_data(item) for item in data}
            )
        elif isinstance(data, (bool, int, str, float, type(None), datetime.date, datetime.datetime)):
            return attrs.YamlAttribute(value=data)
        else:
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

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(cls, path: tp.Union[str, PurePath]) -> "JsonConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path)) as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError as exc:
                raise exceptions.BrokenConfigSchemaError(
                    f"Error while parsing json config: {path}"
                ) from exc

        return cls(
            root_attribute=cls._process_data(json_data),
            path=path if isinstance(path, PurePath) else PurePath(path)
        )

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attrs.JsonAttribute:
        if isinstance(data, dict):
            return attrs.JsonAttribute(
                value={k.lower(): cls._process_data(v) for k, v in data.items()}
            )
        elif isinstance(data, list):
            return attrs.JsonAttribute(
                value=[
                    cls._process_data(item) if not isinstance(item, dict) else attrs.JsonAttribute(
                        value={k.lower(): cls._process_data(v) for k, v in item.items()}
                    ) for item in data
                ]
            )
        elif isinstance(data, (bool, int, str, float, type(None))):
            return attrs.JsonAttribute(value=data)
        else:
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

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(cls, path: tp.Union[str, PurePath]) -> "TomlConfig":
        if not os.path.isfile(str(path)):
            raise exceptions.ConfigNotFoundError(f"Config file not found: {path}")
        with open(str(path), "r", encoding="utf-8") as file:
            toml_decode_exc = (
                toml.TOMLDecodeError  # type: ignore
                if sys.version_info >= (3, 11)
                else toml.TomlDecodeError  # type: ignore
            )
            try:
                if sys.version_info >= (3, 11):
                    toml_data = toml.loads(file.read())
                else:
                    toml_data = toml.load(file)  # pragma: no cover
            except toml_decode_exc as exc:
                raise exceptions.BrokenConfigSchemaError(
                    f"Error while parsing toml config: {path}"
                ) from exc

        return cls(
            root_attribute=cls._process_data(toml_data),
            path=path if isinstance(path, PurePath) else PurePath(path)
        )

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def _process_data(cls, data: tp.Any) -> attrs.TomlAttribute:
        if isinstance(data, dict):
            return attrs.TomlAttribute(
                value={k.lower(): cls._process_data(v) for k, v in data.items()}
            )
        elif isinstance(data, list):
            return attrs.TomlAttribute(
                value=[
                    cls._process_data(item) if not isinstance(item, dict) else attrs.TomlAttribute(
                        value={k.lower(): cls._process_data(v) for k, v in item.items()}
                    ) for item in data
                ]
            )
        elif isinstance(data, (bool, int, str, float, datetime.date, datetime.datetime)):
            return attrs.TomlAttribute(value=data)
        else:
            raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")  # pragma: no cover


class EnvConfig(ConfigType):

    _root: tp.Final[rxconf.EnvAttribute]

    def __init__(self: "EnvConfig", root_attribute: rxconf.EnvAttribute) -> None:
        self._root = root_attribute

    def __repr__(self) -> str:
        return repr(self._root)

    @exceptions.handle_unknown_exception
    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._root, item.lower())

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_environment(cls, prefix: tp.Optional[str] = None, **kwargs) -> "EnvConfig":
        env_vars = {
            k.lower(): v for k, v in os.environ.items()
            if prefix is None or k.lower().startswith(prefix.lower())
        }
        root_attribute = cls._process_data(env_vars)
        return cls(root_attribute=root_attribute, **kwargs)

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

    @property
    def allowed_extensions(self) -> tp.FrozenSet[str]:
        return self._allowed_extensions

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(cls, path: tp.Union[str, PurePath] = ".env") -> FileConfigType:
        load_dotenv(dotenv_path=path)
        return cls.load_from_environment(path=path)
