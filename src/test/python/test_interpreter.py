import unittest
from interpreter import interpret
from modl_creator import process_modl_parsed
import parser


class MyTestCase(unittest.TestCase):
    def test_object_index_as_array(self):
        parsed = parser.parse('?=[red;green;blue]; fav=%1')
        processed = process_modl_parsed(parsed)
        interpreted = interpret(processed)
        # Test the resulting tree
        pair = interpreted.structures[0].pair
        self.assertEqual(('fav', 'green'), (pair.key, pair.value_item.value.get_value()))
        self.assertEqual(1, len(interpreted.structures))

    def test_object_index_as_multivalue(self):
        parsed = parser.parse('?=red:green:blue; fav=%1')
        processed = process_modl_parsed(parsed)
        interpreted = interpret(processed)
        # Test the resulting tree
        pair = interpreted.structures[0].pair
        self.assertEqual(('fav', 'green'), (pair.key, pair.value_item.value.get_value()))
        self.assertEqual(1, len(interpreted.structures))


if __name__ == '__main__':
    unittest.main()
