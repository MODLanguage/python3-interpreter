import parser
import printer
from interpreter import ModlObject, ModlInterpreter
from modl_creator import process_modl_parsed


def to_json(input_stream) -> str:
    """High level API: parses, process, interprets and outputs MODL as JSON.
    This is generally the only method that a client will need to use."""
    modl_object = interpret(input_stream)
    return printer.to_json(modl_object)


def interpret(input_stream) -> ModlObject:
    """High level API: parses, processes and interprets the MODL input"""
    modl_parsed = parser.parse(input_stream)
    raw_modl_object = process_modl_parsed(modl_parsed)
    interpreter = ModlInterpreter()
    return interpreter.execute(raw_modl_object)


