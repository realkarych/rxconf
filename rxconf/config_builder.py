import abc
import pathlib
import typing as tp

from . import config_resolver as resolver
from . import config_types


class ConfigBuilder(metaclass=abc.ABCMeta):  # pragma: no cover

    def __init__(self, config_resolver: resolver.ConfigResolver) -> None:
        self._config_resolver = config_resolver

    @abc.abstractmethod
    def build(self, *args, **kwargs) -> config_types.ConfigType:
        pass


class FileConfigBuilder(ConfigBuilder):

    def __init__(self, config_resolver: resolver.FileConfigResolver) -> None:
        self._config_resolver: resolver.FileConfigResolver = config_resolver

    def build(
        self: "FileConfigBuilder",
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> config_types.FileConfigType:
        return self._config_resolver.resolve(path=path).load_from_path(
            path=path,
            encoding=encoding,
        )

    async def build_async(
        self,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> config_types.FileConfigType:
        return await self._config_resolver.resolve(path=path).load_from_path_async(
            path=path,
            encoding=encoding,
        )
