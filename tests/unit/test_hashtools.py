import unittest
from pathlib import Path
from rxconf import RxConf


_RESOURCE_DIR = Path.cwd() / Path("tests/resources")
_CONF_HASH_DIR = Path.cwd() / Path("tests/resources/conf_hashing")


class TestComputeConfHash(unittest.TestCase):
    # ---------- RxConf ------------
    # def test_empty_to_equal(self):
    #     conf1 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.ini")
    #     conf2 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.yaml")
    #     conf3 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.env")
    #     conf4 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.toml")
    #     conf5 = RxConf.from_file(config_path=_RESOURCE_DIR / "empty.json")
    #
    #     self.assertEqual(conf1 == conf2, True)
    #     self.assertEqual(conf2 == conf3, True)
    #     self.assertEqual(conf3 == conf4, True)
    #     self.assertEqual(conf4 == conf5, True)

    def test_same_attribute_structures(self):
        conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.ini")
        conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.yml")

        self.assertEqual(conf1 == conf2, True)

    def test_list_and_set_to_differ(self):
        conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "yaml_with_list.yaml")
        conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "yaml_with_set.yaml")

        self.assertEqual(conf1 == conf2, False)

    def test_list_order_matters(self):
        conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "list_123.toml")
        conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "list_132.toml")

        self.assertEqual(conf1 == conf2, False)

    def test_inner_structures(self):
        conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "inner_structures.yml")
        conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "inner_pseudo_changed.yml")
        conf3 = RxConf.from_file(config_path=_CONF_HASH_DIR / "inner_structures.json")

        self.assertEqual(conf1 == conf3, True)
        self.assertEqual(conf1 == conf2, False)

    def test_to_differ_str_and_int(self):
        conf1 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_struct_with_str.yml")
        conf2 = RxConf.from_file(config_path=_CONF_HASH_DIR / "simple_structure.yml")

        self.assertEqual(conf1 == conf2, False)
    # --------------------------------------
    # ------------ AsyncRxConf -------------
