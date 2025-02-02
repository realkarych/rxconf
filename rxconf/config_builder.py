import abc
import pathlib
import typing as tp

from . import config_resolver as resolver
from . import config_types


class MetaConfigTypeBuilder(metaclass=abc.ABCMeta):  # pragma: no cover
    """Metaclass for building config types."""

    def __init__(self, config_resolver: resolver.MetaConfigResolver) -> None:
        self._config_resolver = config_resolver

    @abc.abstractmethod
    def build(self, *args, **kwargs) -> config_types.MetaConfigType:
        """Function to build a config type."""

        raise NotImplementedError()


class FileConfigTypeBuilder(MetaConfigTypeBuilder):
    """A builder for file-based config types."""

    def __init__(self, config_resolver: resolver.FileConfigResolver) -> None:
        self._config_resolver: resolver.FileConfigResolver = config_resolver

    def build(
        self: "FileConfigTypeBuilder",
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> config_types.FileConfigType:
        """
        Build a file-based config type.
        :param path: The path to the file on local filesystem.
        :param encoding: The encoding to use when reading the file.
        """

        return self._config_resolver.resolve(path=path).load_from_path(
            path=path,
            encoding=encoding,
        )

    async def build_async(
        self,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> config_types.FileConfigType:
        """
        Build a file-based config type asynchronously.
        :param path: The path to the file on local filesystem.
        :param encoding: The encoding to use when reading the file.
        """

        return await self._config_resolver.resolve(path=path).load_from_path_async(
            path=path,
            encoding=encoding,
        )
