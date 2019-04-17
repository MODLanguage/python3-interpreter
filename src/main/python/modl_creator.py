from parser import ModlParsed


class RawModlObject:
    def __init__(self, modl_parsed: ModlParsed):
        self.modl_parsed = modl_parsed


def process_modl_parsed(parsed: ModlParsed) -> RawModlObject:
    """Post-process the parsed tree, transforming it into an object ready for interpreting"""
    # TODO
    return RawModlObject(parsed)
