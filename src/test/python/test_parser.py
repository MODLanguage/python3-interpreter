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

    def test_map_pair(self):
        modl = parse('a(b=2;c=3)')
        pair = modl.structures[0].pair
        actual_map = { mi.pair.key:mi.pair.value_item.value.number for mi in pair.map.map_items }
        self.assertEqual(('a', {'b':2, 'c':3}), (pair.key, actual_map))

    def test_array_pair(self):
        modl = parse('a[1;2]')
        pair = modl.structures[0].pair
        actual_items = [ai.array_value_item.number for ai in pair.array.array_items]
        self.assertEqual(('a', [1,2]), (pair.key, actual_items))

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

    def test_array(self):
        modl = parse('colours=[red;green;blue]; players=[0;1]')
        pair = modl.structures[0].pair
        self.assertEqual('colours', pair.key)
        actual_items = [ai.array_value_item.string for ai in pair.value_item.value.array.array_items]
        self.assertEqual(['red', 'green', 'blue'], actual_items)

        pair = modl.structures[1].pair
        self.assertEqual('players', pair.key)
        actual_items = [ai.array_value_item.number for ai in pair.value_item.value.array.array_items]
        self.assertEqual([0, 1], actual_items)

    def test_nb_array(self):
        modl = parse('nb=1:2:3:::4; nb2=red::blue')
        pair = modl.structures[0].pair
        self.assertEqual('nb', pair.key)
        actual_items = [ai.array_value_item.number for ai in pair.value_item.value.nb_array.array_items]
        self.assertEquals([1,2,3,None,None,4], actual_items)

        pair = modl.structures[1].pair
        self.assertEqual('nb2', pair.key)
        actual_items = [ai.array_value_item.string for ai in pair.value_item.value.nb_array.array_items]
        self.assertEquals(['red', None, 'blue'], actual_items)

    def test_conditional(self):
        modl = parse('country=gb;support_contact={country=gb?John Smith/country=us?John Doe/?None}')
        pair = modl.structures[1].pair
        self.assertEqual('support_contact', pair.key)
        conditionals = pair.value_item.get_value().value_conditionals
        for k in conditionals.keys():
            print(k)
        self.fail('Not yet working?')


if __name__ == '__main__':
    unittest.main()
