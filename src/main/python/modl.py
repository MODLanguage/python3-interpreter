from antlr4 import InputStream

import printer
from generated.MODLLexer import MODLLexer, CommonTokenStream, ParseTreeWalker
from generated.MODLParser import MODLParser
from parser import ModlObject, ModlObjectListener


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


def to_json(input_stream) -> str:
    parsed_modl = parse(input_stream)
    # interpreted = ....
    return printer.to_json(parsed_modl)

