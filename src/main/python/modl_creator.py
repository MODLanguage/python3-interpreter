from typing import List, Union

import parser


class ModlValue:
    def get_by_name(self, name: str):
        raise ValueError

    def get_by_index(self, index: int):
        raise ValueError

    def get_keys(self):
        raise ValueError

    def get_value(self):
        """Do we need this?"""
        return self.get_modl_values()

    def get_modl_values(self):
        raise ValueError

    def is_modl_object(self) -> bool:
        return False

    def is_structure(self):
        return False

    def is_array(self):
        return False

    def is_map(self):
        return False

    def is_pair(self):
        return False

    def is_terminal(self):
        return False

    def is_string(self):
        return False

    def is_number(self):
        return False

    def is_false(self):
        return False

    def is_true(self):
        return False

    def is_null(self):
        return False


class Structure(ModlValue):
    pass


class Pair(Structure):
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def is_pair(self):
        return True

    def get_key(self):
        return self.key

    def get_keys(self):
        return [self.key]

    def get_value(self):
        return self.value

    def get_modl_values(self):
        # return [self.value]  # TODO: this is why we're getting extra nesting?! See comment in printer.to_json()
        return self.value  # TODO: is this why we're getting extra nesting?! See comment in printer.to_json()

    def add_modl_value(self, value):
        if not value:
            return

        if not self.value:
            self.value = value
            return

        old_value = self.value
        if isinstance(old_value, Map):
            self.value.add(value)
        elif isinstance(old_value, Pair) and isinstance(value, Pair):
            self.value = Map()
            self.value.add(old_value)
            self.value.add(value)
        else:
            self.value = Array()
            self.value.add(old_value)
            self.value.add(value)



class Map(Structure):
    def __init__(self):
        super().__init__()
        self.map_items: List[Pair] = []

    def is_map(self) -> bool:
        return True

    def add(self, pair: Pair):
        self.map_items.append(pair)

    def get_by_name(self, key):
        for map_item in self.map_items:
            if map_item.key == key:
                return map_item.value

    def get_by_index(self, index):
        return self.map_items[index]

    def get_modl_values(self):
        return self.map_items

    def get_keys(self):
        return [mi.key for mi in self.map_items]


class Array(Structure):
    def __init__(self):
        super().__init__()
        self.array_items = []

    def is_array(self):
        return True

    def add(self, value: ModlValue):
        self.array_items.append(value)

    def get_by_index(self, index: int):
        return self.array_items[index]

    def get_by_name(self, name: str):
        for v in self.array_items:
            if isinstance(v, Pair):
                if v.get_key() == name:
                    return v
        return None

    def get_modl_values(self):
        return self.array_items


class Subcondition(Structure):
    pass

class Condition(Subcondition):
    def __init__(self, key: str, operator: str, values: List[ModlValue]):
        self.key: str = key
        self.operator: str = operator
        self.values: List[ModlValue] = values

    def get_key(self):
        return self.key

    def get_operator(self):
        return self.operator

    def get_values(self):
        return self.values

class ConditionTest(Structure):
    def __init__(self):
        self.subconditions = {}

    def add_subcondition(self, operator: str, should_negate: bool, subcon: Subcondition):
        self.subconditions[subcon] = (operator, should_negate)

    def subconditions(self):
        return self.subconditions

class ConditionGroup(Subcondition):
    def __init__(self):
        self.conditions_test_list = []

    def add_condition_test(self, condition_test: ConditionTest, operator: str):
        self.conditions_test_list.append((condition_test, operator))

    def get_conditions_test_list(self):
        return self.conditions_test_list


class Conditional(ModlValue):
    pass

class ValueConditionalReturn:
    def __init__(self):
        self.values: List[ModlValue] = []

    def add(self, value: ModlValue):
        self.values.append(value)

    def get_values(self):
        return self.values


class ValueConditional(Conditional):
    def __init__(self):
        self.conditionals = {}

    def add_conditional(self, condition_test: ConditionTest, conditional_return: ValueConditionalReturn):
        self.conditionals[condition_test] = conditional_return



class ModlObject(ModlValue):
    """Represents the final, interpreted MODL tree. This may for example
    be transformed into another format such as JSON."""
    def __init__(self):
        self.structures: List[Structure] = []

    def get_by_index(self, index: int):
        return self.structures[index]

    def add_structures(self, structures):
        if structures is not None:
            for struct in structures:
                self.structures.append(struct)


class RawModlObject(ModlObject):
    def __init__(self):
        super().__init__()


def process_modl_parsed(parsed: parser.ModlParsed) -> RawModlObject:
    """Post-process the parsed tree, transforming it into an object ready for interpreting"""
    raw_modl_object = RawModlObject()

    for parsed_struct in parsed.structures:
        # TODO: why are we getting a list of lists back here, instead of a list?
        structures = process_modl_structure(raw_modl_object, parsed_struct)
        raw_modl_object.add_structures(structures)

    return raw_modl_object


