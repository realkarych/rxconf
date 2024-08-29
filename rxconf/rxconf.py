import pathlib
import typing as tp

from rxconf import config_resolver, config_types


class RxConf:

    def __init__(
        self: "RxConf",
        config: config_types.ConfigType,
    ) -> None:
        self._config = config

    @classmethod
    def from_file(
        cls: tp.Type["RxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "RxConf":
        return cls(
            config=file_config_resolver.resolve(
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
