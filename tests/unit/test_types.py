import sys
import unittest
from unittest.mock import MagicMock, patch


class TestTypeAliasImport(unittest.TestCase):

    @patch("sys.version_info", new=(3, 9))
    def test_import_typealias_from_typing_extensions(self):
        with patch.dict("sys.modules", {"typing_extensions": MagicMock()}):
            if "rxconf._types" in sys.modules:
                del sys.modules["rxconf._types"]
            import rxconf._types

            self.assertTrue(hasattr(rxconf._types, "TypeAlias"))

    @patch("sys.version_info", new=(3, 10))
    def test_import_typealias_from_typing(self):
        with patch.dict("sys.modules", {"typing": MagicMock()}):
            if "rxconf._types" in sys.modules:
                del sys.modules["rxconf._types"]
            import rxconf._types

            self.assertTrue(hasattr(rxconf._types, "TypeAlias"))

    @patch("sys.version_info", new=(3, 10, 1))
    def test_import_typealias_from_typing_above_310(self):
        with patch.dict("sys.modules", {"typing": MagicMock()}):
            if "rxconf._types" in sys.modules:
                del sys.modules["rxconf._types"]
            import rxconf._types

            self.assertTrue(hasattr(rxconf._types, "TypeAlias"))
