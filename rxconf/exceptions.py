import functools
import typing as tp


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
    For exaple: missing required attributes, invalid types, wrong indentation, etc.
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


def handle_unknown_exception(func: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
    """
    A decorator that catches all exceptions in the decorated function and raises RxConfError instead.
    Implemented to guarantee that all exceptions in the rxconf package are overridden by RxConfError.
    """

    @functools.wraps(func)
    def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        try:
            return func(*args, **kwargs)
        except RxConfError:
            raise
        except Exception as exc:
            raise RxConfError(f"An error occurred in {func.__name__}: {str(exc)}") from exc

    return wrapper
