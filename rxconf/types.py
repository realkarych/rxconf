import sys
import typing as tp
from datetime import date, datetime

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

PRIMITIVE_TYPE: TypeAlias = tp.Union[bool, int, str, float, None]
DATES_TYPE: TypeAlias = tp.Union[date, datetime]
PRIMITIVE_LIST_TYPE: TypeAlias = tp.List[PRIMITIVE_TYPE]
PRIMITIVE_SET_TYPE: TypeAlias = tp.Set[PRIMITIVE_TYPE]
PRIMITIVE_SEQUENCE_TYPE: TypeAlias = tp.Union[PRIMITIVE_LIST_TYPE, PRIMITIVE_SET_TYPE]
