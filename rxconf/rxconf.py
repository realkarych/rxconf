import abc
import functools
import pathlib
import typing as tp

from . import attributes, config_builder, config_resolver, config_types, exceptions, hashtools


class MetaTree(metaclass=abc.ABCMeta):  # pragma: no cover
    """
    Metaclass for tree-like structures.
    """

    def __init__(
        self: "MetaTree",
        config: config_types.MetaConfigType,
    ) -> None:
        self.__structure = config

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return vars(self.__structure) == vars(other._MetaTree__structure)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @abc.abstractmethod
    def __getattr__(self, item: str) -> tp.Any:
        raise NotImplementedError()


class MetaConf(MetaTree, metaclass=abc.ABCMeta):  # pragma: no cover
    """
    Metaclass for configuration classes.
    Whole configuration class should be inherited from this metaclass.
    """

    @classmethod
    @abc.abstractmethod
    def from_file(
        cls: tp.Type["MetaConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "MetaConf":
        """
        Classmethod for creating configuration from file.
        :param config_path: path to the configuration file on the local filesystem.
        :param encoding: encoding of the configuration file. Example: "utf-8".
        """

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    async def from_file_async(
        cls: tp.Type["MetaConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "MetaConf":
        """
        Classmethod for creating configuration from file asynchronously.
        :param config_path: path to the configuration file on the local filesystem.
        :param encoding: encoding of the configuration file. Example: "utf-8".
        """

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_env(
        cls: tp.Type["MetaConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "MetaConf":
        """
        Classmethod for creating configuration from environment variables.
        :param prefix: prefix of the environment variables. Will load only variables with this prefix.
        :param remove_prefix: if True, prefix will be removed from the attribute names.
        """

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_vault(
        cls: tp.Type["MetaConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "MetaConf":
        """
        Classmethod for creating configuration from HashiCorp Vault.
        Check https://www.vaultproject.io/ for more information.
        :param token: token for accessing the Vault.
        :param ip: IP address of the Vault.
        :param path: path to the configuration in the Vault.
        """

        raise NotImplementedError()


class MetaTrigger(metaclass=abc.ABCMeta):  # pragma: no cover
    """
    Metaclass for triggers.
    Trigger is an object that calls when configuration changes.
    Check `RxConf.include_config` for more information.
    """

    @abc.abstractmethod
    def __call__(
        self: "MetaTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> None:
        """
        Method that calls when configuration changes.
        """

        raise NotImplementedError()


class SimpleTrigger(MetaTrigger):
    """
    The base trigger.
    Calls the provided function with provided arguments when configuration changes.
    Does not check which concrete attribute(s) has (have) changed.
    """

    def __init__(
        self: "SimpleTrigger",
        func: tp.Callable,
        args: tp.Optional[tp.Tuple[tp.Any, ...]] = None,
        kwargs: tp.Optional[tp.Dict[str, tp.Any]] = None,
    ) -> None:
        """
        :param func: function (or another callable object) to call when configuration changes.
        :param args: positional arguments for the function which will be called.
        :param kwargs: keyword arguments for the function which will be called.
        """

        self._func = func
        self._args: tp.Tuple[tp.Any, ...] = args if args is not None else ()
        self._kwargs: tp.Dict[str, tp.Any] = kwargs if kwargs is not None else {}

    def __call__(
        self: "SimpleTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> None:
        """
        Calls the provided function with provided arguments.
        Does not check which concrete attribute(s) has (have) changed.
        """

        self._func(*self._args, **self._kwargs)

    def __repr__(self) -> str:
        """
        Returns the string representation of the trigger.
        """

        return f"{self.__class__.__name__}(func={self._func!r}, args={self._args!r}, kwargs={self._kwargs!r})"


class OnChangeTrigger(MetaTrigger):

    def __init__(
        self: "OnChangeTrigger",
        trigger: MetaTrigger,
        all_attributes: tp.Optional[tp.Tuple[str, ...]] = None,
        any_attributes: tp.Optional[tp.Tuple[str, ...]] = None,
    ) -> None:
        """
        Provide trigger, either all_attributes or any_attributes. If all_attributes is provided,
        trigger will be called only if all of them are changed.
        If any_attributes is provided, trigger will be called if any of them is changed.
        WARNING: Exactly one of the all_attributes and any_attributes parameters must be provided.
        Otherwise, an exception will be raised.

        :param trigger: trigger that will be called when configuration changes.
        :param all_attributes: tuple of attributes that must be changed to call the trigger.
        Only if all of them are changed, the trigger will be called.
        Example: all_attributes=("a", "b.c.d", "e.f") - trigger will be called only if
        all attributes (a, d and f) are changed.
        :param any_attributes: tuple of attributes that can be changed to call the trigger.
        If any of them is changed, the trigger will be called.
        Example: any_attributes=("a", "b.c.d", "e.f") - trigger will be called if
        any (>= 1) of attributes (a, d or f) are changed.
        """

        if (not all_attributes and not any_attributes) or (all_attributes and any_attributes):
            raise exceptions.RxConfError("You must provide either `all_attributes` or `any_attributes`.")
        self._trigger = trigger
        self._all_of_attributes: tp.Tuple[str, ...] = all_attributes if all_attributes is not None else ()
        self._any_of_attributes: tp.Tuple[str, ...] = any_attributes if any_attributes is not None else ()

    @property
    def all_of(self) -> tp.Tuple[str, ...]:
        """
        Returns a normalized tuple of attributes that must be changed to call the trigger.
        """

        return self._all_of_attributes

    @property
    def any_of(self) -> tp.Tuple[str, ...]:
        """
        Returns a normalized tuple of attributes that can be changed to call the trigger.
        """

        return self._any_of_attributes

    def __call__(
        self: "OnChangeTrigger",
        old_conf: MetaConf,
        actual_conf: MetaConf,
    ) -> None:
        """
        Calls the trigger if chosen condition (all_attributes or any_attributes) is met.
        """

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
        """
        Checks if any of the attributes from `any_attributes` is changed.
        """

        if old_conf == actual_conf:
            return False
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
        """
        Checks if all the attributes from `all_attributes` are changed.
        """

        if old_conf == actual_conf:
            return False
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
        """
        Checks if the attribute is changed.
        Works recursively for nested attributes.
        Compare AttributeType objects.
        """

        def get_nested_attr(conf: MetaConf, path: str) -> tp.Union[attributes.AttributeType, MetaConf]:
            """
            Returns the target attribute from the configuration.
            :param conf: configuration object.
            :param path: path to the attribute in the configuration. Example: "a.b.c".
            """

            value: tp.Union[attributes.AttributeType, MetaConf] = conf  # type: ignore
            for attr in path.lower().split("."):
                value = getattr(value, attr)
            return value

        try:
            old_value = get_nested_attr(old_conf, attribute_path)
            new_value = get_nested_attr(actual_conf, attribute_path)
            return all(
                (
                    isinstance(old_value, attributes.AttributeType),
                    isinstance(new_value, attributes.AttributeType),
                    old_value != new_value,
                )
            )
        except AttributeError as e:
            raise exceptions.InvalidAttributeError(f"Attribute '{attribute_path}' not found in configuration.") from e


class Conf(MetaConf):
    """
    Base configuration class.
    Stores configuration in the tree-like structure.
    If you want to use reactive configuration, use RxConf instead, it will inject the configuration into the function.
    """

    def __init__(self, config: config_types.MetaConfigType) -> None:
        """
        Do not call this method directly. Use classmethods instead.
        For example: `Conf.from_file(...)`, `Conf.from_env(...)`, `Conf.from_vault(...)` etc.
        :param config: configuration structure.
        """

        super().__init__(config)

    @classmethod
    def from_file(
        cls: tp.Type["Conf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "Conf":
        """
        Classmethod for creating frozen configuration from file.
        :param config_path: path to the configuration file on the local filesystem.
        :param encoding: encoding of the configuration file. Example: "utf-8" (default), "cp1250", "iso-8859-2" etc.
        """

        return cls(
            config=config_builder.FileConfigTypeBuilder(
                config_resolver=file_config_resolver,
            ).build(
                path=config_path,
                encoding=encoding,
            )
        )

    @classmethod
    async def from_file_async(
        cls: tp.Type["Conf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "Conf":
        """
        Classmethod for creating frozen configuration from file asynchronously.
        :param config_path: path to the configuration file on the local filesystem.
        :param encoding: encoding of the configuration file. Example: "utf-8" (default), "cp1250", "iso-8859-2" etc.
        """

        return cls(
            config=await config_builder.FileConfigTypeBuilder(
                config_resolver=file_config_resolver,
            ).build_async(
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
        """
        Classmethod for creating frozen configuration from environment variables.
        :param prefix: prefix of the environment variables. It will load only variables with this prefix.
        :param remove_prefix: if True, prefix will be removed from the attribute names.
        """

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
        """
        Classmethod for creating frozen configuration from HashiCorp Vault.
        Check https://www.vaultproject.io/ for more information.
        :param token: token for accessing the Vault server.
        :param ip: IP address of the Vault server.
        :param path: path to the configuration in the Vault server.
        """

        return cls(config=config_types.VaultConfig.load_from_vault(token=token, ip=ip, path=path))

    def __eq__(self, other: object) -> bool:
        """
        Compares two configurations. other must be an instance of Conf.
        """

        if not isinstance(other, Conf):
            raise TypeError("Conf is comparable only to Conf")
        return self._MetaTree__structure == other._MetaTree__structure

    def __ne__(self, other: object) -> bool:
        """
        Inverts the result of __eq__ method.
        """

        return not self.__eq__(other)

    def __getattr__(self, item: str) -> tp.Any:
        """
        Returns the dummy (root) attribute of the configuration. Entry point to the configuration.
        """

        return getattr(self._MetaTree__structure, f"{hashtools.ATTR_SAULT}{item.lower()}")

    def __repr__(self) -> str:
        """
        Returns the string representation of the configuration structure.
        """

        return repr(self._MetaTree__structure)


class MetaConfFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_conf(
        self: "MetaConfFactory",
    ) -> MetaConf:
        """
        Creates configuration object.
        """

        raise NotImplementedError()


class FileConfFactory(MetaConfFactory):
    """
    Configuration factory for file-based configurations.
    Wrapper to create configuration from file.
    """

    def __init__(
        self: "FileConfFactory",
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> None:
        """
        :param config_path: path to the configuration file on the local filesystem.
        :param encoding: encoding of the configuration file. Example: "utf-8".
        :param file_config_resolver: file configuration resolver.
        """

        self._config_path = config_path
        self._encoding = encoding
        self._file_config_resolver = file_config_resolver

    def create_conf(
        self: "FileConfFactory",
    ) -> Conf:
        """
        Creates actual configuration object from file.
        """

        return Conf.from_file(
            config_path=self._config_path,
            encoding=self._encoding,
            file_config_resolver=self._file_config_resolver,
        )


class EnvConfFactory(MetaConfFactory):
    """
    Configuration factory for environment-based configurations.
    Wrapper to create configuration from environment variables.
    """

    def __init__(
        self: "EnvConfFactory",
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> None:
        """
        :param prefix: prefix of the environment variables. Will load only variables with this prefix.
        :param remove_prefix: if True, prefix will be removed from the attribute names.
        """

        self._prefix = prefix
        self._remove_prefix = remove_prefix

    def create_conf(
        self: "EnvConfFactory",
    ) -> Conf:
        """
        Creates actual configuration object from environment variables.
        """

        return Conf.from_env(
            prefix=self._prefix,
            remove_prefix=self._remove_prefix,
        )


class VaultConfFactory(MetaConfFactory):
    """
    Configuration factory for Vault-based configurations.
    More information: https://www.vaultproject.io/.
    Wrapper to create configuration from HashiCorp Vault.
    """

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


class MetaRxConf(metaclass=abc.ABCMeta):
    """
    Interface for reactive configurations.
    """

    @classmethod
    @abc.abstractmethod
    def from_file(
        cls: tp.Type["MetaRxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str,
        file_config_resolver: config_resolver.FileConfigResolver,
    ) -> "MetaRxConf":
        """
        Classmethod for creating reactive configuration from file.
        """

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    async def from_file_async(
        cls: tp.Type["MetaRxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "MetaRxConf":
        """
        Classmethod for creating reactive configuration from file asynchronously.
        """

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_env(
        cls: tp.Type["MetaRxConf"],
        prefix: tp.Optional[str] = None,
        remove_prefix: tp.Optional[bool] = False,
    ) -> "MetaRxConf":
        """
        Classmethod for creating reactive configuration from environment variables.
        """

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_vault(
        cls: tp.Type["MetaRxConf"],
        token: str,
        ip: str,
        path: tp.Union[str, pathlib.PurePath],
    ) -> "MetaRxConf":
        """
        Classmethod for creating reactive configuration from HashiCorp Vault.
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def include_config(
        self: "MetaRxConf",
        triggers: tp.Optional[tp.Iterable[MetaTrigger]] = None,
    ) -> tp.Callable:
        """
        Decorator for injecting actual configuration into the function.
        param triggers: triggers that will be called when configuration changes.
        """

        raise NotImplementedError()


class RxConf(MetaRxConf):
    """
    Entry point for reactive configurations.
    It's not recommended to use this class directly.
    Use classmethods `RxConf.from_file`, `RxConf.from_env` or `RxConf.from_vault` instead.
    """

    _current_conf: tp.Optional[MetaConf] = None

    def __init__(self, factory: MetaConfFactory, di_arg_name: str = "conf") -> None:
        """
        :param factory: configuration factory.
        :param di_arg_name: name of the argument that will be injected into the function.
        Example:
        ```python
        observer = RxConf.from_file("config.json")
        @observer.include_config(...)
        def my_function(conf: MetaConf):  # <- conf == di_arg_name.
            pass
        ```
        """

        self._factory = factory
        self._di_arg_name = di_arg_name

    @classmethod
    def from_file(
        cls: tp.Type["RxConf"],
        config_path: tp.Union[str, pathlib.PurePath],
        encoding: str = "utf-8",
        file_config_resolver: config_resolver.FileConfigResolver = config_resolver.DefaultFileConfigResolver,
    ) -> "RxConf":
        """
        Classmethod for creating reactive configuration from file.
        :param config_path: path to the configuration file on the local filesystem.
        :param encoding: encoding of the configuration file. Examples: `utf-8`, `cp1250`, `iso-8859-2` etc.
        :param file_config_resolver: file configuration resolver.
        If you want to support custom file formats / extensions, you should implement your own class
        inherited from MetaConfigResolver and provide custom resolver here.
        """

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
        """
        Classmethod for creating reactive configuration from environment variables.
        WARNING: if you want to use dotenv files, use `from_file` method instead.
        :param prefix: prefix of the environment variables. It will load only variables with this prefix.
        """

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
        """
        Classmethod for creating reactive configuration from HashiCorp Vault.
        Check https://www.vaultproject.io/ for more information.
        :param token: token for accessing the Vault.
        :param ip: IP address of the Vault.
        :param path: path to the configuration in the Vault.
        """

        return cls(
            factory=VaultConfFactory(
                token=token,
                ip=ip,
                path=path,
            )
        )

    @property
    def current_conf(self) -> MetaConf:
        """
        Returns the current configuration. Current != actual.
        Current is the configuration that was used in the last function call.
        According to OOP best-practices, it's not recommended to use this property directly.
        """

        if self._current_conf is None:
            self._current_conf = self._factory.create_conf()
        return self._current_conf

    @current_conf.setter
    def current_conf(self, new_conf: MetaConf) -> None:
        """
        Sets the current configuration.
        """

        self._current_conf = new_conf

    def include_config(
        self: "RxConf",
        triggers: tp.Optional[tp.Iterable[MetaTrigger]] = None,
    ) -> tp.Callable:
        """
        Decorator for injecting actual configuration into the function.
        :param triggers: triggers that will be called when configuration changes.
        """

        def decorator(func: tp.Callable) -> tp.Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                """
                Wrapper for injecting actual configuration into the function.
                Execute triggers if the configuration has changed.
                If configuration is the same, do not execute triggers.
                WARNING: this decorator overrides kwargs, so do not use `conf` (or you provided name)
                as a keyword argument in the function for other purposes.
                """

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
