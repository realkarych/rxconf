import abc

from rxconf import rxconf


class MetaObserver(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_actual_config(self) -> rxconf.RxConf:
        pass


class MetaAsyncObserver(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def get_actual_config(self) -> rxconf.RxConf:
        pass


class Observer(MetaObserver):

    def __init__(self, config: rxconf.RxConf):
        self._config = config

    def get_actual_config(self) -> rxconf.RxConf:
        # TODO: Fix stub
        return self._config


class AsyncObserver(MetaAsyncObserver):

    def __init__(self, config: rxconf.RxConf):
        self._config = config

    async def get_actual_config(self) -> rxconf.RxConf:
        # TODO: Fix stub
        return self._config
