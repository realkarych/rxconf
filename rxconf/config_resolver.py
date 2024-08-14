import os
import pathlib
import typing as tp
from abc import ABCMeta

from rxconf import attributes, exceptions
from rxconf.config_types import ConfigType, FileConfigType


class ConfigResolver(metaclass=ABCMeta):

    def __init__(self, config_types: tp.Iterable[tp.Type[ConfigType]]) -> None:
        self._config_types = config_types


class FileConfigResolver(ConfigResolver, metaclass=ABCMeta):

    def __init__(self, config_types: tp.List[tp.Type[FileConfigType]]) -> None:
        self._config_types = config_types

    def resolve(self, path: tp.Union[str, pathlib.PurePath]) -> tp.Type[FileConfigType]:
        _, extension = os.path.splitext(path)
        for config_type in self._config_types:
            if extension in config_type(
                root_attribute=attributes.MockAttribute(),
            ).allowed_extensions:
                return config_type

        # TODO: add here link how to patch the extensions.
        raise exceptions.InvalidExtensionError(
            f"Config file {path} has invalid extension: {extension}."
            f"If you want to add support for this extension, "
            f"follow the tiny guideline: ..."
        )
