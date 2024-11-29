from rxconf import AttributeType
from hashlib import sha256


def hash_to_int(value: str) -> int:
    """Hash the value and return it as integer"""
    return int(sha256(value.encode('utf-8')).hexdigest(), 16)

struct_hash = {
        "list": hash_to_int("[]"),
        "set": hash_to_int("()"),
    }

def compute_conf_hash(attribute: AttributeType, hash_sum: int = 0) -> int:
    if isinstance(attribute._value, dict):
        for key in attribute._value:
            """ hash += hash(sum_of_the_hashes_inside_value) + hash(key) """
            hash_sum += compute_conf_hash(attribute._value[key], hash_sum)  # hash inside value
            hash_sum += hash_to_int(str(hash_sum))  # hash(hash)
            hash_sum += hash_to_int(key)  # hash(key)
    elif isinstance(attribute._value, (list, set)):
        for elem in attribute._value:
            if isinstance(elem._value, (list, set, dict)):
                hash_sum += compute_conf_hash(elem, hash_sum)
            else:
                hash_sum += hash_to_int(str(elem._value))
        hash_sum += struct_hash[type(attribute._value).__name__]
    else:
        hash_sum += hash_to_int(str(attribute._value))

    return hash_sum
