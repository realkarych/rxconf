import typing as tp
from hashlib import sha256

from rxconf import AttributeType


def _hash_with_type(value: tp.Any) -> str:
    return f"{type(value).__name__}{value}"


def _hash_to_int(value: str) -> int:
    """Hash the value and return it as an integer"""
    return int(sha256(value.encode("utf-8")).hexdigest(), 16)


HASHED_STRUCTURES: tp.Final[dict[str, int]] = {
    "list": _hash_to_int("[]"),
    "set": _hash_to_int("()"),
}


def compute_conf_hash(attribute: AttributeType, hash_sum: int = 0) -> int:
    value = attribute.__getattribute__("_AttributeType__value")
    if isinstance(value, dict):
        for key in value:
            val_sum = compute_conf_hash(value[key], 0)
            val_sum = _hash_to_int(_hash_with_type(val_sum))
            key_sum = _hash_to_int(_hash_with_type(key))
            total_sum = _hash_to_int(_hash_with_type(key_sum + val_sum))
            hash_sum += total_sum

    elif isinstance(value, set):
        set_sum = 0
        for elem in value:
            set_sum += _hash_to_int(_hash_with_type(elem.__getattribute__("_AttributeType__value")))
        set_sum += HASHED_STRUCTURES["set"]
        hash_sum += _hash_to_int(_hash_with_type(set_sum))

    elif isinstance(value, list):
        list_sum = 0
        for elem in value:
            list_sum += compute_conf_hash(elem, 0)
            list_sum = _hash_to_int(_hash_with_type(list_sum))
        list_sum += HASHED_STRUCTURES["list"]
        hash_sum += _hash_to_int(_hash_with_type(list_sum))

    else:
        hash_sum += _hash_to_int(_hash_with_type(value))

    return hash_sum
