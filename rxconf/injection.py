import abc
import functools
import typing as tp

from rxconf import observer


class MetaRxConfDI(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def inject_conf(self) -> tp.Callable:
        pass


class MetaAsyncRxConfDI(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def inject_conf(self) -> tp.Callable:
        pass


class InjectableRxConf(MetaRxConfDI):

    def __init__(self, conf: observer.MetaObserver) -> None:
        self._conf = conf

    def inject_conf(self) -> tp.Callable[[tp.Callable[..., tp.Any]], tp.Callable[..., tp.Any]]:
        def decorator(function: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
            @functools.wraps(function)
            def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
                return function(*args, **kwargs, conf=self._conf.get_actual_config())

            return wrapper

        return decorator


class InjectableAsyncRxConf(MetaAsyncRxConfDI):
    def __init__(self, conf: observer.MetaAsyncObserver) -> None:
        self._conf = conf

    async def inject_conf(
        self,
    ) -> tp.Callable[
        [tp.Callable[..., tp.Awaitable[tp.Any]]],
        tp.Callable[..., tp.Awaitable[tp.Any]],
    ]:
        def decorator(function: tp.Callable[..., tp.Awaitable[tp.Any]]) -> tp.Callable[..., tp.Awaitable[tp.Any]]:
            @functools.wraps(function)
            async def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
                return await function(*args, **kwargs, conf=await self._conf.get_actual_config())

            return wrapper

        return decorator
