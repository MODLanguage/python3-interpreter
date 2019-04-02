import parser
import printer


def to_json(input_stream) -> str:
    parsed_modl = parser.parse(input_stream)
    # interpreted = ....
    # return printer.to_json(interpreted)
    return printer.to_json(parsed_modl)

