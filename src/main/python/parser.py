from typing import List

from antlr4.tree.Tree import TerminalNodeImpl

from generated.MODLParserListener import MODLParserListener
from generated.MODLLexer import MODLLexer, CommonTokenStream, ParseTreeWalker
from generated.MODLParser import MODLParser, TerminalNode
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
        self.pair: Pair = None
        self.array: Array = None
        self.top_level_conditional: TopLevelConditional = None
        self.map: Map = None

    def enterModl_structure(self, ctx:MODLParser.Modl_structureContext):
        print("Enter MODL Structure", ctx.getText())
        if ctx.modl_pair():
            self.pair = Pair()
            ctx.modl_pair().enterRule(self.pair)
        elif ctx.modl_array():
            self.array = Array()
            ctx.modl_array().enterRule(self.array)
        elif ctx.modl_top_level_conditional():
            self.top_level_conditional = TopLevelConditional()
            ctx.modl_top_level_conditional().enterRule(self.top_level_conditional)
        elif ctx.modl_map():
            self.map = Map()
            ctx.modl_map().enterRule(self.map)


class Map(MODLParserListener):
    def __init__(self):
        self.map_items: List[MapItem] = None

    def enterModl_map(self, ctx:MODLParser.Modl_mapContext):
        if ctx.modl_map_item():
            self.map_items = []
            for item_ctx in ctx.modl_map_item():
                map_item = MapItem()
                item_ctx.enterRule(map_item)
                self.map_items.append(map_item)


class MapItem(MODLParserListener):
    def __init__(self):
        self.pair = None
        self.map_conditional = None

    def enterModl_map_item(self, ctx:MODLParser.Modl_map_itemContext):
        if ctx.modl_pair():
            self.pair = Pair()
            ctx.modl_pair().enterRule(self.pair)
        if ctx.modl_map_conditional():
            self.map_conditional = MapConditional()
            ctx.modl_map_conditional().enterRule(self.map_conditional)


class MapConditional(MODLParserListener):
    pass # TODO


class TopLevelConditional(MODLParserListener):
    pass # TODO



class AbstractArrayItem():
    pass # TODO


class ArrayItem(MODLParserListener,AbstractArrayItem):
    def __init__(self):
        self.array_value_item: ArrayValueItem = None
        self.array_conditional: ArrayConditional = None

    def enterModl_array_item(self, ctx:MODLParser.Modl_array_itemContext):
        if ctx.modl_array_conditional():
            self.array_conditional = ArrayConditional()
            ctx.modl_array_conditional().enterRule(self.array_conditional)
        if ctx.modl_array_value_item():
            self.array_value_item = ArrayValueItem()
            ctx.modl_array_value_item().enterRule(self.array_value_item)


# TODO: can we factor out this stuff? common with Value (minus the NbArray)?
class ArrayValueItem(MODLParserListener):
    def __init__(self):
        self.map = None
        self.array = None
        self.pair = None
        self.quoted = None
        self.number = None
        self.is_true = None
        self.is_false = None
        self.is_null = None
        self.string = None

    def enterModl_array_value_item(self, ctx:MODLParser.Modl_array_value_itemContext):
        if ctx.modl_map():
            self.map = Map()
            ctx.modl_map().enterRule(self.map)
        if ctx.modl_array():
            self.array = Array()
            ctx.modl_array().enterRule(self.array)
        if ctx.modl_pair():
            self.pair = Pair()
            ctx.modl_pair().enterRule(self.pair)
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
        # Ignoring comments


class ArrayConditional():
    pass # TODO


def handle_empty_array_item() -> ArrayItem:
    """Create something for the blank array item

    The problem is that we might not have any context to tell us what type we need to create
    so this currently defaults to the null value

    TODO: Is there a way to know the type to create or is Null always acceptable?
    :return:  ArrayItem
    """
    array_item = ArrayItem()
    array_item.array_value_item = ArrayValueItem()
    array_item.array_value_item.is_null = True
    return array_item


class NbArray(MODLParserListener):
    def __init__(self):
        self.array_items: List[ArrayItem] = None

    def enterModl_nb_array(self, ctx:MODLParser.Modl_nb_arrayContext):
        self.array_items = []
        prev = None
        for pt in ctx.children:
            if type(pt) == MODLParser.Modl_array_itemContext:
                array_item = ArrayItem()
                pt.enterRule(array_item)
                self.array_items.append(array_item)
            # elif type(pt) == MODLParser.Modl_nb_arrayContext:
            #     nb_array = NbArray()
            #     pt.enterRule(nb_array)
            #     self.array_items.append(nb_array)
            elif type(pt) == TerminalNodeImpl and type(prev) == TerminalNodeImpl:
                    # If we get here then we have two terminal nodes in a row, so we need to output something unless
                    # the terminal symbols are newlines
                    prev_symbol = prev.getSymbol().type
                    curr_symbol = pt.getSymbol().type

                    # if prev_symbol == MODLLexer.LSBRAC and curr_symbol == MODLLexer.RSBRAC:
                    #     continue  # This allows empty arrays

                    if prev_symbol != MODLLexer.NEWLINE and curr_symbol != MODLLexer.NEWLINE:
                        # Create something for the blank array item
                        #
                        # The problem is that we might not have any context to tell us what type we need to create
                        # so this currently defaults to the null
                        #
                        # TODO: Is there a way to know the type to create or is Null always acceptable?
                        array_item = handle_empty_array_item()
                        self.array_items.append(array_item)
            prev = pt


