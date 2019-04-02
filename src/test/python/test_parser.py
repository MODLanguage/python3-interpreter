import unittest
from parser import parse


class ParserTestCase(unittest.TestCase):
    def test_name_number_pair(self):
        modl = parse("a=1")
        pair = modl.structures[0].pair
        self.assertEqual(('a', 1), (pair.key, pair.value_item.value.number))

    def test_name_exp_pair(self):
        modl = parse("a=-1.34234e12")
        pair = modl.structures[0].pair
        self.assertEqual(('a', -1.34234e12), (pair.key, pair.value_item.value.number))

    def test_name_float_pair(self):
        modl = parse("a=1.23")
        pair = modl.structures[0].pair
        self.assertEqual(('a', 1.23), (pair.key, pair.value_item.value.number))

    def test_name_quoted_pair(self):
        modl = parse('a="1"')
        pair = modl.structures[0].pair
        self.assertEqual(('a', '1'), (pair.key, pair.value_item.value.quoted))

    def test_name_string_pair(self):
        modl = parse('a=hello')
        pair = modl.structures[0].pair
        self.assertEqual(('a', 'hello'), (pair.key, pair.value_item.value.string))

    def test_name_null_pair(self):
        modl = parse('nothing=null')
        pair = modl.structures[0].pair
        self.assertEqual(('nothing', None), (pair.key, pair.value_item.value.number))

    def test_name_boolean_pair(self):
        modl = parse('b=true')
        pair = modl.structures[0].pair
        self.assertEqual(('b', True), (pair.key, pair.value_item.value.is_true))
        self.assertEqual(('b', False), (pair.key, pair.value_item.value.is_false))

        modl = parse('b=false')
        pair = modl.structures[0].pair
        self.assertEqual(('b', False), (pair.key, pair.value_item.value.is_true))
        self.assertEqual(('b', True), (pair.key, pair.value_item.value.is_false))

if __name__ == '__main__':
    unittest.main()
