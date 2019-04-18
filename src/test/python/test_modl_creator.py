import unittest

from modl_creator import process_modl_parsed
from parser import parse


class TestModlCreatorTestCase(unittest.TestCase):
    def test_name_number_pair(self):
        modl_parsed = parse("a=1")
        raw_modl = process_modl_parsed(modl_parsed)
        pair = raw_modl.get_by_index(0)[0]  # TODO: yet more over nesting to sort out?
        self.assertEqual(('a', 1), (pair.key, pair.value))


if __name__ == '__main__':
    unittest.main()
