import unittest

from modl import interpret
from modl_creator import RawModlObject, Pair


class MyTestCase(unittest.TestCase):
    @unittest.skip('Not yet implemented')
    def test_object_index_as_array(self):
        interpreted: RawModlObject = interpret('?=[red;green;blue]; fav=%1')
        # Test the resulting tree
        pair:Pair = interpreted.get_by_index(0)
        self.assertEqual(('fav', 'green'), (str(pair.key), pair.get_value()))
        self.assertEqual(1, len(interpreted.structures))

    @unittest.skip('Not yet implemented')
    def test_object_index_as_multivalue(self):
        interpreted: RawModlObject = interpret('?=red:green:blue; fav=%1')
        # Test the resulting tree
        pair:Pair = interpreted.get_by_index(0)
        self.assertEqual(('fav', 'green'), (str(pair.key), pair.get_value()))
        self.assertEqual(1, len(interpreted.structures))


if __name__ == '__main__':
    unittest.main()
