import json
from antlr4 import *
from generated.MODLLexer import MODLLexer
from generated.MODLParser import MODLParser
from generated.MODLParserListener import MODLParserListener


class JSONFormatter(MODLParserListener):
    def __init__(self):
        self.json_obj = {}

    def to_json(self) -> str:
        return json.dumps(self.json_obj)

    def enterModl(self, ctx:MODLParser.ModlContext):
        text = ctx.getText()
        print(f"Entered MODL: {text}")

    def enterModl_pair(self, ctx:MODLParser.Modl_pairContext):
        self.name = str(ctx.STRING())

    def enterModl_value(self, ctx:MODLParser.Modl_valueContext):
        if ctx.NUMBER():
            value = int(ctx.NUMBER().getText())
        elif ctx.STRING():
            value = ctx.STRING().getText()
        elif ctx.QUOTED():
            value = ctx.QUOTED().getText()[1:-1] # strip quotes
        else:
            value = None
        self.json_obj = {self.name: value}

    def exitModl(self, ctx:MODLParser.ModlContext):
        print("MODL has left the building.")


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
