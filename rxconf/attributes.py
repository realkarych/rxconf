import typing as tp
from abc import ABCMeta, abstractmethod

from rxconf import exceptions, types


def _patch_other_value(func: tp.Callable[..., tp.Any]) -> tp.Callable[..., tp.Any]:
    def wrapper(self: "AttributeType", other: tp.Any) -> tp.Any:
        if isinstance(other, AttributeType):
            other = object.__getattribute__(other, "_AttributeType__value")
        return func(self, other)

    return wrapper


class AttributeType(metaclass=ABCMeta):

    def __init__(self, value: tp.Any) -> None:  # pragma: no cover
        self.__value = value

    @abstractmethod
    def __getattr__(self, item: str) -> tp.Any:  # pragma: no cover
        raise NotImplementedError()

    @exceptions.handle_unknown_exception
    def __int__(self) -> int:
        return int(self.__value)

    @exceptions.handle_unknown_exception
    def __float__(self) -> float:
        return float(self.__value)

    @exceptions.handle_unknown_exception
    def __str__(self) -> str:
        return str(self.__value)

    @exceptions.handle_unknown_exception
    def __bool__(self) -> bool:
        return bool(self.__value)

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __add__(self, other: tp.Any) -> tp.Any:
        return self.__value + other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __mul__(self, other: tp.Any) -> tp.Any:
        return self.__value * other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __sub__(self, other: tp.Any) -> tp.Any:
        return self.__value - other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __truediv__(self, other: tp.Any) -> tp.Any:
        return self.__value / other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __floordiv__(self, other: tp.Any) -> tp.Any:
        return self.__value // other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __mod__(self, other: tp.Any) -> tp.Any:
        return self.__value % other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __pow__(self, other: tp.Any) -> tp.Any:
        return self.__value**other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __lshift__(self, other: tp.Any) -> tp.Any:
        return self.__value << other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __rshift__(self, other: tp.Any) -> tp.Any:
        return self.__value >> other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __and__(self, other: tp.Any) -> tp.Any:
        return self.__value & other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __xor__(self, other: tp.Any) -> tp.Any:
        return self.__value ^ other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __or__(self, other: tp.Any) -> tp.Any:
        return self.__value | other

    @exceptions.handle_unknown_exception
    def __neg__(self) -> tp.Any:
        return -self.__value

    @exceptions.handle_unknown_exception
    def __pos__(self) -> tp.Any:
        return +self.__value

    @exceptions.handle_unknown_exception
    def __abs__(self) -> tp.Any:
        return abs(self.__value)

    @exceptions.handle_unknown_exception
    def __invert__(self) -> tp.Any:
        return ~self.__value

    @exceptions.handle_unknown_exception
    def __round__(self, n: int = 0) -> tp.Any:
        return round(self.__value, n)

    @exceptions.handle_unknown_exception
    def __hash__(self) -> int:
        return hash(self.__value)

    @exceptions.handle_unknown_exception
    def __len__(self) -> int:
        return len(self.__value)

    @exceptions.handle_unknown_exception
    def __iter__(self) -> tp.Iterator[tp.Any]:
        return iter(self.__value)

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __contains__(self, item: tp.Any) -> bool:
        return item in self.__value

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __getitem__(self, item: tp.Any) -> tp.Any:
        return self.__value[item]

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __eq__(self, other: tp.Any) -> bool:
        return self.__value == other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __ne__(self, other: tp.Any) -> bool:
        return not self.__eq__(other)

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __lt__(self, other: tp.Any) -> bool:
        return self.__value < other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __le__(self, other: tp.Any) -> bool:
        return self.__value <= other

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __gt__(self, other: tp.Any) -> bool:
        return other < self.__value

    @exceptions.handle_unknown_exception
    @_patch_other_value
    def __ge__(self, other: tp.Any) -> bool:
        return other <= self.__value

    @exceptions.handle_unknown_exception
    def __repr__(self) -> str:
        return f"AttributeType({self.__value})"


class MockAttribute(AttributeType):  # pragma: no cover

    def __init__(self, value: tp.Any = None) -> None:
        super().__init__(value)

    def __getattr__(self, item: str) -> None:
        pass


