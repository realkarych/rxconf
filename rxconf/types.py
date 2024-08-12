import os
import typing as tp
from abc import ABCMeta, abstractmethod
from pathlib import PurePath

import yaml

from rxconf import attributes as attrs
from rxconf import data_processors, exceptions


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
            root_attribute=data_processors.YamlDataProcessor(data=yaml_data).start_processing()
        )
