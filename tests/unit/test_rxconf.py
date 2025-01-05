import unittest
from unittest.mock import MagicMock

from rxconf import AsyncConf, Conf


class TestConf(unittest.TestCase):

    def test_repr(self):
        mock_config = MagicMock()
        mock_config.__repr__ = MagicMock(return_value="MockConfigRepresentation")

        conf_instance = Conf(config=mock_config)

        self.assertEqual(repr(conf_instance), "MockConfigRepresentation")


class TestAsyncConf(unittest.TestCase):

    def test_repr(self):
        mock_config = MagicMock()
        mock_config.__repr__ = MagicMock(return_value="MockConfigRepresentation")

        conf_instance = AsyncConf(config=mock_config)

        self.assertEqual(repr(conf_instance), "MockConfigRepresentation")
