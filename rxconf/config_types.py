import typing as tp
from abc import ABCMeta, abstractmethod
from rxconf import attributes as attrs


class ConfigType(metaclass=ABCMeta):
    pass


class FileConfigType(ConfigType):

    allowed_extensions: tp.FrozenSet[str] = frozenset()

    @abstractmethod
    @classmethod
    def load_from_path(cls, path: str) -> "FileConfigType":
        pass


class YamlConfig(FileConfigType):

    allowed_extensions = frozenset({"yaml", "yml"})
    _attributes: tp.Final[tp.Dict[str, attrs.YamlAttribute]]

    def __init__(self, attributes: tp.Sequence[attrs.YamlAttribute]) -> None:
        self._attributes = {attr.key: attr for attr in attributes}

    @classmethod
    def load_from_path(cls, path: str) -> "YamlConfig":
        raise NotImplementedError()
