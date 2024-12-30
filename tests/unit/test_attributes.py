import unittest

from rxconf import exceptions
from rxconf.attributes import (
    EnvAttribute,
    IniAttribute,
    JsonAttribute,
    MockAttribute,
    TomlAttribute,
    VaultAttribute,
    YamlAttribute,
)


class TestAttributeType(unittest.TestCase):

    def test_init(self):
        attr = MockAttribute(10)
        self.assertEqual(attr.__getattribute__("_AttributeType__value"), 10)

    def test_int_conversion(self):
        attr = MockAttribute(10)
        self.assertEqual(int(attr), 10)

    def test_float_conversion(self):
        attr = MockAttribute(10.5)
        self.assertEqual(float(attr), 10.5)

    def test_str_conversion(self):
        attr = MockAttribute("test")
        self.assertEqual(str(attr), "test")

    def test_bool_conversion(self):
        attr = MockAttribute(True)
        self.assertTrue(attr)

    def test_addition(self):
        attr = MockAttribute(10)
        self.assertEqual(attr + 5, 15)

    def test_subtraction(self):
        attr = MockAttribute(10)
        self.assertEqual(attr - 5, 5)

    def test_multiplication(self):
        attr = MockAttribute(10)
        self.assertEqual(attr * 2, 20)

    def test_division(self):
        attr = MockAttribute(10)
        self.assertEqual(attr / 2, 5)

    def test_floordiv(self):
        attr = MockAttribute(10)
        self.assertEqual(attr // 3, 3)

    def test_mod(self):
        attr = MockAttribute(10)
        self.assertEqual(attr % 3, 1)

    def test_pow(self):
        attr = MockAttribute(2)
        self.assertEqual(attr**3, 8)

    def test_lshift(self):
        attr = MockAttribute(2)
        self.assertEqual(attr << 2, 8)

    def test_rshift(self):
        attr = MockAttribute(8)
        self.assertEqual(attr >> 2, 2)

    def test_and(self):
        attr = MockAttribute(8)
        self.assertEqual(attr & 2, 0)

    def test_xor(self):
        attr = MockAttribute(8)
        self.assertEqual(attr ^ 2, 10)

    def test_or(self):
        attr = MockAttribute(8)
        self.assertEqual(attr | 2, 10)

    def test_neg(self):
        attr = MockAttribute(8)
        self.assertEqual(-attr, -8)

    def test_pos(self):
        attr = MockAttribute(8)
        self.assertEqual(+attr, 8)

    def test_abs(self):
        attr = MockAttribute(-8)
        self.assertEqual(abs(attr), 8)

    def test_invert(self):
        attr = MockAttribute(8)
        self.assertEqual(~attr, ~8)

    def test_round(self):
        attr = MockAttribute(8.123)
        self.assertEqual(round(attr, 2), 8.12)

    def test_hash(self):
        attr = MockAttribute(8)
        self.assertEqual(hash(attr), hash(8))

    def test_len(self):
        attr = MockAttribute([1, 2, 3])
        self.assertEqual(len(attr), 3)

    def test_iter(self):
        attr = MockAttribute([1, 2, 3])
        self.assertEqual(list(iter(attr)), [1, 2, 3])

    def test_contains(self):
        attr = MockAttribute([1, 2, 3])
        self.assertTrue(2 in attr)

    def test_getitem(self):
        attr = MockAttribute([1, 2, 3])
        self.assertEqual(attr[1], 2)

    def test_eq(self):
        attr = MockAttribute(8)
        self.assertTrue(attr == 8)

    def test_ne(self):
        attr = MockAttribute(8)
        self.assertTrue(attr != 9)

    def test_lt(self):
        attr = MockAttribute(8)
        self.assertTrue(attr < 9)

    def test_le(self):
        attr = MockAttribute(8)
        self.assertTrue(attr <= 8)

    def test_gt(self):
        attr = MockAttribute(8)
        self.assertTrue(attr > 7)

    def test_ge(self):
        attr = MockAttribute(8)
        self.assertTrue(attr >= 8)

    def test_repr(self):
        attr = MockAttribute(8)
        self.assertEqual(repr(attr), "AttributeType(8)")


class TestVaultAttribute(unittest.TestCase):

    def test_getattr(self):
        attr = VaultAttribute({"key": "value"})  # type: ignore
        self.assertEqual(attr.key, "value")

    def test_getattr_key_error(self):
        attr = VaultAttribute({"key": "value"})  # type: ignore
        with self.assertRaises(exceptions.RxConfError):
            _ = attr.nonexistent_key


class TestYamlAttribute(unittest.TestCase):

    def test_getattr(self):
        attr = YamlAttribute({"key": "value"})  # type: ignore
        self.assertEqual(attr.key, "value")

    def test_getattr_key_error(self):
        attr = YamlAttribute({"key": "value"})  # type: ignore
        with self.assertRaises(exceptions.RxConfError):
            _ = attr.nonexistent_key


class TestJsonAttribute(unittest.TestCase):

    def test_getattr(self):
        attr = JsonAttribute({"key": "value"})  # type: ignore
        self.assertEqual(attr.key, "value")

    def test_getattr_key_error(self):
        attr = JsonAttribute({"key": "value"})  # type: ignore
        with self.assertRaises(exceptions.RxConfError):
            _ = attr.nonexistent_key


class TestTomlAttribute(unittest.TestCase):

    def test_getattr(self):
        attr = TomlAttribute({"key": "value"})  # type: ignore
        self.assertEqual(attr.key, "value")

    def test_getattr_key_error(self):
        attr = TomlAttribute({"key": "value"})  # type: ignore
        with self.assertRaises(exceptions.RxConfError):
            _ = attr.nonexistent_key


class TestIniAttribute(unittest.TestCase):
    def test_getattr(self):
        attr = IniAttribute({"key": "value"})  # type: ignore
        self.assertEqual(attr.key, "value")

    def test_getattr_key_error(self):
        attr = IniAttribute({"key": "value"})  # type: ignore
        with self.assertRaises(exceptions.RxConfError):
            _ = attr.nonexistent_key


class TestEnvAttribute(unittest.TestCase):

    def test_getattr(self):
        attr = EnvAttribute({"key": "value"})  # type: ignore
        self.assertEqual(attr.key, "value")

    def test_getattr_key_error(self):
        attr = EnvAttribute({"key": "value"})  # type: ignore
        with self.assertRaises(exceptions.RxConfError):
            _ = attr.nonexistent_key
