import typing as tp
from hashlib import sha256

from . import attributes


def _hash_with_type(value: tp.Any) -> str:
    """
    Return the type and value of the given value.
    Needed to hash the value and distinguish between different types.
    Example: _hash_with_type(5) -> "int5"
    """

    return f"{type(value).__name__}{value}"


def _hash_to_int(value: str) -> int:
    """
    Hash the value and return it as an integer.
    Uses sha256 to hash the value and converts it to an integer.
    """

    return int(sha256(value.encode("utf-8")).hexdigest(), 16)


# Hashed structures to distinguish between different types of structures.
HASHED_STRUCTURES: tp.Final[dict[str, int]] = {
    "list": _hash_to_int("[]"),
    "set": _hash_to_int("()"),
}


def compute_conf_hash(attribute: attributes.AttributeType, hash_sum: int = 0) -> int:
    """
    Compute the hash of the given attribute.
    The hash is computed by hashing the type and value of the attribute.
    Works recursively for nested attributes.
    """

    # Name mangling to access the private value of the attribute.
    # Reason: AttributeType overrides all magic methods and provide abstraction for the value.
    # User do not have direct access to the value of the attribute.
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


# Sault the root attributes to distinguish between built-in attributes and config attributes.
# The sault is hardcoded, but it can be changed to any other value.
# The main idea: exclude the possibility of name collisions between built-in attributes and config attributes.
# For example: config has the `hash` attribute on the top-level, but the built-in attribute has the same name.
ATTR_SAULT: tp.Final[str] = "b35f36857ba6b56d"
