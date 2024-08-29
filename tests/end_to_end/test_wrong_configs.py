from pathlib import Path

import pytest

from rxconf import RxConf, exceptions

_RESOURCE_DIR = Path.cwd() / Path("tests/resources")


def test_not_existing_yaml() -> None:
    with pytest.raises(exceptions.ConfigNotFoundError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "something_not_exist.yaml")


def test_broken_schema_yaml() -> None:
    with pytest.raises(exceptions.BrokenConfigSchemaError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "broken_schema.yml")


def test_not_existing_json() -> None:
    with pytest.raises(exceptions.ConfigNotFoundError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "something_not_exist.json")


def test_broken_schema_json() -> None:
    with pytest.raises(exceptions.BrokenConfigSchemaError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "broken_schema.json")


def test_not_existing_toml() -> None:
    with pytest.raises(exceptions.ConfigNotFoundError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "something_not_exist.toml")


def test_broken_schema_toml() -> None:
    with pytest.raises(exceptions.BrokenConfigSchemaError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "broken_schema.toml")


def test_unrecognized_extension() -> None:
    with pytest.raises(exceptions.InvalidExtensionError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "something.tpl")


def test_not_existing_ini() -> None:
    with pytest.raises(exceptions.ConfigNotFoundError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "something_not_exist.ini")


def test_broken_schema_ini() -> None:
    with pytest.raises(exceptions.BrokenConfigSchemaError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "broken_schema.ini")


def test_unsupported_ini_type() -> None:
    with pytest.raises(exceptions.BrokenConfigSchemaError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "unsupported_data_type.ini")
