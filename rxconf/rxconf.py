from rxconf import config_resolver, config_types
import typing as tp
import pathlib


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

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._config, item)

    def __repr__(self) -> str:
        return repr(self._config)
