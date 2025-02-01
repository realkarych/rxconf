from pathlib import Path

import pytest

import rxconf


_RESOURCE_DIR = Path.cwd() / Path("tests/resources")


def test_empty() -> None:
    conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "empty.env")

    assert conf._MetaTree__structure._root == {}


def test_primitive_types() -> None:
    conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert conf.another_bool == False  # noqa: E712
    assert conf.hash == 1


def test_key_cases() -> None:
    conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.STRANGECASE
    assert conf.STRanGeCasE
    assert conf.value == "x"


def test_numeric_casts() -> None:
    conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.integer - 1 < conf.integer < conf.integer + 1
    assert conf.integer - 0.1 < conf.integer <= int(conf.integer + 0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer**1
    assert conf.big_integer > conf.integer


def test_string_casts() -> None:
    conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.STRING[0] == "H"
    assert conf.string[1:-1] == "ello world ="
    assert str(conf.string).upper() == "HELLO WORLD =)"
    assert conf.string + "!" == "Hello world =)!"
    with pytest.raises(rxconf.exceptions.RxConfError):
        assert conf.string.unknown


def test_not_existing_attribute() -> None:
    conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    with pytest.raises(rxconf.exceptions.RxConfError):
        assert conf.string.unknown


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    env_vars = {
        "INTEGER": "42",
        "BIG_INTEGER": "100500",
        "FLOAT": "36.6",
        "STRING": "Hello world =)",
        "BOOLEAN": "true",
        "another_bool": "false",
        "NONE": "None",
        "StrANGEcAse": "abc",
        "soME_Prefix_value1": "1",
        "some_prefix_value2": "2",
        "SomePrefixValue3": "3",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    yield
    for key in env_vars:
        monkeypatch.delenv(key, raising=False)


def test_empty_from_env() -> None:
    conf = rxconf.Conf.from_env(prefix="NOT_EXISTING_PREFIX")

    assert conf._MetaTree__structure._root == {}


def test_wrong_equality() -> None:
    conf = rxconf.Conf.from_env()._MetaTree__structure
    file_conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")._MetaTree__structure
    with pytest.raises(rxconf.exceptions.RxConfError):
        assert conf == 1
    with pytest.raises(rxconf.exceptions.RxConfError):
        assert file_conf == 1


def test_correct_equality() -> None:
    conf = rxconf.Conf.from_env()
    another_conf = rxconf.Conf.from_env()
    file_conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")
    another_file_conf = rxconf.Conf.from_file(config_path=_RESOURCE_DIR / "primitives.env")
    assert conf == another_conf
    assert file_conf == another_file_conf


def test_primitive_types_from_env() -> None:
    conf = rxconf.Conf.from_env()

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert conf.another_bool == False  # noqa: E712


def test_key_cases_from_env() -> None:
    conf = rxconf.Conf.from_env()

    assert conf.STRANGECASE
    assert conf.STRanGeCasE


def test_numeric_casts_from_env() -> None:
    conf = rxconf.Conf.from_env()

    assert conf.integer - 1 < conf.integer < conf.integer + 1
    assert conf.integer - 0.1 < conf.integer <= int(conf.integer + 0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer**1
    assert conf.big_integer > conf.integer


def test_string_casts_from_env() -> None:
    conf = rxconf.Conf.from_env()

    assert conf.STRING[0] == "H"
    assert conf.string[1:-1] == "ello world ="
    assert str(conf.string).upper() == "HELLO WORLD =)"
    assert conf.string + "!" == "Hello world =)!"
    with pytest.raises(rxconf.exceptions.RxConfError):
        assert conf.string.unknown


def test_not_existing_attribute_from_env() -> None:
    conf = rxconf.Conf.from_env()

    with pytest.raises(rxconf.RxConfError):
        assert conf.string.unknown


def test_env_prefix() -> None:
    conf1 = rxconf.Conf.from_env(prefix="some_prefix_")
    assert conf1.some_prefix_value1 == 1
    assert conf1.some_PREFIX_value2 == 2

    conf2 = rxconf.Conf.from_env(prefix="some_prefix", remove_prefix=True)
    assert conf2.value1 == 1
    assert conf2.value2 == 2

    conf3 = rxconf.Conf.from_env(prefix="somePrefix", remove_prefix=True)
    assert conf3.value3 == 3


def test_repr():
    config = rxconf.config_types.EnvConfig.load_from_environment(prefix="TEST_")
    expected_repr = repr(config._root)
    assert repr(config) == expected_repr


@pytest.mark.asyncio
async def test_empty_async() -> None:
    conf = await rxconf.AsyncConf.from_file(config_path=_RESOURCE_DIR / "empty.env")

    assert conf._MetaTree__structure._root == {}


@pytest.mark.asyncio
async def test_from_env_async() -> None:
    conf2 = await rxconf.AsyncConf.from_env(prefix="some_prefix", remove_prefix=True)
    assert conf2.value1 == 1
    assert conf2.value2 == 2


@pytest.mark.asyncio
async def test_primitive_types_async() -> None:
    conf = await rxconf.AsyncConf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.integer == 42
    assert conf.float == 36.6
    assert conf.string == "Hello world =)"
    assert conf.boolean == True  # noqa: E712
    assert conf.another_bool == False  # noqa: E712


@pytest.mark.asyncio
async def test_key_cases_async() -> None:
    conf = await rxconf.AsyncConf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.STRANGECASE
    assert conf.STRanGeCasE


@pytest.mark.asyncio
async def test_numeric_casts_async() -> None:
    conf = await rxconf.AsyncConf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.integer - 1 < conf.integer < conf.integer + 1
    assert conf.integer - 0.1 < conf.integer <= int(conf.integer + 0.1)
    assert int(conf.integer) == conf.integer
    assert int(conf.integer * 2 / 2) == conf.integer**1
    assert conf.big_integer > conf.integer


@pytest.mark.asyncio
async def test_string_casts_async() -> None:
    conf = await rxconf.AsyncConf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    assert conf.STRING[0] == "H"
    assert conf.string[1:-1] == "ello world ="
    assert str(conf.string).upper() == "HELLO WORLD =)"
    assert conf.string + "!" == "Hello world =)!"
    with pytest.raises(rxconf.exceptions.RxConfError):
        assert conf.string.unknown


@pytest.mark.asyncio
async def test_not_existing_attribute_async() -> None:
    conf = await rxconf.AsyncConf.from_file(config_path=_RESOURCE_DIR / "primitives.env")

    with pytest.raises(rxconf.exceptions.RxConfError):
        assert conf.string.unknown