def process_modl_structure(raw: RawModlObject, parsed_structure: parser.Structure) -> Union[None,List[Structure]]:
    if parsed_structure is None:
        return None

    structures: List[Structure] = []

    structure = process_modl_item(raw, parsed_structure.map)
    if structure is not None:
        structures.append(structure)
        return structures

    structure = process_modl_item(raw, parsed_structure.array)
    if structure is not None:
        structures.append(structure)
        return structures

    structure = process_modl_item(raw, parsed_structure.pair)
    if structure is not None:
        structures.append(structure) # This is not in the Java
        return structures

    structure = process_modl_item(raw, parsed_structure.top_level_conditional)
    # structures.clear() # Should be clear already
    structures.append(structure)
    return structures


def process_import_statement(raw, parsed_pair: parser.Pair):
    structures: List[Structure] = []
    array: Array = process_modl_item(raw, parsed_pair.array)
    if not array:
        if parsed_pair.value_item and parsed_pair.value_item.get_value():
            array = process_modl_item(raw, parsed_pair.value_item.value.nb_array)

    if array:
        for mv in array.get_modl_values():
            pair: Pair = Pair(key=parsed_pair.get_key())
            pair.add_modl_value(mv)
            structures.append(pair)
    else:
        if parsed_pair.value_item:
            pair: Pair = Pair(key=parsed_pair.get_key())
            value_parsed = parsed_pair.value_item
            v = process_modl_item_for_parent(raw, value_parsed, pair)
            pair.add_modl_value(v)
            structures.append(pair)


def process_modl_item(raw: RawModlObject, parsed_item):
    print("Found type", type(parsed_item))

    if parsed_item is None:
        return None

    if type(parsed_item) == parser.Map:
        modl_map = Map()
        for map_item_parsed in parsed_item.map_items:
            pair = process_modl_item(raw, map_item_parsed)
            modl_map.add(pair)
        return map

    if type(parsed_item) == parser.MapItem:
        pair = process_modl_item(raw, parsed_item.map_conditional)
        if pair is not None:
            return pair
        structures = process_modl_item(raw, parsed_item.pair)
        if len(structures) > 0:
            return structures[0]

    if type(parsed_item) == parser.Value:
        # pairs = process_modl_item(raw, parsed_item.pair)
        # if len(pairs) > 0:
        #     return pairs[0]  # why? why not just parsed_item.get_value() as below?
        return parsed_item.get_value()

    if type(parsed_item) == parser.ArrayValueItem:
        # pairs = process_modl_item(raw, parsed_item.pair)
        # if len(pairs) > 0:
        #     return pairs[0]  # why? why not just parsed_item.get_value() as below?
        return parsed_item.get_value()

    if type(parsed_item) == parser.ConditionTest:
        condition_test = ConditionTest()
        for subcon_info in condition_test.subconditions:
            subcondition, (operator, should_negate) = subcon_info
            if isinstance(subcondition, parser.ConditionGroup):
                condition_group: ConditionGroup = process_modl_item(raw, subcondition)
                condition_test.add_subcondition(operator, should_negate, condition_group)
            elif isinstance(subcondition, parser.Condition):
                # This isn't really helping in python, since the different type params map to the same method
                condition: Condition = process_modl_item(raw, subcondition)
                condition_test.add_subcondition(operator, should_negate, condition)
        return condition_test

    #... various other condition related bits from Java, e.g. ModlObjectCreator:251...
    # RawModlObject.Condition processModlParsed(RawModlObject rawModlObject, ModlParsed.Condition conditionParsed)

    if type(parsed_item) == parser.Pair:
        pair = Pair(key=parsed_item.get_key())

        if parsed_item.get_key() == '*I' or parsed_item.get_key() == '*IMPORT':
            return process_import_statement(raw, parsed_item)
        else:
            modl_map = process_modl_item(raw, parsed_item.map)
            if modl_map:
                pair.add_modl_value(modl_map)
            modl_array = process_modl_item(raw, parsed_item.array)
            if modl_array:
                pair.add_modl_value(modl_array)
            if parsed_item.value_item:
                pair.add_modl_value(process_modl_item_for_parent(raw, parsed_item.value_item, pair))
            return pair


    return None


def process_modl_item_for_parent(raw: RawModlObject, value_item_parsed: parser.ValueItem, parent: Pair):
    if not value_item_parsed:
        return

    value = None

    if value_item_parsed.value_conditional:
        value = process_conditional_for_parent(raw, value_item_parsed.value_conditional, parent)

    if value_item_parsed.get_value():
        value = process_modl_item(raw, value_item_parsed.get_value())

    return value


def process_conditional_return_for_parent(raw, conditional_return_parsed: parser.ValueConditionalReturn, parent: Pair):
    if not conditional_return_parsed:
        return None

    conditional_return = ValueConditionalReturn()

    if conditional_return_parsed.value_items:
        for value_parsed in conditional_return_parsed.value_items:
            value = process_modl_item_for_parent(raw, value_parsed, parent)
            conditional_return.add(value)

    return conditional_return


def process_conditional_for_parent(raw: RawModlObject, conditional_parsed: parser.ValueConditional, parent: Pair):
    if not conditional_parsed:
        return None

    conditional = ValueConditional()

    for c_test,c_return in conditional_parsed.get_conditional_returns().items():
        conditional.add_conditional(process_modl_item(raw, c_test),
                                    process_conditional_return_for_parent(raw, c_return, parent))
        
    return conditional


