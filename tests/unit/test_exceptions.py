import unittest

import rxconf


class TestInvalidAttributeError(unittest.TestCase):
    def test_invalid_attribute_error_message(self):
        message = "Invalid attribute found"
        with self.assertRaises(rxconf.InvalidAttributeError) as context:
            raise rxconf.InvalidAttributeError(message)

        self.assertEqual(str(context.exception), message)
