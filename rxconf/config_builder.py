import abc
import pathlib
import typing as tp
from rxconf.config_resolver import ConfigResolver, FileConfigResolver
from rxconf.config_types import ConfigType, FileConfigType


class ConfigBuilder(metaclass=abc.ABCMeta):  # pragma: no cover

    def __init__(self, config_resolver: ConfigResolver) -> None:
        self._config_resolver = config_resolver

    @abc.abstractmethod
    def build(self, *args, **kwargs) -> ConfigType:
        pass


class FileConfigBuilder(ConfigBuilder):

    def __init__(self, config_resolver: FileConfigResolver) -> None:
        self._config_resolver = config_resolver

    def build(self, path: tp.Union[str, pathlib.PurePath]) -> FileConfigType:
        return self._config_resolver.resolve(path=path).load_from_path(path)

    async def build_async(self, path: tp.Union[str, pathlib.PurePath]) -> FileConfigType:
        return await self._config_resolver.resolve(path=path).load_from_path_async(path)
