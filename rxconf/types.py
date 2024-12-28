import sys
import typing as tp
from datetime import date, datetime


if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

YAML_ATTRIBUTE_TYPE: TypeAlias = tp.Union[
    tp.Union[bool, int, str, float, None],
    tp.List[tp.Union[bool, int, str, float, None]],
    tp.Set[tp.Union[bool, int, str, float, None]],
    tp.Union[date, datetime],
]

JSON_ATTRIBUTE_TYPE: TypeAlias = tp.Union[
    tp.Union[bool, int, str, float, None],
    tp.List[tp.Union[bool, int, str, float, None]],
]

TOML_ATTRIBUTE_TYPE: TypeAlias = tp.Union[
    tp.Union[bool, int, str, float],
    tp.List[tp.Union[bool, int, str, float]],
    tp.Union[date, datetime],
]

INI_ATTRIBUTE_TYPE: TypeAlias = tp.Union[
    bool,
    int,
    str,
    float,
    None,
]

ENV_ATTRIBUTE_TYPE: TypeAlias = tp.Union[
    bool,
    int,
    str,
    float,
    None,
]


def map_primitive(value: str) -> tp.Union[int, float, bool, None, str]:
    lower_value = value.lower()
    if lower_value == "none" or lower_value == "null":
        return None
    if lower_value == "true":
        return True
    if lower_value == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
