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


class MetaRxConf(MetaTree, metaclass=abc.ABCMeta):  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    def from_file(
        cls: tp.Type["MetaRxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "MetaRxConf":
        pass

    @classmethod
    @abc.abstractmethod
    def from_env(
        cls: tp.Type["MetaRxConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "MetaRxConf":
        pass


class AsyncMetaRxConf(MetaTree, metaclass=abc.ABCMeta):  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    async def from_file(
        cls: tp.Type["AsyncMetaRxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "AsyncMetaRxConf":
        pass

    @classmethod
    @abc.abstractmethod
    async def from_env(
        cls: tp.Type["AsyncMetaRxConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "AsyncMetaRxConf":
        pass


class RxConf(MetaRxConf):

    def __init__(self, config: config_types.ConfigType) -> None:
        super().__init__(config)

    @classmethod
    def from_file(
        cls: tp.Type["RxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "RxConf":
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
        cls: tp.Type["RxConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "RxConf":
        return cls(
            config=config_types.EnvConfig.load_from_environment(
                prefix=prefix,
                remove_prefix=remove_prefix,
            ),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RxConf):
            raise TypeError("RxConf is comparable only to RxConf")
        return self._config == other._config

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._config, item.lower())

    def __repr__(self) -> str:
        return repr(self._config)


class AsyncRxConf(AsyncMetaRxConf):

    def __init__(self, config: config_types.ConfigType) -> None:
        super().__init__(config)

    @classmethod
    async def from_file(
        cls: tp.Type["AsyncRxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "AsyncRxConf":
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
        cls: tp.Type["AsyncRxConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "AsyncRxConf":
        return cls(
            config=config_types.EnvConfig.load_from_environment(
                prefix=prefix,
                remove_prefix=remove_prefix,
            ),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncRxConf):
            raise TypeError("AsyncRxConf is comparable only to AsyncRxConf")
        return self._config == other._config

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._config, item.lower())

    def __repr__(self) -> str:
        return repr(self._config)
