import json
from typing import Sized

from interpreter import ModlObject
from modl_creator import Structure, Map, ModlValue, Pair, Array


class MODLJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == Structure:
            return self.transform_structure(o)
        if type(o) == ModlValue:
            return self.transform_value(o)
        # if type(o) == ValueItem:
        #     return o.get_value()
        # if type(o) == ArrayValueItem:
        #     return o.get_value()
        if type(o) == Array:
            return o.to_list()
        # if type(o) == ArrayItem:
        #     return o.get_item()
        if type(o) == Pair:
            return self.encode_pair(o)
        if type(o) == Map:
            return self.encode_map(o)
        else:
            return json.JSONEncoder.default(self, o)

    def transform_value(self, value: ModlValue):
        return value.get_value()

    def encode_map(self, value: Map):
        return {key: value.get_by_name(key) for key in value.get_keys()}

    def transform_structure(self, struct: Structure):
        if struct.is_pair():
            return {key: struct.get_by_name(key) for key in struct.get_keys()}

    def encode_pair(self, o: Pair):
        return {o.get_key(): o.get_value()}


def to_json(modl: ModlObject) -> str:
    # TODO: temporary use of original ModlParsed object - replace with direct usage of ModlObject
    structures = modl.structures
    # TODO: sort out this horrible, horrible block that shouldn't be here
    if len(structures) == 1:
        if isinstance(structures, Sized) and len(structures[0]) == 1:
            data = structures[0][0]  # TODO: we shouldn't have this level of nesting. Why list in a list?
        else:
            data = structures[0]
        # data = structures[0]
    else:
        data = structures
    return json.dumps(data, cls=MODLJSONEncoder)
