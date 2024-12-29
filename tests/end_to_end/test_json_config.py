from pathlib import Path

import pytest

from rxconf import AsyncRxConf, RxConf, exceptions


_RESOURCE_DIR = Path.cwd() / Path("tests/resources")


def test_empty() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.json")

    assert conf._config._root == {}


@pytest.mark.asyncio
async def test_empty_async() -> None:
    conf = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "empty.json")

    assert conf._config._root == {}


def test_primitive_types() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert not conf.none


@pytest.mark.asyncio
async def test_primitive_types_async() -> None:
    conf = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert not conf.none


def test_pritive_collections() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")
    expected_list = [1, 2, 3]
    expected_set = {"a", "b", "c"}

    got_list = conf.list
    got_set = conf.set

    for item, expected in zip(got_list, expected_list):
        assert expected == item

    assert list(got_list) == expected_list
    assert sorted(got_set) == sorted(expected_set)
    assert set(got_set) == expected_set


@pytest.mark.asyncio
async def test_pritive_collections_async() -> None:
    conf = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")
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
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")

    assert conf.camelcase
    assert conf.CamelCase
    assert conf.snake_case
    assert conf.SNAKE_CASE
    assert conf.strangecase
    assert conf.STRanGeCasE


@pytest.mark.asyncio
async def test_key_cases_async() -> None:
    conf = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")

    assert conf.camelcase
    assert conf.CamelCase
    assert conf.snake_case
    assert conf.SNAKE_CASE
    assert conf.strangecase
    assert conf.STRanGeCasE


def test_numeric_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")

    assert conf.integer - 1 < conf.integer < conf.integer + 1
    assert conf.integer - 0.1 < conf.integer <= int(conf.integer + 0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer**1
    assert conf.big_integer > conf.integer


@pytest.mark.asyncio
async def test_numeric_casts_async() -> None:
    conf = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")

    assert conf.integer - 1 < conf.integer < conf.integer + 1
    assert conf.integer - 0.1 < conf.integer <= int(conf.integer + 0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer**1
    assert conf.big_integer > conf.integer


def test_string_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.json")

    assert conf.string[0] == "H"
    assert conf.string[1:-1] == "ello world ="
    assert str(conf.string).upper() == "HELLO WORLD =)"
    assert conf.string + "!" == "Hello world =)!"
    with pytest.raises(exceptions.RxConfError):
        assert conf.string.unknown


def test_inner_structures() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "inner_structures.json")

    assert conf.config.name == "John Doe"
    assert conf.config.age == 42
    assert conf.config.address.address == "123 Main St"
    assert not conf.config.address.city
    assert list(conf.config.preferences.favorites) == ["a", "b", "c"]
    assert conf.config.is_active == True  # noqa: E712
