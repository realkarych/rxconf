import datetime
import typing as tp

PRIMITIVE_TYPE = tp.Union[bool, int, str, float, type(None)]
DATES_TYPE = tp.Union[datetime.date, datetime.datetime]
PRIMITIVE_LIST_TYPE = tp.List[PRIMITIVE_TYPE]
PRIMITIVE_SET_TYPE = tp.Set[PRIMITIVE_TYPE]
PRIMITIVE_SEQUENCE_TYPE = tp.Union[PRIMITIVE_LIST_TYPE, PRIMITIVE_SET_TYPE]
