from modl_creator import RawModlObject, ModlObject


class ModlInterpreter:
    """Process the RawModlObject and produce a ModlObject.
    The ModlObject is the finished article."""

    def __init__(self):
        self.indexed_strings = None

    def execute(self, raw_modl: RawModlObject) -> ModlObject:
        # for k in raw_modl.structures:
        #     if k.pair:
        #         if k.pair.key == '?':
        #             print(f'Found indexed objects {k.pair.value_item.value.get_value()}')
        return raw_modl

