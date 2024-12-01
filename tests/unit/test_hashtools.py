import pytest
from pathlib import Path
from rxconf import RxConf, AsyncRxConf


_RESOURCE_DIR = Path.cwd() / Path("tests/resources")
_CONF_HASH_DIR = Path.cwd() / Path("tests/resources/conf_hashing")


# ---------- RxConf ------------
# def test_empty_to_equal():
#     conf1 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.ini")
#     conf2 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.yaml")
#     conf3 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.env")
#     conf4 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.toml")
#     conf5 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.json")
#
#     assert conf1 == conf2
#     assert conf2 == conf3
#     assert conf3 == conf4
#     assert conf4 == conf5

def test_same_attribute_structures():
    conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.ini")
    conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.yml")

    assert conf1 == conf2

def test_list_and_set_to_differ():
    conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "yaml_with_list.yaml")
    conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "yaml_with_set.yaml")

    assert conf1 != conf2

def test_list_order_matters():
    conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "list_123.toml")
    conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "list_132.toml")

    assert conf1 != conf2

def test_inner_structures():
    conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "inner_structures.yml")
    conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "inner_pseudo_changed.yml")
    conf3 = RxConf.from_file(config_path=_CONF_HASH_DIR / "inner_structures.json")

    assert conf1 == conf3
    assert conf1 == conf2

def test_to_differ_str_and_int():
    conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_struct_with_str.yml")
    conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.yml")

    assert conf1 != conf2

def test_key_order():
    conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "key_order_1_2.yml")
    conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "key_order_2_1.yml")

    assert conf1 != conf2

# --------------------------------------
# ------------ AsyncRxConf -------------

# @pytest.mark.asyncio
# async def test_async_empty_to_equal():
#     conf1 = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "empty.ini")
#     conf2 = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "empty.yaml")
#     conf3 = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "empty.env")
#     conf4 = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "empty.toml")
#     conf5 = await AsyncRxConf.from_file(config_path=_RESOURCE_DIR / "empty.json")
#
#     assert conf1 == conf2
#     assert conf2 == conf3
#     assert conf3 == conf4
#     assert conf4 == conf5

@pytest.mark.asyncio
async def test_async_same_attribute_structures():
    conf1 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.ini")
    conf2 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.yml")

    assert conf1 == conf2

@pytest.mark.asyncio
async def test_async_list_and_set_to_differ():
    conf1 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "yaml_with_list.yaml")
    conf2 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "yaml_with_set.yaml")

    assert conf1 != conf2

@pytest.mark.asyncio
async def test_async_list_order_matters():
    conf1 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "list_123.toml")
    conf2 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "list_132.toml")

    assert conf1 != conf2

@pytest.mark.asyncio
async def test_async_inner_structures():
    conf1 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "inner_structures.yml")
    conf2 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "inner_pseudo_changed.yml")
    conf3 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "inner_structures.json")

    assert conf1 == conf3
    assert conf1 == conf2

@pytest.mark.asyncio
async def test_async_to_differ_str_and_int():
    conf1 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "simple_struct_with_str.yml")
    conf2 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.yml")

    assert conf1 != conf2

@pytest.mark.asyncio
async def test_async_key_order():
    conf1 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "key_order_1_2.yml")
    conf2 = await AsyncRxConf.from_file(config_path=_CONF_HASH_DIR / "key_order_2_1.yml")

    assert conf1 != conf2