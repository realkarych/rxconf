import functools
import typing as tp


class RxConfError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


class BrokenConfigSchemaError(RxConfError):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidAttributeError(BrokenConfigSchemaError):
    def __init__(self, message: str):
        super().__init__(message)


class ConfigNotFoundError(RxConfError):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidExtensionError(RxConfError):
    def __init__(self, message: str):
        super().__init__(message)


def handle_unknown_exception(func: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
    @functools.wraps(func)
    def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        try:
            return func(*args, **kwargs)
        except RxConfError:
            raise
        except Exception as exc:
            raise RxConfError(f"An error occurred in {func.__name__}: {str(exc)}") from exc
    return wrapper
