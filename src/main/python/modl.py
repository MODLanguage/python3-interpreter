import json
from typing import List

from antlr4 import *
from generated.MODLLexer import MODLLexer
from generated.MODLParser import MODLParser
from generated.MODLParserListener import MODLParserListener


class JSONFormatter(MODLParserListener):
    def __init__(self):
        self.structures: List[Structure] = []

    def to_json(self) -> str:
        if len(self.structures) == 1:
            data = self.structures[0]
        else:
            data = self.structures
        return json.dumps(data, cls=MODLJSONEncoder)

    def enterModl(self, ctx:MODLParser.ModlContext):
        text = ctx.getText()
        print(f"Entered MODL: {text}")

        for struct in ctx.modl_structure():
            structure = Structure()
            struct.enterRule(structure)
            self.structures.append(structure)

    def exitModl(self, ctx:MODLParser.ModlContext):
        print("MODL has left the building.")


class Structure(MODLParserListener):
    def __init__(self):
        self.pair = None

    def enterModl_structure(self, ctx:MODLParser.Modl_structureContext):
        print("Enter MODL Structure", ctx.getText())
        if ctx.modl_pair():
            self.pair = Pair()
            ctx.modl_pair().enterRule(self.pair)


class Pair(MODLParserListener):
    def __init__(self):
        self.key = ''
        self.value_item = None

    def enterModl_pair(self, ctx:MODLParser.Modl_pairContext):
        if ctx.STRING():
            self.key = ctx.STRING().getText()
        elif ctx.QUOTED():
            self.key = ctx.QUOTED().getText()[1:-1] # strip quotes

        if ctx.modl_value_item():
            self.value_item = ValueItem()
            ctx.modl_value_item().enterRule(self.value_item)


class ValueItem(MODLParserListener):
    def __init__(self):
        self.value = None

    def enterModl_value_item(self, ctx:MODLParser.Modl_value_itemContext):
        if ctx.modl_value():
            self.value = Value()
            ctx.modl_value().enterRule(self.value)


class Value(MODLParserListener):
    def __init__(self):
        self.string = None
        self.number = None
        self.quoted = None
        self.is_true = False
        self.is_false = False
        self.is_null = False

    def enterModl_value(self, ctx:MODLParser.Modl_valueContext):
        if ctx.STRING():
            self.string = ctx.STRING().getText()
        if ctx.NUMBER():
            self.number = int(ctx.NUMBER().getText())
        if ctx.QUOTED():
            self.quoted = ctx.QUOTED().getText()[1:-1] # strip quotes
        if ctx.TRUE():
            self.is_true = True
        if ctx.FALSE():
            self.is_false = True
        if ctx.NULL():
            self.is_null = True



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



def to_json(input_stream) -> str:
    # Wrap the input in an InputStream if it's just a string
    if type(input_stream) == str:
        input_stream = InputStream(input_stream)
    lexer = MODLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = MODLParser(stream)
    tree = parser.modl()
    walker = ParseTreeWalker()
    listener = JSONFormatter()
    walker.walk(listener, tree)
    return listener.to_json()
