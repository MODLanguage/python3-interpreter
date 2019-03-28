import unittest
import modl


class ParseToJSONTestCase(unittest.TestCase):
    """
    Tests to ensure JSON generated by parser matches the canonical test cases
    specified in the MODL grammar project.
    """

    def test_name_number_pair(self):
        self.assertEqual('{"a": 1}', modl.to_json("a=1"))

    def test_name_string_pair(self):
        self.assertEqual('{"a": "1"}', modl.to_json('a="1"'))


if __name__ == '__main__':
    unittest.main()