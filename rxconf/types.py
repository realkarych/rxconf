import datetime
import os
import typing as tp
from abc import ABCMeta, abstractmethod
from pathlib import PurePath

import yaml

from rxconf import attributes as attrs
from rxconf import exceptions


class ConfigType(metaclass=ABCMeta):
    pass


class FileConfigType(ConfigType):
    allowed_extensions: tp.FrozenSet[str]

    @classmethod
    @abstractmethod
    def load_from_path(cls, path: tp.Union[str, PurePath]) -> "FileConfigType":
        pass


class YamlConfig(FileConfigType):
    allowed_extensions = frozenset({".yaml", ".yml"})
    _root: tp.Final[attrs.YamlAttribute]

    def __init__(self, root_attribute: attrs.YamlAttribute) -> None:
        self._root = root_attribute

    @classmethod
    @exceptions.handle_unknown_exception
    def load_from_path(cls, path: tp.Union[str, PurePath]) -> "YamlConfig":
        _, extension = os.path.splitext(path)
        if extension not in cls.allowed_extensions:
            raise exceptions.InvalidExtensionError(
                f"Invalid file extension: {extension} (allowed: {cls.allowed_extensions})"
            )
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
            root_attribute=_YamlDataProcessor(data=yaml_data).start_processing()
        )


class _YamlDataProcessor:

    def __init__(self, data: tp.Any) -> None:
        self._data = data

    def start_processing(self) -> attrs.YamlAttribute:
        return self._process_data(self._data)

    def _process_data(self, data: tp.Any) -> attrs.YamlAttribute:
        if isinstance(data, dict):
            return attrs.YamlAttribute(
                value={k: self._process_data(v) for k, v in data.items()}
            )
        elif isinstance(data, list):
            return attrs.YamlAttribute(
                value=[
                    self._process_data(item) if not isinstance(item, dict) else attrs.YamlAttribute(
                        value={k: self._process_data(v) for k, v in item.items()}
                    ) for item in data
                ]
            )
        elif isinstance(data, set):
            return attrs.YamlAttribute(
                value={self._process_data(item) for item in data}
            )
        elif isinstance(data, (str, int, float, bool, type(None))):
            return attrs.YamlAttribute(value=data)
        elif isinstance(data, (datetime.date, datetime.datetime)):
            return attrs.YamlAttribute(value=data)
        else:
            raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")
