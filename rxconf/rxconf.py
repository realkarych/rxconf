import abc
import pathlib
import typing as tp

from rxconf import config_resolver, config_types
from rxconf.config_builder import FileConfigBuilder


class MetaTree(metaclass=abc.ABCMeta):  # pragma: no cover

    def __init__(
        self: "MetaTree",
        config: config_types.ConfigType,
    ) -> None:
        self._config = config

    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def __ne__(self, other: object) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def __getattr__(self, item: str) -> tp.Any:
        pass


class MetaConf(MetaTree, metaclass=abc.ABCMeta):  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    def from_file(
        cls: tp.Type["MetaConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "MetaConf":
        pass

    @classmethod
    @abc.abstractmethod
    def from_env(
        cls: tp.Type["MetaConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "MetaConf":
        pass

    @classmethod
    @abc.abstractmethod
    def from_vault(
        cls: tp.Type["MetaConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "MetaConf":
        pass


class MetaAsyncConf(MetaTree, metaclass=abc.ABCMeta):  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    async def from_file(
        cls: tp.Type["MetaAsyncConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "MetaAsyncConf":
        pass

    @classmethod
    @abc.abstractmethod
    async def from_env(
        cls: tp.Type["MetaAsyncConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "MetaAsyncConf":
        pass

    @classmethod
    @abc.abstractmethod
    async def from_vault(
        cls: tp.Type["MetaAsyncConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "MetaAsyncConf":
        pass


class Conf(MetaConf):

    def __init__(self, config: config_types.ConfigType) -> None:
        super().__init__(config)

    @classmethod
    def from_file(
        cls: tp.Type["Conf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "Conf":
        return cls(
            config=FileConfigBuilder(
                config_resolver=file_config_resolver,
            ).build(
                path=config_path,
                encoding=encoding,
            )
        )

    @classmethod
    def from_env(
        cls: tp.Type["Conf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "Conf":
        return cls(
            config=config_types.EnvConfig.load_from_environment(
                prefix=prefix,
                remove_prefix=remove_prefix,
            ),
        )

    @classmethod
    def from_vault(
        cls: tp.Type["Conf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "Conf":
        return cls(config=config_types.VaultConfig.load_from_vault(token=token, ip=ip, path=path))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Conf):
            raise TypeError("Conf is comparable only to Conf")
        return self._config == other._config

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._config, item.lower())

    def __repr__(self) -> str:
        return repr(self._config)


class AsyncConf(MetaAsyncConf):

    def __init__(self, config: config_types.ConfigType) -> None:
        super().__init__(config)

    @classmethod
    async def from_file(
        cls: tp.Type["AsyncConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "AsyncConf":
        return cls(
            config=await FileConfigBuilder(
                config_resolver=file_config_resolver,
            ).build_async(
                path=config_path,
                encoding=encoding,
            )
        )

    @classmethod
    async def from_env(
        cls: tp.Type["AsyncConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "AsyncConf":
        return cls(
            config=config_types.EnvConfig.load_from_environment(
                prefix=prefix,
                remove_prefix=remove_prefix,
            ),
        )

    @classmethod
    async def from_vault(
        cls: tp.Type["AsyncConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "AsyncConf":
        raise NotImplementedError()  # pragma: no cover

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncConf):
            raise TypeError("AsyncConf is comparable only to AsyncConf")
        return self._config == other._config

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._config, item.lower())

    def __repr__(self) -> str:
        return repr(self._config)
