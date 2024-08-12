import datetime
import typing as tp
from abc import ABCMeta, abstractmethod

from rxconf import attributes as attrs
from rxconf import exceptions


class DataProcessor(metaclass=ABCMeta):

    def __init__(self, data: tp.Any) -> None:
        self._data = data

    @abstractmethod
    def start_processing(self) -> attrs.AttributeType:
        pass


class YamlDataProcessor(DataProcessor):

    def __init__(self, data: tp.Any) -> None:
        self._data = data

    def start_processing(self) -> attrs.YamlAttribute:
        return self._process_data(self._data)

    def _process_data(self, data: tp.Any) -> attrs.YamlAttribute:
        if isinstance(data, dict):
            return attrs.YamlAttribute(
                value={k: self._process_data(v) for k, v in data.items()}
            )
        elif isinstance(data, list):
            return attrs.YamlAttribute(
                value=[
                    self._process_data(item) if not isinstance(item, dict) else attrs.YamlAttribute(
                        value={k: self._process_data(v) for k, v in item.items()}
                    ) for item in data
                ]
            )
        elif isinstance(data, set):
            return attrs.YamlAttribute(
                value={self._process_data(item) for item in data}
            )
        elif isinstance(data, (str, int, float, bool, type(None))):
            return attrs.YamlAttribute(value=data)
        elif isinstance(data, (datetime.date, datetime.datetime)):
            return attrs.YamlAttribute(value=data)
        else:
            raise exceptions.BrokenConfigSchemaError(f"Unsupported data type: {type(data)}")
