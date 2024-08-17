import unittest
from rxconf.exceptions import InvalidAttributeError


class TestInvalidAttributeError(unittest.TestCase):
    def test_invalid_attribute_error_message(self):
        message = "Invalid attribute found"
        with self.assertRaises(InvalidAttributeError) as context:
            raise InvalidAttributeError(message)

        self.assertEqual(str(context.exception), message)
