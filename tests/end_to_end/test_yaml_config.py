import datetime
from pathlib import Path

import pytest

from rxconf import AsyncRxConf, RxConf, exceptions

_RESOURCE_DIR = Path.cwd() / Path("tests/resources")


def test_empty() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.yaml")

    assert conf


@pytest.mark.asyncio
async def test_empty_async() -> None:
    conf = await AsyncRxConf.from_file_async(config_path=_RESOURCE_DIR / "empty.yaml")

    assert conf


def test_primitive_types() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.yml")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert not conf.none


@pytest.mark.asyncio
async def test_primitive_types_async() -> None:
    conf = await AsyncRxConf.from_file_async(config_path=_RESOURCE_DIR / "primitives.yml")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert not conf.none


def test_pritive_collections() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.yml")
    expected_list = [1, 2, 3]
    expected_set = {"a", "b", "c"}

    got_list = conf.list
    got_set = conf.set

    for item, expected in zip(got_list, expected_list):
        assert expected == item

    assert list(got_list) == expected_list
    assert sorted(list(got_set)) == sorted(list(expected_set))
    assert set(got_set) == expected_set


def test_key_cases() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.yml")

    assert conf.camelcase
    assert conf.CamelCase
    assert conf.snake_case
    assert conf.SNAKE_CASE
    assert conf.strangecase
    assert conf.STRanGeCasE


def test_numeric_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.yml")

    assert conf.integer-1 < conf.integer < conf.integer+1
    assert conf.integer-0.1 < conf.integer <= int(conf.integer+0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer**1
    assert conf.big_integer > conf.integer


def test_string_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.yml")

    assert conf.string[0] == "H"
    assert conf.string[1:-1] == "ello world ="
    assert str(conf.string).upper() == "HELLO WORLD =)"
    assert conf.string + "!" == "Hello world =)!"
    with pytest.raises(exceptions.RxConfError):
        assert conf.string.unknown


def test_dates() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.yml")

    assert conf.date == datetime.date(2024, 8, 17)
    assert conf.datetime == datetime.datetime(2024, 8, 17)


def test_not_existing_attribute() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.yml")

    with pytest.raises(exceptions.RxConfError):
        assert conf.string.unknown


def test_inner_structures() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "inner_structures.yml")

    assert conf.config.name == "John Doe"
    assert conf.config.age == 42
    assert conf.config.address.address == "123 Main St"
    assert not conf.config.address.city
    assert sorted(list(conf.config.hobbies)) == sorted(["1", "2", "3"])
    assert list(conf.config.preferences.favorites) == ["a", "b", "c"]
    assert conf.config.is_active == True  # noqa: E712
    assert conf.second.element == "value"
