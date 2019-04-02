import json
from parser import Structure, ModlObject


class MODLJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == Structure:
            return self.encode_structure(o)
        else:
            return json.JSONEncoder.default(self, o)

    def encode_structure(self, struct: Structure):
        if struct.pair and struct.pair.value_item:
            value = None
            pair = struct.pair
            if pair.value_item.value.string:
                value = pair.value_item.value.string
            if pair.value_item.value.number:
                value = pair.value_item.value.number
            if pair.value_item.value.quoted:
                value = pair.value_item.value.quoted
            if pair.value_item.value.is_true:
                value = True
            if pair.value_item.value.is_false:
                value = False
            if pair.value_item.value.is_null:
                value = None
            return {pair.key: value}


def to_json(modl: ModlObject) -> str:
    structures = modl.structures
    if len(structures) == 1:
        data = structures[0]
    else:
        data = structures
    return json.dumps(data, cls=MODLJSONEncoder)
