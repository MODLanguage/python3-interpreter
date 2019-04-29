import unittest

from interpreter import UnrecognisedInstruction
import modl
from modl_creator import RawModlObject, Pair


class InterpreterTestCase(unittest.TestCase):
    def test_object_index_as_array(self):
        interpreted: RawModlObject = modl.interpret('?=[red;green;blue]; fav=%1')
        # Test the resulting tree
        pair:Pair = interpreted.get_by_index(0)
        self.assertEqual(('fav', 'green'), (str(pair.key), pair.get_value()))
        self.assertEqual(1, len(interpreted.structures))

    def test_object_index_as_multivalue(self):
        interpreted: RawModlObject = modl.interpret('?=red:green:blue; fav=%1')
        # Test the resulting tree
        pair:Pair = interpreted.get_by_index(0)
        self.assertEqual(('fav', 'green'), (str(pair.key), pair.get_value()))
        self.assertEqual(1, len(interpreted.structures))

    def test_unrecognised_config(self):
        try:
            modl.interpret('*blah=hello')
            self.fail("Failure was expected, since *blah is not a valid interpreter instruction")
        except UnrecognisedInstruction:
            # good!
            pass


if __name__ == '__main__':
    unittest.main()
