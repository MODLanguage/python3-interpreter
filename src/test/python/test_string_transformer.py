import unittest

from modl_creator import String, TrueVal, FalseVal
from string_transformer import StringTransformer


class StringTransformerTestCase(unittest.TestCase):
    def test_numbered_variable(self):
        transformer = StringTransformer({}, {}, {0: String('hello'), 1: String('world'), 2: String('goodbye')})
        self.assertEqual(String('hello'), transformer.transform('%0'))
        self.assertEqual(String('world'), transformer.transform('%1'))
        self.assertEqual(String('goodbye'), transformer.transform('%2'))
        self.assertEqual(String('hello goodbye'), transformer.transform('%0 %2'))
        self.assertEqual(String('hello'), transformer.transform('`%0`'))

    def test_boolean(self):
        transformer = StringTransformer({}, {}, {})
        self.assertEqual(TrueVal(), transformer.transform('true'))
        self.assertEqual(FalseVal(), transformer.transform('false'))

    def test_unescape(self):
        transformer = StringTransformer({}, {}, {})
        self.assertEqual(String('\n&'), transformer.transform('\\n~&'))


if __name__ == '__main__':
    unittest.main()
