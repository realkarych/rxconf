import datetime
import typing as tp
from dataclasses import dataclass

from typing_extensions import runtime_checkable

PRIMITIVE_TYPE = tp.Union[bool, int, str, float, None]
DATES_TYPE = tp.Union[datetime.date, datetime.datetime]

PRIMITIVE_LIST_TYPE = tp.List[PRIMITIVE_TYPE]
PRIMITIVE_SET_TYPE = tp.Set[PRIMITIVE_TYPE]
PRIMITIVE_SEQUENCE_TYPE = tp.Union[PRIMITIVE_LIST_TYPE, PRIMITIVE_SET_TYPE]


@runtime_checkable
class AttributeType(tp.Protocol):
    value: tp.Any


@runtime_checkable
class KVAttributeType(AttributeType, tp.Protocol):
    key: str
    value: tp.Any


@dataclass(frozen=True)
class YamlAttribute(KVAttributeType):
    __slots__ = ("key", "value")

    key: str
    value: tp.Union[
        PRIMITIVE_TYPE,
        PRIMITIVE_SEQUENCE_TYPE,
        DATES_TYPE,
        "YamlAttribute",
        tp.List["YamlAttribute"],
        tp.Set["YamlAttribute"],
    ]
