import parser
import printer
import interpreter
from modl_creator import ModlObject, process_modl_parsed
import logging


logging.basicConfig(level=logging.DEBUG)
MODL_VERSION = 1


def to_json(input_stream) -> str:
    """High level API: parses, process, interprets and outputs MODL as JSON.
    This is generally the only method that a client will need to use."""
    modl_object = interpret(input_stream)
    return printer.to_json(modl_object)


def interpret(input_stream) -> ModlObject:
    """High level API: parses, processes and interprets the MODL input"""
    modl_parsed = parser.parse(input_stream)
    raw_modl_object = process_modl_parsed(modl_parsed)
    return interpreter.interpret(raw_modl_object)


