from parser import ModlObject

class ModlInterpreter:
    """Process the RawModlObject and produce a ModlObject.
    The ModlObject is the finished article."""

    def __init__(self):
        self.indexed_strings = None

    def interpret(self, rawModl: ModlObject) -> ModlObject:
        # for k in rawModl.structures:
        #     if k.pair:
        #         if k.pair.key == '?':
        #             print(f'Found indexed objects {k.pair.value_item.value.get_value()}')
        return rawModl

