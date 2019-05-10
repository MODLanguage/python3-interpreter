import logging
from typing import List, Union

import modl
import parser
from modl_creator import RawModlObject, ModlObject, Pair, Structure, Map, ModlValue, Array, String, Number, \
    process_modl_parsed, ValueConditional, TrueVal, FalseVal, NullVal, MapConditional
from parser import TopLevelConditional
from string_transformer import StringTransformer


def interpret(raw_modl: RawModlObject) -> ModlObject:
    """Creates a new interpreter and invokes it against the supplied RawModlObject."""
    interpreter = ModlInterpreter()
    return interpreter.execute(raw_modl)


class RequiresRestart(BaseException):
    def __init__(self):
        super().__init__()


class UnrecognisedInstruction(BaseException):
    def __init__(self):
        super().__init__()


class ModlInterpreter:
    """Process the RawModlObject and produce a ModlObject.
    The ModlObject is the finished article."""

    def __init__(self):
        self.indexed_strings = None
        self.pair_names = set()
        self.value_pairs = {}

        self.classes = {}
        self.variables = {}
        self.numbered_variables = {}

    def execute(self, raw_modl: RawModlObject) -> ModlObject:
        modl_obj: ModlObject = None

        while modl_obj is None:
            try:
                modl_obj = self._attempt_interpret(raw_modl)
            except RequiresRestart:
                modl_obj = None  # Try again with updated raw_modl

        return modl_obj

    def _attempt_interpret(self, raw_modl: RawModlObject) -> ModlObject:
        """
        Throws a RequiresRestart exception if the return value should be ignored
        and the method run again with the same raw_modl input (which may have been
        updated by the previous attempt to interpret it).
        """
        modl_obj = ModlObject()
        self._load_class_o()  # move to __init__ ?
        self.pair_names = set()
        self.value_pairs = {}

        # Interpret raw_modl based on specified config files
        started_interpreting = False
        need_restart = False
        loaded_raw_modl: RawModlObject = None
        import_file_value: str = None

        for raw_struct in raw_modl.structures:
            if isinstance(raw_struct, Pair) and (raw_struct.key == '*V' or raw_struct.key == '*VERSION'):
                # Version number, check it, then ignore it.
                version = raw_struct.get_value().get_value()
                if version != modl.MODL_VERSION:
                    raise ValueError(f"Can't handle MODL version '{version}', requires '{modl.MODL_VERSION}'")
                continue
            if isinstance(raw_struct, Pair) and (raw_struct.key == '*I' or raw_struct.key == '*IMPORT'):
                if isinstance(raw_struct.get_value(), String):
                    import_file_value = str(raw_struct.get_value())
                    loaded_raw_modl = self._load_config_file(import_file_value)
                    need_restart = True
                    break
                elif isinstance(raw_struct.get_value(), Number):
                    import_file_value = str(raw_struct.get_value())
                    loaded_raw_modl = self._load_config_file(import_file_value)
                    need_restart = True
                    break
                continue
            if isinstance(raw_struct, Pair) and (str(raw_struct.key) in ['*class', '*c', '*method', '*m', '?']):
                key = str(raw_struct.get_key())
                if key in ['*class', '*c']:
                    self._load_class(raw_struct)
                    continue
                elif key in ['*method', '*m']:
                    self._load_variable_method(raw_struct)
                elif key == '?':
                    self._load_config_numbered_vars(raw_struct.get_value())
            if isinstance(raw_struct, Pair) and raw_struct.key.get_value().startswith('_'):
                self._load_config_var(raw_struct.key.get_value()[1:], raw_struct)
            if isinstance(raw_struct, Pair) and raw_struct.key.get_value().startswith('*'):
                raise UnrecognisedInstruction()

            structures: List[Structure] = self._interpret_raw_struct(modl_obj, raw_struct)
            modl_obj.add_structures(structures)

        return modl_obj

    def _load_class_o(self):
        # TODO Get this to work for including more files during the load. Anything to do?
        o = {}
        superclass = String('map')
        o['*superclass'] = superclass

        name = String('o')
        o['*name'] = name

        output = String('map')
        o['*output'] = output

        self.classes['o'] = o


    def _interpret_raw_struct(self, modl_obj, raw_struct):
        if raw_struct is None:
            return None

        structures = []

        if not isinstance(raw_struct, TopLevelConditional):  # TODO: not sure we're doing correct comparison here
            if raw_struct.is_map():
                struct = self._interpret_map(modl_obj, raw_struct)
                if struct:
                    structures.append(struct)

            if raw_struct.is_array():
                struct = self._interpret_array(modl_obj, raw_struct)
                if struct:
                    structures.append(struct)

            if raw_struct.is_pair():
                pair: Pair = self._interpret_pair(modl_obj, raw_struct)
                if pair and pair.get_key():
                    key = pair.get_key().get_value()
                    if not (key.startswith('_') or key.startswith('*') or key.startswith('?')):
                        structures.append(pair)

        return structures

    def _interpret_map(self, modl_obj, orig_map: Map, parent_pair=None):
        if orig_map is None:
            return None

        map_obj = Map()

        if orig_map.get_modl_values() is not None:
            for orig_pair in orig_map.get_modl_values():
                pairs = self._interpret_map_pair(modl_obj, orig_pair, parent_pair)
                if pairs is not None:
                    for pair in pairs:
                        key = pair.get_key().get_value()
                        if not (key.startswith('_') or key.startswith('*') or key.startswith('?')):
                            map_obj.add(pair)

        return map_obj

    def _interpret_map_pair(self, modl_obj, orig_pair, parent_pair):
        if orig_pair is None:
            return None

        pairs = []
        if isinstance(orig_pair, parser.MapConditional):  # TODO: correct type?
            # evaluate the conditional
            pairs = self._interpret_value_conditional(modl_obj, orig_pair, parent_pair)
        pair = self._interpret_pair(modl_obj, orig_pair, parent_pair)
        if pair:
            if not str(pair.get_key().get_value()).startswith('_'):
                pairs.append(pair)

        return pairs

    def _interpret_array(self, modl_obj, raw_array: Array, parent_pair: Pair=None):
        if raw_array is None:
            return None

        array = Array()

        if raw_array.get_modl_values() is not None:
            for orig_array_item in raw_array.get_modl_values():
                value: ModlValue = self._interpret_something(modl_obj, orig_array_item, parent_pair)
                if value is not None:
                    array.add(value)
                    if parent_pair is not None:
                        parent_pair.add_modl_value(value)
        return array

    def _interpret_something(self, modl_obj, raw_value: ModlValue, parent_pair=None):
        """TODO: what is this doing? Better name required!"""
        if raw_value is None:
            return None

        if isinstance(raw_value, ValueConditional):
            return self._interpret_value_conditional(modl_obj, raw_value, parent_pair)
        if not isinstance(raw_value, Array):
            return self._interpret_value(modl_obj, raw_value, parent_pair)

        array = Array()
        for vi in raw_value.get_modl_values():
            array.add(self._interpret_something(modl_obj, vi, parent_pair))
            
        return array

    def _interpret_number(self, modl_obj: ModlObject, orig_num: Number):
        """Why?"""
        if orig_num is None:
            return None
        return Number(orig_num.get_value())

    def _interpret_true(self, true_val: TrueVal):
        if true_val:
            return TrueVal()
        return None

    def _interpret_false(self, false_val: FalseVal):
        if false_val:
            return FalseVal()
        return None

    def _interpret_null(self, null_val: NullVal):
        if null_val:
            return NullVal()
        return None

    def _interpret_string(self, string_val: String):
        if string_val:
            return self._transform_string(str(string_val))
        return None

    def _interpret_pair(self, modl_obj: ModlObject, raw_pair: Pair,
                        parent_pair: Pair = None, add_to_value_pairs=False) -> Union[Pair,None]:
        if raw_pair is None:
            return None

        key = raw_pair.get_key().get_value()
        if key == '?':
            # self._load_config_numbered_vars(raw_pair.get_value())
            return None

        pair: Pair = Pair()

        if not raw_pair.get_key():
            return None

        orig_key: str = str(raw_pair.get_key())
        new_key: str = orig_key

        if self._have_modl_class(orig_key):
            new_key = self._transform_key(orig_key)
            raw_pair = self._transform_value(raw_pair)

        # IF WE ALREADY HAVE A PAIR WITH THIS NAME, AND THE NAME IS UPPER-CASE, THEN RAISE AN ERROR
        if new_key:
            if new_key.upper() == new_key and add_to_value_pairs:
                raise ValueError(f'{new_key} cannot be redefined as upper-case keys are immutable')

        if new_key and ('_'+new_key) not in self.pair_names:
            if parent_pair is None and (not new_key.startswith('%')) and add_to_value_pairs:
                self.pair_names.add(new_key)
            self._transform_pair_key(modl_obj, raw_pair, new_key, parent_pair)

        # TODO: factor out is_directive(...) or whatever
        if new_key and (new_key.startswith('_') or new_key.startswith('*') or new_key.startswith('?')):
            return None

        # A pair with a key that matches a class ID or class name is transformed according to the class definition:
        # TODO Should be able to look up by transformed name too?
        if self._have_modl_class(orig_key):
            # The key of the pair is set to the class name.
            # The value of the original standard pair is given the key value in the new map pair
            if self._generate_modl_class_object(modl_obj, raw_pair, pair, orig_key, new_key, parent_pair):
                return pair  # TODO in all cases?

        pair.key = String(new_key)

        if isinstance(raw_pair.get_value(), Array):
            for value in raw_pair.get_value().get_modl_values():
                self.add_value_from_pair(modl_obj, raw_pair, parent_pair, pair, value)
        else:
            self.add_value_from_pair(modl_obj, raw_pair, parent_pair, pair, raw_pair.get_value())

        return pair

    def _load_config_numbered_vars(self, modl_value: ModlValue):
        if modl_value is None:
            return

        if isinstance(modl_value, Array):
            for val in modl_value.get_modl_values():
                self.add_config_numbered_var(val)
        else:
            self.add_config_numbered_var(modl_value)

    def _have_modl_class(self, orig_key):
        return self._get_modl_class(orig_key) is not None

    def _get_modl_class(self, key: str) -> dict:
        for class_key, class_details in self.classes.items():
            for ck, cv in class_details.items():
                if ck in ['*name', '*n', '*id', '*i']:
                    if isinstance(cv, str) and cv == key:
                        return class_details
                    elif isinstance(cv, String) and cv.get_value() == key:
                        return class_details
        return self.classes.get(key, None)

    def _transform_key(self, orig_key):
        modl_class = self._get_modl_class(orig_key)
        if modl_class:
            if '*name' in modl_class:
                return str(modl_class['*name'])
            if '*n' in modl_class:
                return str(modl_class['*n'])
        return orig_key

    def _transform_value(self, raw_pair):
        # TODO
        return raw_pair

    def _transform_pair_key(self, raw_modl_obj, orig_pair, new_key, parent_pair):
        transformed_key = new_key
        if transformed_key.startswith('_'):
            transformed_key = transformed_key[1:]
        if not parent_pair:
            if new_key.startswith('_'):
                if orig_pair.get_value().is_map():
                    orig_pair.key = String(transformed_key)
                    new_map = {}
                    self._interpret_map(raw_modl_obj, orig_pair.get_value(), new_map)
                if orig_pair.get_value().is_array():
                    orig_pair.key = String(transformed_key)
                    new_list = []
                    self._interpret_array(raw_modl_obj, orig_pair.get_value(), new_list)
            if orig_pair.get_value().is_string():
                self.value_pairs[transformed_key] = self._transform_string(str(orig_pair.get_value()))
            else:
                self.value_pairs[transformed_key] = orig_pair.get_value()
        else:
            # We have a new definition which must live under an existing mapPair or arrayPair
            if type(parent_pair) == dict:
                string = self._get_string_from_value(orig_pair)
                parent_pair[transformed_key] = string
            elif type(parent_pair) == list:
                string = self._get_string_from_value(orig_pair)
                parent_pair.append(string)
            else:
                raise ValueError('Expecting dict or list as parent_pair!')


    def _get_string_from_value(self, pair: Pair):
        string = None
        v: ModlValue = pair.get_value()
        if isinstance(v, Array):
            v = v.get_by_index(0)
        if isinstance(v, String):
            string = str(v)
        if isinstance(v, Number):
            string = str(v.get_value())
        return string

    def _generate_modl_class_object(self,
                                    modl_obj: ModlObject,
                                    raw_pair,
                                    pair: Pair,
                                    orig_key: str,
                                    new_key: str,
                                    parent_pair
                                    ) -> bool:
        pair.key = String(new_key)
        num_params = 0
        # if raw_pair.get_value():
        #     if isinstance(raw_pair.get_value(), Map):
        #         pass
        #     elif isinstance(raw_pair.get_value(), Array):
        #         num_params = len(raw_pair.get_value().get_modl_values())
        #     else:
        #         num_params = 1
        num_params = self._get_num_params(raw_pair, num_params)
        params_key_str: str = '*params' + str(num_params)
        obj = self._get_modl_class(str(raw_pair.get_key())).get(params_key_str, None)
        has_params = obj is not None

        # If it's not already a map pair, and one of the parent classes in the class hierarchy includes pairs, then it is transformed to a map pair.
        if self._any_class_contains_pairs(orig_key) or self._map_pair_already(raw_pair) or has_params:
            pair.key = String(new_key)  # TODO: Do we need to do this again here?!
            pairs = None
            was_array = False

            if isinstance(raw_pair.get_value(), Array):
                # TODO They are not necessarily pairs!!!
                # TODO But they will _become_ pairs when paired up with the ModlClass
                try:
                    pairs = self._get_pairs_from_array(modl_obj, raw_pair.get_value(), parent_pair)
                    if len(pairs) > 0:
                        was_array = True
                    else:
                        pairs = None
                except:
                    was_array = False

            if self._map_pair_already(raw_pair):
                pairs = []
                self._add_map_items_to_pair(modl_obj, raw_pair.get_value().get_modl_values(), pairs, parent_pair)

            if pairs is not None:
                # Make all the new map values in the new map pair
                self._make_new_map_pair(modl_obj, pair, pairs, was_array, parent_pair)

            # TODO.... carry on.... lots more to implement in this method - see Java
            #...

    def add_value_from_pair(self, modl_obj, raw_pair, parent_pair, pair, value):
        # Is this a variable prefixed by "%"?
        if isinstance(value, Pair) and str(value.get_key()).startswith('%'):
            key = str(value.get_key())
            # If so, then look up the reference!!
            new_value: ModlValue = None
            if key.replace('%', '_', 1) in self.pair_names:
                stored_value: ModlValue = self.value_pairs.get(key.replace('%', '', 1))
                if stored_value.is_map():
                    new_value = Pair(String('obsolete'), stored_value)
                elif stored_value.is_array():
                    values: List[ModlValue] = stored_value.get_modl_values()
                    index = None
                    if value.get_value().is_number():
                        index = int(value.get_value())
                    else:
                        index = int(value.get_value().get_by_index(0))
                    new_value = values[index]
            else:
                new_value = self._transform_string(str(value.get_key()))
            # Now go through the object reference for value.get_value() until we are at the end of it!
            new_value = self._run_deep_ref(value, new_value)
            pair.add_modl_value(new_value)
        else:
            pair.add_modl_value(self._interpret_something(modl_obj, value, parent_pair))

    def _load_config_file(self, location):
        # We no longer keep configs around - they can be built up dynamically for each new record that comes in
        # Load the config file!
        value = self._transform_string(location)
        if isinstance(value, String):
            location = str(value.get_value())
        else:
            raise ValueError('Expected String for location, but got ' + str(type(value)))

        raw_modl_object = self._load_file(location)
        return raw_modl_object

    def _load_file(self, location):
        """
        TODO: this is temporary, see Java FileLoader implementation for proper code
        """

        if not (location.endswith('.modl') or location.endswith('.txt')):
            location = location + '.modl'

        with open(location, 'r') as config:
            config_text = config.readlines()

        logging.debug('Loading:', location)
        logging.debug('Config:', config_text)

        modl_parsed = parser.parse(config_text)
        raw_modl_object = process_modl_parsed(modl_parsed)

        return raw_modl_object

    def _transform_string(self, input: str):
        transformer = StringTransformer(self.value_pairs, self.variables, self.numbered_variables)
        return transformer.transform(input)

    def add_config_numbered_var(self, modl_value):
        var_num = len(self.numbered_variables)
        self.numbered_variables[var_num] = modl_value
        return var_num

    def _load_class(self, structure):
        if isinstance(structure, Pair):
            key = structure.get_key()
            if not (key == '*class' or key == '*c'):
                raise ValueError('Expected *class in class loader')
            self._load_class_structure(structure)

    def _load_class_structure(self, structure):
        # Load in the new klass
        values = {}
        id = self._get_pair_value_for(structure, '*id')
        if id is None:
            id = self._get_pair_value_for(structure, '*i')
        if id is None:
            raise ValueError("Can't find *id in *class")
        self.classes[id] = values
        superclass = self._get_pair_value_for(structure, '*superclass')
        if superclass is None:
            superclass = self._get_pair_value_for(structure, '*s')
        values['*superclass'] = superclass
        name = self._get_pair_value_for(structure, '*name')
        if name is None:
            name = self._get_pair_value_for(structure, '*n')
        if name is None:
            name = id
        values['*name'] = name  # TODO???
        # Remember to see if there is a superclass - if so, then copy all its values in first
        if superclass is not None:
            if superclass.upper() == superclass:
                raise ValueError("Can't derive from " + superclass + ", as it in upper case and therefore fixed")
        superklass: dict = self.classes.get(superclass, None)
        if superklass is not None:
            for key, value in superklass.items():
                values[key] = value

        # Go through the structure and find all the new values and add them (replacing any already there from superklass)
        #...

    def _get_pair_value_for(self, structure: Structure, pair_value: str) -> Union[str, None]:
        for map_item in structure.get_value().get_modl_values():
            if map_item.get_key().get_value() == pair_value:
                # TODO This does not need to be a String!
                return map_item.get_value().get_value()
        return None

    def _load_variable_method(self, raw_struct):
        pass

    def _load_config_var(self, param, raw_struct):
        pass

    def _run_deep_ref(self, value, new_value):
        # TODO
        pass

    def _interpret_value_conditional(self, modl_obj, raw_value, parent_pair):
        raise NotImplemented('_interpret_value_conditional not implemented')

    def _interpret_value(self, modl_obj, raw_value, parent_pair):
        if raw_value is None:
            return None

        if raw_value.is_pair():
            return self._interpret_pair(modl_obj, raw_value, parent_pair)

        if raw_value.is_map():
            return self._interpret_map(modl_obj, raw_value, parent_pair)

        if raw_value.is_array():
            return self._interpret_array(modl_obj, raw_value, parent_pair)

        if raw_value.is_number():
            return self._interpret_number(modl_obj, raw_value)

        if raw_value.is_true():
            return self._interpret_true(raw_value)

        if raw_value.is_false():
            return self._interpret_false(raw_value)

        if raw_value.is_null():
            return self._interpret_null(raw_value)

        if raw_value.is_string():
            return self._interpret_string(raw_value)

    def _get_num_params(self, raw_pair, num_params):
        if isinstance(raw_pair.get_value(), Map):
            map_pair: Map = raw_pair
            num_params = len(map_pair.get_modl_values())
        elif isinstance(raw_pair.get_value(), Array):
            array_pair: Array = raw_pair
            num_params = len(array_pair.get_modl_values())
        elif raw_pair.get_value() is not None:
            num_params = 1

        return num_params

    def _any_class_contains_pairs(self, orig_key: str) -> bool:
        # If this class, or any of its parent classes, define any pairs, then return true
        # A pair is defined in a class if it has a pair whose key does not start in "_"
        cls = self._get_modl_class(orig_key)
        for key in cls.keys():
            if not (key.startswith('_') or key.startswith('*') or key == '?'):
                return True
        return False


    def _map_pair_already(self, orig_pair):
        return isinstance(orig_pair.get_value(), Map)

    def _get_pairs_from_array(self, modl_obj: ModlObject, array: Array, parent_pair):
        return self._get_pairs_from_list(modl_obj, array.get_modl_values(), parent_pair)

    def _get_pairs_from_list(self, modl_obj: ModlObject, array_items: List[ModlValue], parent_pair) -> List[Pair]:
        pairs = []
        if array_items is not None:
            for array_item in array_items:
                if isinstance(array_item, parser.ArrayConditional):
                    new_array_items = self._interpret_array_conditional(modl_obj, array_item, parent_pair)
                    for v in new_array_items:
                        if isinstance(v, Pair):
                            pairs.append(v)
                elif isinstance(array_item, Pair):
                    pairs.append(self._interpret_pair(modl_obj, array_item, parent_pair))
        return pairs
    
    def _interpret_array_conditional(self, modl_obj, array_item, parent_pair):
        raise NotImplementedError('_interpret_array_conditional not implemented yet')

    def _add_map_items_to_pair(self, modl_obj: ModlObject, map_items: List[Pair], pairs: List[Pair], parent_pair):
        if map_items is None:
            return

        for map_item in map_items:
            if isinstance(map_item, MapConditional):
                # handle conditionals
                new_pairs = self._interpret_map_conditional(modl_obj, map_item, parent_pair)
                for pair in new_pairs:
                    pairs.append(pair)
            elif map_item is not None:
                pairs.append(self._interpret_pair(modl_obj, map_item, parent_pair))

    def _interpret_map_conditional(self, modl_obj, map_item, parent_pair):
        raise NotImplementedError('_interpret_map_conditional not yet implemented')













