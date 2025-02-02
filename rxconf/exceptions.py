import functools
import sys
import typing as tp


if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


T = tp.TypeVar("T")
P = ParamSpec("P")
R = tp.TypeVar("R")


class RxConfError(RuntimeError):
    """
    Raised when an error occurs in the rxconf package.
    You can catch this exception to handle all errors in the package.
    Check the inherited classes for more concrete exceptions.
    """

    def __init__(self, message: str):
        super().__init__(message)


class BrokenConfigSchemaError(RxConfError):
    """
    Raised when the schema of the configuration file is broken.
    For example: missing required attributes, invalid types, wrong indentation, etc.
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidAttributeError(BrokenConfigSchemaError):
    """
    Raised when an attribute in the configuration file is invalid.
    For example: you try selecting not existing attribute.
    """

    def __init__(self, message: str):
        super().__init__(message)


class ConfigNotFoundError(RxConfError):
    """
    Raised when the config not found.
    For example: the config file is not found in the specified path on the filesystem,
    provided link / ip / port / password in the web-conf is incorrect, etc.
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidExtensionError(RxConfError):
    """
    Raised when the extension of the configuration file is invalid.
    It happens when you try to load the configuration file with an unsupported extension.
    """

    def __init__(self, message: str):
        super().__init__(message)


@tp.overload
def handle_unknown_exception(obj: tp.Type[T]) -> tp.Type[T]: ...


@tp.overload
def handle_unknown_exception(obj: tp.Callable[P, R]) -> tp.Callable[P, R]: ...


def handle_unknown_exception(  # noqa: C901
    obj: tp.Union[tp.Callable[..., tp.Any], type],
) -> tp.Union[tp.Callable[..., tp.Any], type]:
    """
    A decorator that catches all exceptions in the decorated function and raises RxConfError instead.
    Implemented to guarantee that all exceptions in the rxconf package are overridden by RxConfError.

    When applied to a class, all callable attributes (methods, staticmethods and classmethods) will be wrapped.
    """
    if isinstance(obj, type):
        for attr_name, attr in obj.__dict__.items():
            if attr_name != "__call__" and attr_name.startswith("__") and attr_name.endswith("__"):
                continue

            if isinstance(attr, staticmethod):
                decorated_func = handle_unknown_exception(attr.__func__)
                setattr(obj, attr_name, staticmethod(decorated_func))
            elif isinstance(attr, classmethod):
                decorated_func = handle_unknown_exception(attr.__func__)
                setattr(obj, attr_name, classmethod(decorated_func))
            elif isinstance(attr, property):
                new_getter = handle_unknown_exception(attr.fget) if attr.fget is not None else None
                new_setter = handle_unknown_exception(attr.fset) if attr.fset is not None else None
                new_deleter = handle_unknown_exception(attr.fdel) if attr.fdel is not None else None
                setattr(obj, attr_name, property(new_getter, new_setter, new_deleter))
            elif callable(attr):
                decorated = handle_unknown_exception(attr)
                setattr(obj, attr_name, decorated)
        return obj

    @functools.wraps(obj)
    def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        try:
            return obj(*args, **kwargs)
        except RxConfError:
            raise
        except Exception as exc:
            raise RxConfError(f"An error occurred in {obj.__name__}: {str(exc)}") from exc

    return wrapper
