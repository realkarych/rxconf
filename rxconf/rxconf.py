import abc
import functools
import pathlib
import typing as tp

from rxconf import config_resolver, config_types
from rxconf.config_builder import FileConfigBuilder


class MetaRxConf(metaclass=abc.ABCMeta):

    def __init__(
        self: "MetaRxConf",
        config: config_types.ConfigType,
    ) -> None:
        self._config = config


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
    ) -> "RxConf":
        return cls(
            config=config_types.EnvConfig.load_from_environment(
                prefix=prefix,
            ),
        )

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._config, item.lower())

    def __repr__(self) -> str:
        return repr(self._config)


class AsyncRxConf(RxConf):

    @classmethod
    async def from_file_async(
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


class MetaReniewableRxConf(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def renew(self) -> RxConf:
        pass


class RenewableRxConf(MetaReniewableRxConf):

    def __init__(self, base_config: RxConf):
        self._base_rxconf = base_config

    def renew(self) -> RxConf:
        # TODO: Implement renewing logic
        return self._base_rxconf


class MetaObservable(metaclass=abc.ABCMeta):
    pass


class ObservableRxConf(MetaObservable):

    def __init__(self, renewable_rxconf: MetaReniewableRxConf) -> None:
        self._renewable_rxconf = renewable_rxconf

    def include_config(self, func: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
        @functools.wraps(func)
        def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            kwargs["config"] = self._renewable_rxconf.renew()
            return func(*args, **kwargs)

        return wrapper
