import unittest
import modl
import json


class ParseToJSONTestCase(unittest.TestCase):
    """
    Tests to ensure JSON generated by parser matches the canonical test cases
    specified in the MODL grammar project.
    """

    def test_name_number_pair(self):
        self.assertEqual('{"a": 1}', modl.to_json("a=1"))

    # def test_name_exp_pair(self):
    #     self.assertEqual('{"a": -1.34234e2}', modl.to_json("a=-1.34234e2"))

    def test_name_float_pair(self):
        self.assertEqual('{"a": 1.23}', modl.to_json("a=1.23"))

    def test_name_string_pair(self):
        self.assertEqual('{"a": "1"}', modl.to_json('a="1"'))

    def test_name_null_pair(self):
        self.assertEqual('{"b": null}', modl.to_json('b=null'))

    def test_name_boolean_pair(self):
        self.assertEqual('{"b": true}', modl.to_json('b=true'))
        self.assertEqual('{"b": false}', modl.to_json('b=false'))

    def test_base_tests(self):
        with open("../json/base_tests.json") as f:
            test_data = json.load(f)

        i = 0;
        for t in test_data:
            i += 1
            input: str = t['input']
            expected: str = json.dumps(json.loads(t['expected_output']))
            with self.subTest(msg=f"JSON {i}", input=input, expected=expected):
                actual = json.dumps(json.loads(modl.to_json(input)))
                self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()