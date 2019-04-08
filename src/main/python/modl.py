import parser
import printer
from interpreter import ModlInterpreter


def to_json(input_stream) -> str:
    parsed = parser.parse(input_stream)
    interpreted = ModlInterpreter().interpret(parsed)
    return printer.to_json(interpreted)

