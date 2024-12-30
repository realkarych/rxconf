from unittest.mock import patch

import pytest

from rxconf import config_resolver, config_types, exceptions


@pytest.fixture
def resolver():
    return config_resolver.FileConfigResolver(config_types=config_types.BASE_FILE_CONFIG_TYPES)


def test_resolve_yaml_file(resolver):
    path = "config.yaml"
    with (
        patch("os.path.splitext", return_value=("config", ".yaml")),
        patch("rxconf.config_types.YamlConfig.__init__", return_value=None),
    ):
        config_type = resolver.resolve(path)
        assert config_type == config_types.YamlConfig


def test_resolve_json_file(resolver):
    path = "config.json"
    with (
        patch("os.path.splitext", return_value=("config", ".json")),
        patch("rxconf.config_types.JsonConfig.__init__", return_value=None),
    ):
        config_type = resolver.resolve(path)
        assert config_type == config_types.JsonConfig


def test_resolve_toml_file(resolver):
    path = "config.toml"
    with (
        patch("os.path.splitext", return_value=("config", ".toml")),
        patch("rxconf.config_types.TomlConfig.__init__", return_value=None),
    ):
        config_type = resolver.resolve(path)
        assert config_type == config_types.TomlConfig


def test_resolve_ini_file(resolver):
    path = "yaml.toml.ini"
    with (
        patch("os.path.splitext", return_value=("yaml.toml.ini", ".ini")),
        patch("rxconf.config_types.IniConfig.__init__", return_value=None),
    ):
        config_type = resolver.resolve(path)
        assert config_type == config_types.IniConfig


def test_resolve_dotenv_file(resolver):
    path = ".env"
    with (
        patch("os.path.splitext", return_value=(".env", ".env")),
        patch("rxconf.config_types.DotenvConfig.__init__", return_value=None),
    ):
        config_type = resolver.resolve(path)
        assert config_type == config_types.DotenvConfig


def test_resolve_invalid_extension(resolver):
    path = "config.txt"
    with patch("os.path.splitext", return_value=("config", ".txt")):
        with pytest.raises(exceptions.InvalidExtensionError) as excinfo:
            resolver.resolve(path)
        assert "invalid extension" in str(excinfo.value)


def test_resolve_empty_config_types():
    resolver = config_resolver.FileConfigResolver(config_types=[])
    path = "config.yaml"
    with patch("os.path.splitext", return_value=("config", ".yaml")):
        with pytest.raises(exceptions.InvalidExtensionError) as excinfo:
            resolver.resolve(path)
        assert "invalid extension" in str(excinfo.value)


def test_resolve_case_insensitive_extension(resolver):
    path = "config.YAML"
    with (
        patch("os.path.splitext", return_value=("config", ".YAML")),
        patch("rxconf.config_types.YamlConfig.__init__", return_value=None),
    ):
        config_type = resolver.resolve(path)
        assert config_type == config_types.YamlConfig
