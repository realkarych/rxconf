import collections
import typing as tp
from abc import ABCMeta, abstractmethod

import yaml

from rxconf import attributes as attrs


class ConfigType(metaclass=ABCMeta):
    pass


class FileConfigType(ConfigType):

    allowed_extensions: tp.FrozenSet[str]

    @classmethod
    @abstractmethod
    def load_from_path(cls, path: str) -> "FileConfigType":
        pass


class YamlConfig(FileConfigType):

    allowed_extensions = frozenset({"yaml", "yml"})
    _attributes: tp.Final[tp.Dict[str, attrs.YamlAttribute]]

    def __init__(self, attributes: tp.Sequence[attrs.YamlAttribute]) -> None:
        self._attributes = tp.OrderedDict({attr.key: attr for attr in attributes})

    @classmethod
    def load_from_path(cls, path: str) -> "YamlConfig":
        with open(path) as file:
            yaml_data = yaml.safe_load(file)

        def parse_yaml(data, parent_key=''):
            queue = collections.deque([(parent_key, data)])
            attributes = []

            while queue:
                current_key, current_value = queue.popleft()

                if isinstance(current_value, dict):
                    nested_attributes = []
                    for key, value in current_value.items():
                        queue.append((key, value))
                        nested_attributes.append(attrs.YamlAttribute(key=key, value=value))
                    attributes.append(attrs.YamlAttribute(key=current_key, value=nested_attributes))
                else:
                    attributes.append(attrs.YamlAttribute(key=current_key, value=current_value))

            return attributes

        first_level_attributes = parse_yaml(yaml_data)
        return cls(first_level_attributes)
