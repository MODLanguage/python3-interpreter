import json

from interpreter import ModlObject
from parser import Structure, Value, ValueItem, Map, Array, ArrayValueItem, ArrayItem


class MODLJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == Structure:
            return self.transform_structure(o)
        if type(o) == Value:
            return self.transform_value(o)
        if type(o) == ValueItem:
            return o.get_value()
        if type(o) == ArrayValueItem:
            return o.get_value()
        if type(o) == Array:
            return o.to_list()
        if type(o) == ArrayItem:
            return o.get_item()
        if type(o) == Map:
            return self.encode_map(o)
        else:
            return json.JSONEncoder.default(self, o)

    def transform_value(self, value: Value):
        return value.get_value()

    def encode_map(self, value: Map):
        return value.to_dict()

    def transform_structure(self, struct: Structure):
        if struct.pair:
            return {struct.pair.get_key(): struct.pair.get_value()}


def to_json(modl: ModlObject) -> str:
    # TODO: temporary use of original ModlParsed object - replace with direct usage of ModlObject
    structures = modl.raw_modl.modl_parsed.structures
    if len(structures) == 1:
        data = structures[0]
    else:
        data = structures
    return json.dumps(data, cls=MODLJSONEncoder)
