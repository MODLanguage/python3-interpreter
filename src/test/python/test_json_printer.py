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

    # TODO: do we want to keep the format of the original input?
    def test_name_exp_pair(self):
        self.assertEqual('{"a": -1342340000000.0}', modl.to_json("a=-1.34234e12"))

    def test_name_float_pair(self):
        self.assertEqual('{"a": 1.23}', modl.to_json("a=1.23"))

    def test_name_string_pair(self):
        self.assertEqual('{"a": "hello"}', modl.to_json('a=hello'))

    def test_name_quoted_pair(self):
        self.assertEqual('{"a": "1"}', modl.to_json('a="1"'))

    def test_name_null_pair(self):
        self.assertEqual('{"b": null}', modl.to_json('b=null'))

    def test_name_boolean_pair(self):
        self.assertEqual('{"b": true}', modl.to_json('b=true'))
        self.assertEqual('{"b": false}', modl.to_json('b=false'))

    def test_simple_array(self):
        self.assertEqual('["a", "b", "c"]', modl.to_json('[a;b;c]'))

    def test_base_tests(self):
        with open("../json/base_tests.json") as f:
            test_data = json.load(f)

        print(f"Running {len(test_data)} test cases in base_tests.json")
        i = 0
        for t in test_data:
            i += 1
            # Restrict which tests are run - comment out to run all
            # if i not in range(102,103):
            #     continue
            input: str = t['input']
            with self.subTest(msg=f"JSON {i}", input=input):
                expected = json.loads(t['expected_output'])
                actual_str = modl.to_json(input)
                actual = json.loads(actual_str)
                # Compare JSON structures rather than strings, so that we're not failing on, e.g. whitespace
                self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
