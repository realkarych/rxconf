import abc
import pathlib
import typing as tp
from rxconf.config_resolver import ConfigResolver, FileConfigResolver, VaultConfigResolver
from rxconf.config_types import ConfigType, FileConfigType


class ConfigBuilder(metaclass=abc.ABCMeta):  # pragma: no cover

    def __init__(self, config_resolver: ConfigResolver) -> None:
        self._config_resolver = config_resolver

    @abc.abstractmethod
    def build(self, *args, **kwargs) -> ConfigType:
        pass


class FileConfigBuilder(ConfigBuilder):

    def __init__(self, config_resolver: FileConfigResolver) -> None:
        self._config_resolver: FileConfigResolver = config_resolver

    def build(
        self: "FileConfigBuilder",
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> FileConfigType:
        return self._config_resolver.resolve(path=path).load_from_path(
            path=path,
            encoding=encoding,
        )

    async def build_async(
        self,
        path: tp.Union[str, pathlib.PurePath],
        encoding: str,
    ) -> FileConfigType:
        return await self._config_resolver.resolve(path=path).load_from_path_async(
            path=path,
            encoding=encoding,
        )


class VaultConfigBuilder(ConfigBuilder):

    def __init__(self, config_resolver: VaultConfigResolver) -> None:
        self._config_resolver: VaultConfigResolver = config_resolver

    def build(
        self,
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
        ext: str
    ) -> FileConfigType:
        return self._config_resolver.resolve(ext=ext).load_from_vault(
            token=token,
            ip=ip,
            path=path,
        )

    async def build_async(
        self,
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
        ext: str
    ) -> FileConfigType:
        pass
