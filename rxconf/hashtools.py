from rxconf import AttributeType
from hashlib import sha256
import typing as tp


def _type_hashed(value: tp.Any) -> str:
    return f"{type(value).__name__}{value}"


def _hash_to_int(value: str) -> int:
    """Hash the value and return it as integer"""
    return int(sha256(value.encode('utf-8')).hexdigest(), 16)


hashed_structures: tp.Final[dict[str, int]] = {
    "list": _hash_to_int("[]"),
    "set": _hash_to_int("()"),
}


def compute_conf_hash(attribute: AttributeType, hash_sum: int = 0) -> int:

    if isinstance(attribute._value, dict):
        for key in attribute._value:
            """ hash += hash(sum_of_the_hashes_inside_value) + hash(key) """
            hash_sum += compute_conf_hash(attribute._value[key], hash_sum)  # hash inside value
            hash_sum += _hash_to_int(_type_hashed(hash_sum))  # hash(hash)
            hash_sum += _hash_to_int(key)  # hash(key)

    elif isinstance(attribute._value, set):
        for elem in attribute._value:
            if isinstance(elem._value, (list, set, dict)):
                hash_sum += compute_conf_hash(elem, hash_sum)
            else:
                hash_sum += _hash_to_int(_type_hashed(elem._value))
        hash_sum += hashed_structures["set"]

    elif isinstance(attribute._value, list):
        for elem in attribute._value:
            if isinstance(elem._value, (list, set, dict)):
                hash_sum += compute_conf_hash(elem, hash_sum)
            else:
                hash_sum = hash_sum + _hash_to_int(_type_hashed(elem._value))
                hash_sum = _hash_to_int(_type_hashed(hash_sum))  # to ensure the order hasn't changed
        hash_sum += hashed_structures["list"]

    else:
        hash_sum += _hash_to_int(_type_hashed(attribute._value))

    return hash_sum
