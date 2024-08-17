import datetime
import os
import typing as tp
from abc import ABCMeta, abstractmethod
from pathlib import PurePath

import yaml

import rxconf
from rxconf import attributes as attrs
from rxconf import exceptions


class ConfigType(metaclass=ABCMeta):

    @abstractmethod
    def __getattr__(self, item: str) -> tp.Any:
        raise NotImplementedError()


class FileConfigType(ConfigType, metaclass=ABCMeta):

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
            return attrs.YamlAttribute(
                value={cls._process_data(item) for item in data}
            )
        elif isinstance(data, (bool, int, str, float, type(None), datetime.date, datetime.datetime)):
            return attrs.YamlAttribute(value=data)
        else:
            raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")
