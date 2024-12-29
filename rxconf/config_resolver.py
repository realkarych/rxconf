import os
import pathlib
import typing as tp
from abc import ABCMeta, abstractmethod

from rxconf import attributes, config_types, exceptions


class ConfigResolver(metaclass=ABCMeta):  # pragma: no cover

    @abstractmethod
    def resolve(self, *args, **kwargs) -> tp.Type[config_types.ConfigType]:
        raise NotImplementedError()


class FileConfigResolver(ConfigResolver):

    def __init__(self, config_types: tp.Iterable[tp.Type[config_types.FileConfigType]]) -> None:
        self._config_types = config_types

    def resolve(
        self,
        path: tp.Union[str, pathlib.PurePath],
    ) -> tp.Type[config_types.FileConfigType]:
        _, extension = os.path.splitext(path)
        extension = extension.lower()
        for config_type in self._config_types:
            if (
                extension
                in config_type(
                    root_attribute=attributes.MockAttribute(),
                    path=pathlib.Path(),
                ).allowed_extensions
            ):
                return config_type

        # TODO: add here link how to patch the extensions.
        raise exceptions.InvalidExtensionError(
            f"Config file `{path}` has invalid extension: {extension}. "
            f"If you want to support this extension, "
            f"follow the tiny guideline: ..."
        )


DefaultFileConfigResolver: tp.Final[FileConfigResolver] = FileConfigResolver(
    config_types=config_types.BASE_FILE_CONFIG_TYPES,
)
