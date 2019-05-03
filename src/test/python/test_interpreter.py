import unittest

from interpreter import UnrecognisedInstruction
import modl
from modl_creator import RawModlObject, Pair


class InterpreterTestCase(unittest.TestCase):
    def test_object_index_as_array(self):
        interpreted: RawModlObject = modl.interpret('?=[red;green;blue]; fav=%1')
        # Test the resulting tree
        pair:Pair = interpreted.get_by_index(0)
        self.assertEqual(('fav', 'green'), (str(pair.key), str(pair.get_value())))
        self.assertEqual(1, len(interpreted.structures))

    def test_object_index_as_multivalue(self):
        interpreted: RawModlObject = modl.interpret('?=red:green:blue; fav=%1')
        # Test the resulting tree
        pair:Pair = interpreted.get_by_index(0)
        self.assertEqual(('fav', 'green'), (str(pair.key), str(pair.get_value())))
        self.assertEqual(1, len(interpreted.structures))

    def test_object_ref_by_name(self):
        interpreted: RawModlObject = modl.interpret('_red=#f00; _green=#0f0; _blue=#00f; fav=%blue')
        # Test the resulting tree
        pair:Pair = interpreted.get_by_index(0)
        self.assertEqual(('fav', '#00f'), (str(pair.key), str(pair.get_value())))
        self.assertEqual(1, len(interpreted.structures))

    def test_bool_true(self):
        interpreted: RawModlObject = modl.interpret('sky_is_blue=true')
        pair: Pair = interpreted.get_by_index(0)
        key_modl_obj = pair.get_key()
        value_modl_obj = pair.get_value()
        self.assertEqual('sky_is_blue', str(key_modl_obj))
        self.assertEqual(True, value_modl_obj.get_value())
        self.assertTrue(value_modl_obj.is_true())
        self.assertFalse(value_modl_obj.is_false())

    def test_bool_false(self):
        interpreted: RawModlObject = modl.interpret('sky_is_blue=false')
        pair: Pair = interpreted.get_by_index(0)
        key_modl_obj = pair.get_key()
        value_modl_obj = pair.get_value()
        self.assertEqual('sky_is_blue', str(key_modl_obj))
        self.assertEqual(False, value_modl_obj.get_value())
        self.assertFalse(value_modl_obj.is_true())
        self.assertTrue(value_modl_obj.is_false())

    def test_unrecognised_config(self):
        try:
            modl.interpret('*blah=hello')
            self.fail("Failure was expected, since *blah is not a valid interpreter instruction")
        except UnrecognisedInstruction:
            # good!
            pass


if __name__ == '__main__':
    unittest.main()
