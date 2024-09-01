import datetime
import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from rxconf import AsyncRxConf, RxConf, exceptions

_RESOURCE_DIR = Path.cwd() / Path("tests/resources")


def test_import_tomllib():
    if 'rxconf.config_types' in sys.modules:
        del sys.modules['rxconf.config_types']
    import rxconf.config_types
    importlib.reload(rxconf.config_types)
    assert any((
        'tomllib' in sys.modules and 'toml' not in sys.modules,
        'tomllib' not in sys.modules and 'toml' in sys.modules,
    )), f"Expected 'tomllib' or 'toml' in sys.modules, but got {sys.modules.keys()}"


def test_import_toml():
    with patch.object(sys, 'version_info', (3, 10)):
        if 'rxconf.config_types' in sys.modules:
            del sys.modules['rxconf.config_types']
        import rxconf.config_types
        importlib.reload(rxconf.config_types)
        assert 'toml' in sys.modules, f"Expected 'toml' in sys.modules, but got {sys.modules.keys()}"


def test_empty() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.toml")

    assert conf


@pytest.mark.asyncio
async def test_empty_async() -> None:
    conf = await AsyncRxConf.from_file_async(config_path=_RESOURCE_DIR / "empty.toml")

    assert conf


def test_primitive_types() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.toml")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712


@pytest.mark.asyncio
async def test_primitive_types_async() -> None:
    conf = await AsyncRxConf.from_file_async(config_path=_RESOURCE_DIR / "primitives.toml")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712


def test_pritive_collections() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.toml")
    expected_list = [1, 2, 3]

    got_list = conf.list

    for item, expected in zip(got_list, expected_list):
        assert expected == item
    assert list(got_list) == expected_list


def test_key_cases() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.toml")

    assert conf.camelcase
    assert conf.CamelCase
    assert conf.snake_case
    assert conf.SNAKE_CASE
    assert conf.strangecase
    assert conf.STRanGeCasE


def test_numeric_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.toml")

    assert conf.integer - 1 < conf.integer < conf.integer + 1
    assert conf.integer - 0.1 < conf.integer <= int(conf.integer + 0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer ** 1
    assert conf.big_integer > conf.integer


def test_string_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.toml")

    assert conf.string[0] == "H"
    assert conf.string[1:-1] == "ello world ="
    assert str(conf.string).upper() == "HELLO WORLD =)"
    assert conf.string + "!" == "Hello world =)!"
    with pytest.raises(exceptions.RxConfError):
        assert conf.string.unknown


def test_dates() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.toml")

    assert conf.date == datetime.date(2024, 8, 17)
    assert conf.datetime == datetime.datetime(2024, 8, 17)


def test_not_existing_attribute() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.toml")

    with pytest.raises(exceptions.RxConfError):
        assert conf.string.unknown


@pytest.mark.asyncio
async def test_not_existing_attribute_async() -> None:
    conf = await AsyncRxConf.from_file_async(config_path=_RESOURCE_DIR / "primitives.toml")

    with pytest.raises(exceptions.RxConfError):
        assert conf.string.unknown


def test_inner_structures() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "inner_structures.toml")

    assert conf.config.name == "John Doe"
    assert conf.config.age == 42
    assert conf.config.address.address == "123 Main St"
    assert list(conf.config.hobbies.hobbies) == ["1", "2", "3"]
    assert conf.config.hobbies.is_active == True  # noqa: E712
    assert conf.second.element == "value"
