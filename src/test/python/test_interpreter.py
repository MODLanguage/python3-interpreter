import unittest
from interpreter import ModlInterpreter
import parser


class MyTestCase(unittest.TestCase):
    def test_object_index_as_array(self):
        parsed = parser.parse('?=[red;green;blue]; fav=%1')
        interpreted = ModlInterpreter().interpret(parsed)
        # Test the resulting tree
        pair = interpreted.structures[0].pair
        self.assertEqual(('fav', 'green'), (pair.key, pair.value_item.value.get_value()))
        self.assertEqual(1, len(interpreted.structures))

    def test_object_index_as_multivalue(self):
        parsed = parser.parse('?=red:green:blue; fav=%1')
        interpreted = ModlInterpreter().interpret(parsed)
        # Test the resulting tree
        pair = interpreted.structures[0].pair
        self.assertEqual(('fav', 'green'), (pair.key, pair.value_item.value.get_value()))
        self.assertEqual(1, len(interpreted.structures))

if __name__ == '__main__':
    unittest.main()
