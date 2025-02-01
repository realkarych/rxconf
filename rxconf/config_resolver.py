import abc
import os
import pathlib
import typing as tp

from . import attributes, config_types, exceptions


class MetaConfigResolver(metaclass=abc.ABCMeta):  # pragma: no cover
    """Metaclass for deciding which config type should be used for a given config."""

    @abc.abstractmethod
    def resolve(self, *args, **kwargs) -> tp.Type[config_types.MetaConfigType]:
        """Resolve the config type for a given config file."""
        raise NotImplementedError()


class FileConfigResolver(MetaConfigResolver):
    """Decides which config type should be used for a given config file."""

    def __init__(self, config_types: tp.Iterable[tp.Type[config_types.FileConfigType]]) -> None:
        """
        :param config_types: List of config types to be used for resolving the config file.
        Check DefaultFileConfigResolver for the default list.
        You can provide your own list of config types if you want to extend the supported extensions.
        """

        self._config_types = config_types

    def resolve(
        self,
        path: tp.Union[str, pathlib.PurePath],
    ) -> tp.Type[config_types.FileConfigType]:
        """
        Resolve the config type for a given config file.
        :param path: Path to the config file in the local filesystem.
        Decision is based on the file extension.
        """

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
            f"Config file `{path}` has invalid extension: '{extension}'. "
            f"If you want to support this extension, "
            f"follow the tiny guideline: ..."
        )


DefaultFileConfigResolver: tp.Final[FileConfigResolver] = FileConfigResolver(
    config_types=config_types.BASE_FILE_CONFIG_TYPES,
)
