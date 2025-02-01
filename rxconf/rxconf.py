import abc
import functools
import pathlib
import typing as tp

from . import config_builder, config_resolver, config_types, exceptions, hashtools


class MetaTree(metaclass=abc.ABCMeta):  # pragma: no cover

    def __init__(
        self: "MetaTree",
        config: config_types.ConfigType,
    ) -> None:
        self.__config = config

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return vars(self.__config) == vars(other._MetaTree__config)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @abc.abstractmethod
    def __getattr__(self, item: str) -> tp.Any:
        raise NotImplementedError()


class MetaConf(MetaTree, metaclass=abc.ABCMeta):  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    def from_file(
        cls: tp.Type["MetaConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "MetaConf":
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_env(
        cls: tp.Type["MetaConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "MetaConf":
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_vault(
        cls: tp.Type["MetaConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "MetaConf":
        raise NotImplementedError()


class MetaAsyncConf(MetaTree, metaclass=abc.ABCMeta):  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    async def from_file(
        cls: tp.Type["MetaAsyncConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "MetaAsyncConf":
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    async def from_env(
        cls: tp.Type["MetaAsyncConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "MetaAsyncConf":
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    async def from_vault(
        cls: tp.Type["MetaAsyncConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "MetaAsyncConf":
        raise NotImplementedError()


class MetaTrigger(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(
        self: "MetaTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> None:
        pass


class BaseTrigger(MetaTrigger):

    def __init__(
        self: "BaseTrigger",
        func: tp.Callable,
        args: tp.Optional[tp.Tuple[tp.Any, ...]] = None,
        kwargs: tp.Optional[tp.Dict[str, tp.Any]] = None,
    ) -> None:
        self._func = func
        self._args: tp.Tuple[tp.Any, ...] = args if args is not None else ()
        self._kwargs: tp.Dict[str, tp.Any] = kwargs if kwargs is not None else {}

    def __call__(
        self: "BaseTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> None:
        self._func(*self._args, **self._kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(func={self._func!r}, args={self._args!r}, kwargs={self._kwargs!r})"


class OnChangeTrigger(MetaTrigger):

    def __init__(
        self: "OnChangeTrigger",
        trigger: BaseTrigger,
        all_attributes: tp.Optional[tp.Tuple[str, ...]] = None,
        any_attributes: tp.Optional[tp.Tuple[str, ...]] = None,
    ) -> None:
        if (not all_attributes and not any_attributes) or (all_attributes and any_attributes):
            raise exceptions.RxConfError("You must provide either `all_attributes` or `any_attributes`.")
        self._trigger = trigger
        self._all_of_attributes: tp.Tuple[str, ...] = all_attributes if all_attributes is not None else ()
        self._any_of_attributes: tp.Tuple[str, ...] = any_attributes if any_attributes is not None else ()

    @property
    def all_of(self) -> tp.Tuple[str, ...]:
        return self._all_of_attributes

    @property
    def any_of(self) -> tp.Tuple[str, ...]:
        return self._any_of_attributes

    def __call__(
        self: "OnChangeTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> None:
        if any(
            (
                self._is_any_of_attributes_changed(old_conf=old_conf, actual_conf=actual_conf),
                self._is_all_attributes_changed(old_conf=old_conf, actual_conf=actual_conf),
            )
        ):
            self._trigger(
                old_conf=old_conf,
                actual_conf=actual_conf,
            )

    def _is_any_of_attributes_changed(
        self: "OnChangeTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> bool:
        return (
            any(
                self._is_attribute_changed(old_conf=old_conf, actual_conf=actual_conf, attribute_path=attr)
                for attr in self._any_of_attributes
            )
            if self._any_of_attributes
            else False
        )

    def _is_all_attributes_changed(
        self: "OnChangeTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> bool:
        return (
            all(
                self._is_attribute_changed(old_conf=old_conf, actual_conf=actual_conf, attribute_path=attr)
                for attr in self._all_of_attributes
            )
            if self._all_of_attributes
            else False
        )

    def _is_attribute_changed(
        self: "OnChangeTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
        attribute_path: str,
    ) -> bool:
        def get_nested_attr(conf: MetaConf, path: str) -> tp.Any:
            value = conf
            for attr in path.lower().split("."):
                value = getattr(value, attr)
            return value

        try:
            old_value = get_nested_attr(old_conf, attribute_path)
            new_value = get_nested_attr(actual_conf, attribute_path)
            return old_value != new_value

        except AttributeError as e:
            raise exceptions.RxConfError(f"Attribute '{attribute_path}' not found in configuration.") from e


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
            config=config_builder.FileConfigBuilder(
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
        return self._MetaTree__config == other._MetaTree__config

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._MetaTree__config, f"{hashtools.ATTR_SAULT}{item.lower()}")

    def __repr__(self) -> str:
        return repr(self._MetaTree__config)


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
            config=await config_builder.FileConfigBuilder(
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
        # TODO: add support for VaultConfig
        raise NotImplementedError("AsyncConf does not support VaultConfig yet. Use Conf instead.")  # pragma: no cover

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncConf):
            raise TypeError("AsyncConf is comparable only to AsyncConf")
        return self._MetaTree__config == other._MetaTree__config

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self._MetaTree__config, f"{hashtools.ATTR_SAULT}{item.lower()}")

    def __repr__(self) -> str:
        return repr(self._MetaTree__config)


class MetaConfFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_conf(
        self: "MetaConfFactory",
    ) -> MetaConf:
        raise NotImplementedError()


class FileConfFactory(MetaConfFactory):

    def __init__(
        self: "FileConfFactory",
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> None:
        self._config_path = config_path
        self._encoding = encoding
        self._file_config_resolver = file_config_resolver

    def create_conf(
        self: "FileConfFactory",
    ) -> Conf:
        return Conf.from_file(
            config_path=self._config_path,
            encoding=self._encoding,
            file_config_resolver=self._file_config_resolver,
        )


class EnvConfFactory(MetaConfFactory):

    def __init__(
        self: "EnvConfFactory",
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> None:
        self._prefix = prefix
        self._remove_prefix = remove_prefix

    def create_conf(
        self: "EnvConfFactory",
    ) -> Conf:
        return Conf.from_env(
            prefix=self._prefix,
            remove_prefix=self._remove_prefix,
        )


class VaultConfFactory(MetaConfFactory):

    def __init__(
        self: "VaultConfFactory",
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> None:
        self._token = token
        self._ip = ip
        self._path = path

    def create_conf(
        self: "VaultConfFactory",
    ) -> Conf:
        return Conf.from_vault(
            token=self._token,
            ip=self._ip,
            path=self._path,
        )


class IRxConf(MetaConf, metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def from_file(
        cls: tp.Type["IRxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "IRxConf":
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_env(
        cls: tp.Type["IRxConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "IRxConf":
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_vault(
        cls: tp.Type["IRxConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "IRxConf":
        raise NotImplementedError()

    @abc.abstractmethod
    def include_config(
        self: "IRxConf",
        triggers: tp.Optional[tp.Iterable[MetaTrigger]] = None,
    ) -> tp.Callable:
        raise NotImplementedError()


class RxConf(IRxConf):

    _current_conf: tp.Optional[MetaConf] = None

    def __init__(self, factory: MetaConfFactory, di_arg_name: str = "conf") -> None:
        self._factory = factory
        self._di_arg_name = di_arg_name

    @classmethod
    def from_file(
        cls: tp.Type["RxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "RxConf":
        return cls(
            factory=FileConfFactory(
                config_path=config_path, encoding=encoding, file_config_resolver=file_config_resolver
            )
        )

    @classmethod
    def from_env(
        cls: tp.Type["RxConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "RxConf":
        return cls(
            factory=EnvConfFactory(
                prefix=prefix,
                remove_prefix=remove_prefix,
            )
        )

    @classmethod
    def from_vault(
        cls: tp.Type["RxConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "RxConf":
        return cls(
            factory=VaultConfFactory(
                token=token,
                ip=ip,
                path=path,
            )
        )

    @property
    def current_conf(self) -> MetaConf:
        if self._current_conf is None:
            self._current_conf = self._factory.create_conf()
        return self._current_conf

    @current_conf.setter
    def current_conf(self, new_conf: MetaConf) -> None:
        self._current_conf = new_conf

    def include_config(
        self: "RxConf",
        triggers: tp.Optional[tp.Iterable[MetaTrigger]] = None,
    ) -> tp.Callable:
        def decorator(func: tp.Callable) -> tp.Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                new_conf = self._factory.create_conf()
                if new_conf != self.current_conf:
                    for trigger in triggers or []:
                        trigger(
                            old_conf=self.current_conf,
                            actual_conf=new_conf,
                        )
                self.current_conf = new_conf
                kwargs[self._di_arg_name] = self.current_conf
                return func(*args, **kwargs)

            return wrapper

        return decorator
