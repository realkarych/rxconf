import abc
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
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "RxConf":
        return cls(
            config=FileConfigBuilder(
                config_resolver=file_config_resolver,
            ).build(
                path=config_path,
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
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "AsyncRxConf":
        return cls(
            config=await FileConfigBuilder(
                config_resolver=file_config_resolver,
            ).build_async(
                path=config_path,
            )
        )