class Array(MODLParserListener):
    def __init__(self):
        self.array_items: List[AbstractArrayItem] = None

    def enterModl_array(self, ctx: MODLParser.Modl_arrayContext):
        self.array_items = []
        prev = None
        for pt in ctx.children:
            if type(pt) == MODLParser.Modl_array_itemContext:
                array_item = ArrayItem()
                pt.enterRule(array_item)
                self.array_items.append(array_item)
            elif type(pt) == MODLParser.Modl_nb_arrayContext:
                nb_array = NbArray()
                pt.enterRule(nb_array)
                self.array_items.append(nb_array)
            elif type(pt) == TerminalNodeImpl and type(prev) == TerminalNodeImpl:
                    # If we get here then we have two terminal nodes in a row, so we need to output something unless
                    # the terminal symbols are newlines
                    prev_symbol = prev.getSymbol().type
                    curr_symbol = pt.getSymbol().type

                    if prev_symbol == MODLLexer.LSBRAC and curr_symbol == MODLLexer.RSBRAC:
                        continue  # This allows empty arrays

                    if prev_symbol != MODLLexer.NEWLINE and curr_symbol != MODLLexer.NEWLINE:
                        # Create something for the blank array item
                        #
                        # The problem is that we might not have any context to tell us what type we need to create
                        # so this currently defaults to the null
                        #
                        # TODO: Is there a way to know the type to create or is Null always acceptable?
                        array_item = handle_empty_array_item()
                        self.array_items.append(array_item)
            prev = pt


class Pair(MODLParserListener):
    def __init__(self):
        self.key: str = None
        self.map: Map = None
        self.array: Array = None
        self.value_item: ValueItem = None

    def enterModl_pair(self, ctx:MODLParser.Modl_pairContext):
        if ctx.STRING():
            self.key = ctx.STRING().getText()
        if ctx.QUOTED():
            self.key = ctx.QUOTED().getText()[1:-1] # strip quotes

        if ctx.modl_array():
            self.array = Array()
            ctx.modl_array().enterRule(self.array)
        if ctx.modl_map():
            self.map = Map()
            ctx.modl_map().enterRule(self.map)
        if ctx.modl_value_item():
            self.value_item = ValueItem()
            ctx.modl_value_item().enterRule(self.value_item)


class ValueItem(MODLParserListener):
    def __init__(self):
        self.value = None
        self.value_conditional = None

    def enterModl_value_item(self, ctx:MODLParser.Modl_value_itemContext):
        if ctx.modl_value():
            self.value = Value()
            ctx.modl_value().enterRule(self.value)
        if ctx.modl_value_conditional():
            self.value_conditional = ValueConditional()
            ctx.modl_value_conditional().enterRule(self.value_conditional)


class ValueConditional(MODLParserListener):
    pass


class Value(MODLParserListener):
    def __init__(self):
        super().__init__()
        self.map = None
        self.array = None
        self.nb_array = None
        self.pair = None
        self.string = None
        self.number = None
        self.quoted = None
        self.is_true = False
        self.is_false = False
        self.is_null = False

    def __str__(self):
        return str(self.get_value())

    def get_value(self):
        if self.map:
            return self.map
        if self.array:
            return self.array
        if self.nb_array:
            return self.nb_array
        if self.pair:
            return self.pair
        if self.string:
            return self.string
        if self.number:
            return self.number
        if self.quoted:
            return self.quoted
        if self.is_true:
            return True
        if self.is_false:
            return False
        if self.is_null:
            return None

    def enterModl_value(self, ctx: MODLParser.Modl_valueContext):
        if ctx.modl_map():
            self.map = Map()
            ctx.modl_map().enterRule(self.map)
        if ctx.modl_array():
            self.array = Array()
            ctx.modl_array().enterRule(self.array)
        if ctx.modl_nb_array():
            self.nb_array = NbArray()
            ctx.modl_nb_array().enterRule(self.nb_array)
        if ctx.modl_pair():
            self.pair = Pair()
            ctx.modl_pair().enterRule(self.pair)

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
