from typing import List

from generated.MODLParserListener import MODLParserListener
from generated.MODLLexer import MODLLexer, CommonTokenStream, ParseTreeWalker
from generated.MODLParser import MODLParser
from antlr4 import InputStream


class ModlObjectListener(MODLParserListener):
    def __init__(self):
        self.modl = ModlObject()

    def enterModl(self, ctx:MODLParser.ModlContext):
        text = ctx.getText()
        print(f"Entered MODL: {text}")

        for struct in ctx.modl_structure():
            structure = Structure()
            struct.enterRule(structure)
            self.modl.append(structure)

    def exitModl(self, ctx:MODLParser.ModlContext):
        print("MODL has left the building.")

    def modl_object(self):
        return self.modl


class ModlObject:
    def __init__(self):
        self.structures: List[Structure] = []

    def append(self, structure):
        self.structures.append(structure)


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
            try:
                self.number = int(ctx.NUMBER().getText())
            except ValueError:
                self.number = float(ctx.NUMBER().getText())

        if ctx.QUOTED():
            self.quoted = ctx.QUOTED().getText()[1:-1] # strip quotes
        if ctx.TRUE():
            self.is_true = True
        if ctx.FALSE():
            self.is_false = True
        if ctx.NULL():
            self.is_null = True


def parse(input_stream) -> ModlObject:
    # Wrap the input in an InputStream if it's just a string
    if type(input_stream) == str:
        input_stream = InputStream(input_stream)
    lexer = MODLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = MODLParser(stream)
    tree = parser.modl()
    walker = ParseTreeWalker()
    listener = ModlObjectListener()
    walker.walk(listener, tree)
    return listener.modl_object()