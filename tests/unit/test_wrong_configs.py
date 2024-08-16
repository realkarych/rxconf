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


def test_unrecognized_extension() -> None:
    with pytest.raises(exceptions.InvalidExtensionError):
        assert RxConf.from_file(config_path=_RESOURCE_DIR / "something.tpl")
