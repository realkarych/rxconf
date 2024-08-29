from pathlib import Path

import pytest

from rxconf import RxConf, exceptions

_RESOURCE_DIR = Path.cwd() / Path("tests/resources")


def test_empty() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.ini")

    assert conf


def test_primitive_types() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.ini")

    assert conf.primitives.integer == 42
    assert conf.primitives.float == 36.6
    assert conf.primitives.string == "Hello world =)"
    assert conf.primitives.boolean


def test_key_cases() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.ini")

    assert conf.primitives.camelcase
    assert conf.primitives.CamelCase
    assert conf.primitives.snake_case
    assert conf.primitives.SNAKE_CASE
    assert conf.primitives.strangecase
    assert conf.primitives.STRanGeCasE


def test_numeric_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.ini")

    assert conf.primitives.integer - 1 < conf.primitives.integer < conf.primitives.integer + 1
    assert conf.primitives.integer - 0.1 < conf.primitives.integer <= int(conf.primitives.integer + 0.1)
    assert int(conf.primitives.integer) == conf.primitives.integer
    assert int(conf.primitives.integer * 2 / 2) == conf.primitives.integer ** 1
    assert conf.primitives.big_integer > conf.primitives.integer


def test_string_casts() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "primitives.ini")

    assert conf.primitives.string[0] == "H"
    assert conf.primitives.string[1:-1] == "ello world ="
    assert str(conf.primitives.string).upper() == "HELLO WORLD =)"
    assert conf.primitives.string + "!" == "Hello world =)!"
    with pytest.raises(exceptions.RxConfError):
        assert conf.primitives.string.unknown


def test_inner_structures() -> None:
    conf = RxConf.from_file(config_path=_RESOURCE_DIR / "inner_structures.ini")

    assert conf.config.name == "John Doe"
    assert conf.config.age == 42
    assert conf.config.address.address == "123 Main St"
    assert not conf.config.address.city
    assert conf.config.active.is_active


def test_structures() -> None:
    config = RxConf.from_file(config_path=_RESOURCE_DIR / "types_and_nesting.ini")

    assert config.general.app_name == "MyApp"
    assert config.general.version == "1.2.3"
    assert config.general.debug_mode == True

    assert config.database.host == "localhost"
    assert config.database.port == 3306
    assert config.database.username == "root"
    assert config.database.password == "password123"
    assert config.database.max_connections == 100
    assert config.database.timeout == 30.5

    assert config.api.enabled == True
    assert config.api.base_url == "https://api.example.com"
    assert config.api.retry_attempts == 5
    assert config.api.timeout_seconds == 10.0

    assert config.logging.log_level == "DEBUG"
    assert config.logging.log_file == "/var/log/myapp.log"
    assert config.logging.api.log_requests == True
    assert config.logging.api.log_responses == False

    assert config.caches.type == "redis"
    assert config.caches.host == "127.0.0.1"
    assert config.caches.port == 6379
    assert config.caches.enabled == True

    assert config.features.enabled_features == "feature1"
    assert config.features.feature1.description == "This is feature 1"
    assert config.features.feature1.max_users == 50
    assert config.features.feature2.description == "This is feature 2"
    assert config.features.feature2.max_users == 100

    assert config.users.admin_users == "alice"
    assert config.users.regular_users == "dave"
    assert config.users.alice.email == "alice@example.com"
    assert config.users.alice.is_active == True
    assert config.users.bob.email == "bob@example.com"
    assert config.users.bob.is_active == False


def test_creates_nested_dict():
    config = RxConf.from_file(config_path=_RESOURCE_DIR / "deep_nesting_schema.ini")

    assert config.database.main.settings.username == 'example_user'
    assert config.database.main.settings.password == 'secret'
    assert config.database.main.connection.host == 'localhost'
    assert config.database.main.connection.port == 3306

