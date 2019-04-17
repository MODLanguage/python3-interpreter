from modl_creator import RawModlObject


class ModlObject:
    """Represents the final, interpreted MODL tree. This may for example
    be transformed into another format such as JSON."""
    def __init__(self, raw_modl: RawModlObject):
        self.raw_modl = raw_modl


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
        return ModlObject(raw_modl)

