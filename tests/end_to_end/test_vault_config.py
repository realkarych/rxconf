import hvac  # type: ignore
import pytest

from rxconf import RxConf, exceptions


VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = "root"


def set_vault_data() -> None:
    vault_primitive_data = {
        "integer": 42,
        "big_integer": 100500,
        "float": 36.6,
        "string": "Hello world =)",
        "boolean": True,
        "none": None,
        "list": [1, 2, 3],
        "set": ["a", "b", "c"],
        "CamelCase": "ok",
        "snake_case": "ok",
        "StRanGeCasE": "ok",
    }

    vault_inner_data = {
        "config": {
            "name": "John Doe",
            "age": 42,
            "Address": {"ADDRESS": "123 Main St", "city": None},
            "preferences": {"FaVoriteS": ["a", "b", "c"]},
            "is_active": True,
        }
    }

    client = hvac.Client(
        url=VAULT_ADDR,
        token=VAULT_TOKEN,
    )

    client.secrets.kv.v2.create_or_update_secret(
        path="test_vault/vault_primitive_data",
        secret=vault_primitive_data,
    )

    client.secrets.kv.v2.create_or_update_secret(
        path="test_vault/vault_inner_data",
        secret=vault_inner_data,
    )


set_vault_data()


def test_primitive_types() -> None:
    conf = RxConf.from_vault(token=VAULT_TOKEN, ip=VAULT_ADDR, path="test_vault/vault_primitive_data")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert not conf.none


def test_primitive_collections() -> None:
    conf = RxConf.from_vault(token=VAULT_TOKEN, ip=VAULT_ADDR, path="test_vault/vault_primitive_data")

    expected_list = [1, 2, 3]
    expected_set = {"a", "b", "c"}

    got_list = conf.list
    got_set = conf.set

    for item, expected in zip(got_list, expected_list):
        assert expected == item

    assert list(got_list) == expected_list
    assert sorted(got_set) == sorted(expected_set)
    assert set(got_set) == expected_set


def test_key_cases() -> None:
    conf = RxConf.from_vault(token=VAULT_TOKEN, ip=VAULT_ADDR, path="test_vault/vault_primitive_data")

    assert conf.camelcase
    assert conf.CamelCase
    assert conf.snake_case
    assert conf.SNAKE_CASE
    assert conf.strangecase
    assert conf.STRanGeCasE


def test_numeric_cast() -> None:
    conf = RxConf.from_vault(token=VAULT_TOKEN, ip=VAULT_ADDR, path="test_vault/vault_primitive_data")

    assert conf.integer - 1 < conf.integer < conf.integer + 1
    assert conf.integer - 0.1 < conf.integer <= int(conf.integer + 0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer**1
    assert conf.big_integer > conf.integer


def test_string_cast() -> None:
    conf = RxConf.from_vault(token=VAULT_TOKEN, ip=VAULT_ADDR, path="test_vault/vault_primitive_data")

    assert conf.string[0] == "H"
    assert conf.string[1:-1] == "ello world ="
    assert str(conf.string).upper() == "HELLO WORLD =)"
    assert conf.string + "!" == "Hello world =)!"
    with pytest.raises(exceptions.RxConfError):
        assert conf.string.unknown


def test_inner() -> None:
    conf = RxConf.from_vault(token=VAULT_TOKEN, ip=VAULT_ADDR, path="test_vault/vault_inner_data")

    assert conf.config.name == "John Doe"
    assert conf.config.age == 42
    assert conf.config.address.address == "123 Main St"
    assert not conf.config.address.city
    assert list(conf.config.preferences.favorites) == ["a", "b", "c"]
    assert conf.config.is_active == True  # noqa: E712
