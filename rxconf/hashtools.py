from rxconf import AttributeType
from hashlib import sha256
import typing as tp


def _type_hashed(value: tp.Any) -> str:
    return f"{type(value).__name__}{value}"


def _hash_to_int(value: str) -> int:
    """Hash the value and return it as an integer"""
    return int(sha256(value.encode('utf-8')).hexdigest(), 16)


hashed_structures: tp.Final[dict[str, int]] = {
    "list": _hash_to_int("[]"),
    "set": _hash_to_int("()"),
}


def compute_conf_hash(attribute: AttributeType, hash_sum: int = 0) -> int:
    if isinstance(attribute._value, dict):
        for key in attribute._value:
            """ hash += hash(sum_of_the_hashes_inside_value) + hash(key) """
            val_sum = compute_conf_hash(attribute._value[key], 0)  # hash inside value
            val_sum = _hash_to_int(_type_hashed(val_sum))  # hash(hash)
            key_sum = _hash_to_int(_type_hashed(key))  # hash(key)
            total_sum = _hash_to_int(_type_hashed(key_sum + val_sum))
            hash_sum += total_sum

    elif isinstance(attribute._value, set):
        set_sum = 0
        for elem in attribute._value:
            set_sum += _hash_to_int(_type_hashed(elem._value))
        set_sum += hashed_structures["set"]
        hash_sum += _hash_to_int(_type_hashed(set_sum))

    elif isinstance(attribute._value, list):
        list_sum = 0
        for elem in attribute._value:
            list_sum += compute_conf_hash(elem, 0)
            list_sum = _hash_to_int(_type_hashed(list_sum))  # to keep order
        list_sum += hashed_structures["list"]
        hash_sum += _hash_to_int(_type_hashed(list_sum))

    else:
        hash_sum += _hash_to_int(_type_hashed(attribute._value))

    return hash_sum