class YamlAttribute(AttributeType):

    def __init__(
        self: "YamlAttribute",
        value: tp.Union[
            types.YAML_ATTRIBUTE_TYPE,
            "YamlAttribute",
            tp.List["YamlAttribute"],
            tp.Set["YamlAttribute"],
            tp.Dict[str, "YamlAttribute"],
        ],
    ) -> None:
        super().__init__(value)

    @exceptions.handle_unknown_exception
    def __getattr__(
        self: "YamlAttribute",
        item: str,
    ) -> tp.Union[
        types.YAML_ATTRIBUTE_TYPE,
        "YamlAttribute",
        tp.List["YamlAttribute"],
        tp.Set["YamlAttribute"],
        tp.Dict[str, "YamlAttribute"],
    ]:
        value = object.__getattribute__(self, "_AttributeType__value")
        if isinstance(value, dict):
            try:
                return value[item.lower()]
            except KeyError as exc:
                raise KeyError(f"Key `{item}` doesn't exist...") from exc

        raise KeyError(f"Key `{item}` doesn't exist...")


class JsonAttribute(AttributeType):

    def __init__(
        self: "JsonAttribute",
        value: tp.Union[
            types.JSON_ATTRIBUTE_TYPE,
            "JsonAttribute",
            tp.List["JsonAttribute"],
            tp.Dict[str, "JsonAttribute"],
        ],
    ) -> None:
        super().__init__(value)

    @exceptions.handle_unknown_exception
    def __getattr__(
        self: "JsonAttribute",
        item: str,
    ) -> tp.Union[
        types.JSON_ATTRIBUTE_TYPE,
        "JsonAttribute",
        tp.List["JsonAttribute"],
        tp.Dict[str, "JsonAttribute"],
    ]:
        value = object.__getattribute__(self, "_AttributeType__value")
        if isinstance(value, dict):
            try:
                return value[item.lower()]
            except KeyError as exc:
                raise KeyError(f"Key `{item}` doesn't exist...") from exc

        raise KeyError(f"Key `{item}` doesn't exist...")


class TomlAttribute(AttributeType):

    def __init__(
        self: "TomlAttribute",
        value: tp.Union[
            types.TOML_ATTRIBUTE_TYPE,
            "TomlAttribute",
            tp.List["TomlAttribute"],
            tp.Dict[str, "TomlAttribute"],
        ],
    ) -> None:
        super().__init__(value)

    @exceptions.handle_unknown_exception
    def __getattr__(
        self: "TomlAttribute",
        item: str,
    ) -> tp.Union[
        types.TOML_ATTRIBUTE_TYPE,
        "TomlAttribute",
        tp.List["TomlAttribute"],
        tp.Dict[str, "TomlAttribute"],
    ]:
        value = object.__getattribute__(self, "_AttributeType__value")
        if isinstance(value, dict):
            try:
                return value[item.lower()]
            except KeyError as exc:
                raise KeyError(f"Key `{item}` doesn't exist...") from exc

        raise KeyError(f"Key `{item}` doesn't exist...")


class EnvAttribute(AttributeType):

    def __init__(
        self: "EnvAttribute",
        value: tp.Union[
            types.ENV_ATTRIBUTE_TYPE,
            "EnvAttribute",
            tp.Dict[str, "EnvAttribute"],
        ],
    ) -> None:
        super().__init__(value)

    @exceptions.handle_unknown_exception
    def __getattr__(
        self: "EnvAttribute",
        item: str,
    ) -> tp.Union[
        types.ENV_ATTRIBUTE_TYPE,
        "EnvAttribute",
        tp.Dict[str, "EnvAttribute"],
    ]:
        value = object.__getattribute__(self, "_AttributeType__value")
        if isinstance(value, dict):
            try:
                return value[item.lower()]
            except KeyError as exc:
                raise KeyError(f"Key `{item}` doesn't exist...") from exc

        raise KeyError(f"Key `{item}` doesn't exist...")


class IniAttribute(AttributeType):

    def __init__(self: "IniAttribute", value: tp.Union[types.INI_ATTRIBUTE_TYPE, tp.Dict[str, "IniAttribute"]]) -> None:
        super().__init__(value)

    @exceptions.handle_unknown_exception
    def __getattr__(
        self: "IniAttribute",
        item: str,
    ) -> tp.Union[types.INI_ATTRIBUTE_TYPE, tp.Dict[str, "IniAttribute"], "IniAttribute"]:
        value = object.__getattribute__(self, "_AttributeType__value")
        if isinstance(value, dict):
            try:
                return value[item.lower()]
            except KeyError as exc:
                raise KeyError(f"Key `{item}` doesn't exist...") from exc

        raise KeyError(f"Key `{item}` doesn't exist...")
