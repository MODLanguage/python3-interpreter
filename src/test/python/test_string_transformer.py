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

    def test_trim(self):
        transformer = StringTransformer({}, {String('v'): String('testing')}, {})
        result = transformer.transform("`%v.t(ing)`")
        self.assertEqual(String('test'), result)

    def test_uppercase(self):
        transformer = StringTransformer({}, {String('v'): String('testing')}, {})
        result = transformer.transform("%v.u")
        self.assertEqual(String('TESTING'), result)


if __name__ == '__main__':
    unittest.main()
