from typing import List, Dict

from antlr4.tree.Tree import TerminalNodeImpl

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

    def to_dict(self):
        if self.map_items:
            return {i.get_key():i.get_value() for i in self.map_items}
        return {}

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

    def get_key(self):
        if self.pair:
            return self.pair.get_key()
        else:
            return self.map_conditional.get_key()

    def get_value(self):
        if self.pair:
            return self.pair.get_value()
        else:
            return self.map_conditional.get_value()

    def enterModl_map_item(self, ctx:MODLParser.Modl_map_itemContext):
        if ctx.modl_pair():
            self.pair = Pair()
            ctx.modl_pair().enterRule(self.pair)
        if ctx.modl_map_conditional():
            self.map_conditional = MapConditional()
            ctx.modl_map_conditional().enterRule(self.map_conditional)


class MapConditional(MODLParserListener):
    def __init__(self):
        self.map_conditionals = {}

    def enterModl_map_conditional(self, ctx:MODLParser.Modl_map_conditionalContext):
        for i in range(0, len(ctx.modl_condition_test())):
            condition_test = ConditionTest()
            ctx.modl_condition_test(i).enterRule(condition_test)
            conditional_return = MapConditionalReturn()
            ctx.modl_map_conditional_return(i).enterRule(conditional_return)
            self.map_conditionals[condition_test] = conditional_return
        num_returns = len(ctx.modl_map_conditional_return())
        num_tests = len(ctx.modl_condition_test())
        if num_returns > num_tests:
            condition_test = ConditionTest()
            conditional_return = MapConditionalReturn()
            ctx.modl_map_conditional_return(num_returns-1).enterRule(conditional_return)
            self.map_conditionals[condition_test] = conditional_return


class MapConditionalReturn(MODLParserListener):
    def __init__(self):
        self.map_items = []

    def enterModl_map_conditional_return(self, ctx:MODLParser.Modl_map_conditional_returnContext):
        if ctx.modl_map_item():
            for mi in ctx.modl_map_item():
                map_item = MapItem()
                mi.enterRule(map_item)
                self.map_items.append(map_item)


class SubCondition(MODLParserListener):
    """Base class"""
    pass


class ConditionGroup(SubCondition):
    def __init__(self):
        self.condition_tests = []

    def __str__(self):
        return ','.join(self.condition_tests)

    def enterModl_condition_group(self, ctx:MODLParser.Modl_condition_groupContext):
        if ctx.children:
            last_operator = None
            for child in ctx.children:
                if type(child) == MODLParser.Modl_condition_testContext:
                    condition_test = ConditionTest()
                    child.enterRule(condition_test)
                    self.condition_tests.append((condition_test,last_operator))
                    last_operator = None
                else:
                    if not(child.getText == '{' or child.getText == '}'):
                        last_operator = child.getText()


class Condition(SubCondition):
    def __init__(self):
        self.key = None
        self.operator = None
        self.values = []

    def __str__(self):
        return str(self.key)

    def enterModl_condition(self, ctx:MODLParser.Modl_conditionContext):
        if ctx.STRING():
            self.key = ctx.STRING().getText()
        if ctx.modl_operator():
            self.operator = ctx.modl_operator().getText()
        for v in ctx.modl_value():
            value = Value()
            v.enterRule(value)
            self.values.append(value)


class ConditionTest(MODLParserListener):
    def __init__(self):
        self.subconditions = []

    def __str__(self):
        return ','.join([f"{a} {b} {c}" for (a,b,c) in self.subconditions])

    def enterModl_condition_test(self, ctx:MODLParser.Modl_condition_testContext):
        if ctx.children:
            last_operator: str = None
            should_negate = False
            for child in ctx.children:
                if type(child) == MODLParser.Modl_condition_groupContext:
                    condition_group = ConditionGroup()
                    child.enterRule(condition_group)
                    self.subconditions.append((condition_group,last_operator,should_negate))
                    last_operator = None
                    should_negate = False
                elif type(child) == MODLParser.Modl_conditionContext:
                    condition = Condition()
                    child.enterRule(condition)
                    self.subconditions.append((condition,last_operator,should_negate))
                    last_operator = None
                    should_negate = False
                else:
                    if child.getText() == '!':
                        should_negate = True
                    else:
                        last_operator = child.getText()


class TopLevelConditionalReturn(MODLParserListener):
    def __init__(self):
        self.structures = []

    def enterModl_top_level_conditional_return(self, ctx:MODLParser.Modl_top_level_conditional_returnContext):
        if ctx.modl_structure():
            for struct in ctx.modl_structure():
                structure = Structure()
                struct.enterRule(structure)
                self.structures.append(structure)


class TopLevelConditional(MODLParserListener):
    def __init__(self):
        self.conditions: Dict[ConditionTest,TopLevelConditionalReturn] = None

    def enterModl_top_level_conditional(self, ctx:MODLParser.Modl_top_level_conditionalContext):
        self.conditions = {}

        for i in range(0, len(ctx.modl_condition_test())):
            condition_test = ConditionTest()
            ctx.modl_condition_test(i).enterRule(condition_test)
            conditional_return = TopLevelConditionalReturn()
            ctx.modl_top_level_conditional_return(i).enterRule(conditional_return)
            self.conditions[condition_test] = conditional_return
        # This seems odd...
        num_returns = len(ctx.modl_top_level_conditional_return())
        num_tests = len(ctx.modl_condition_test())
        if num_returns > num_tests:
            condition_test = ConditionTest()
            conditional_return = TopLevelConditionalReturn()
            ctx.modl_top_level_conditional_return(num_returns-1).enterRule(conditional_return)
            self.conditions[condition_test] = conditional_return


class ArrayItem(MODLParserListener):
    def __init__(self):
        self.array_value_item: ArrayValueItem = None
        self.array_conditional: ArrayConditional = None

    def get_item(self):
        if self.array_value_item:
            return self.array_value_item
        else:
            return self.array_conditional

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

    def get_value(self):
        if self.map:
            return self.map
        if self.array:
            return self.array
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


class ArrayConditionalReturn(MODLParserListener):
    def __init__(self):
        self.array_items = []

    def enterModl_array_conditional_return(self, ctx:MODLParser.Modl_array_conditional_returnContext):
        if ctx.modl_array_item():
            for ai in ctx.modl_array_item():
                array_item = ArrayItem()
                ai.enterRule(array_item)
                self.array_items.append(array_item)


class ArrayConditional(MODLParserListener):
    def __init__(self):
        self.conditions: Dict[ConditionTest, ArrayConditionalReturn] = {}

    def enterModl_array_conditional(self, ctx:MODLParser.Modl_array_conditionalContext):
        for i in range(0, len(ctx.modl_condition_test())):
            condition_test = ConditionTest()
            ctx.modl_condition_test(i).enterRule(condition_test)
            conditional_return = ArrayConditionalReturn()
            ctx.modl_array_conditional_return(i).enterRule(conditional_return)
            self.conditions[condition_test] = conditional_return

        num_returns = len(ctx.modl_array_conditional_return())
        num_tests = len(ctx.modl_condition_test())
        if num_returns > num_tests:
            condition_test = ConditionTest()
            conditional_return = ArrayConditionalReturn()
            ctx.modl_array_conditional_return(num_returns-1).enterRule(conditional_return)
            self.conditions[condition_test] = conditional_return


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
        self.array_items: List = None

    def get_item(self):
        return self.array_items

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
        self.array_items: List = None

    def to_list(self) -> List:
        return [ai.get_item() for ai in self.array_items]

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

    def get_key(self):
        return self.key

    def get_value(self):
        if self.map:
            return map
        if self.array:
            return self.array
        if self.value_item:
            return self.value_item

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

    def get_value(self):
        if self.value:
            return self.value
        else:
            return self.value_conditional

    def __str__(self):
        return str(self.get_value())

    def enterModl_value_item(self, ctx:MODLParser.Modl_value_itemContext):
        if ctx.modl_value():
            self.value = Value()
            ctx.modl_value().enterRule(self.value)
        if ctx.modl_value_conditional():
            self.value_conditional = ValueConditional()
            ctx.modl_value_conditional().enterRule(self.value_conditional)


class ValueConditionalReturn(MODLParserListener):
    def __init__(self):
        self.value_items = []

    def __str__(self):
        return ','.join(self.value_items)

    def enterModl_value_conditional_return(self, ctx:MODLParser.Modl_value_conditional_returnContext):
        if ctx.modl_value_item():
            for vi in ctx.modl_value_item():
                value_item = ValueItem()
                vi.enterRule(value_item)
                self.value_items.append(value_item)


class ValueConditional(MODLParserListener):
    def __init__(self):
        self.value_conditionals = {}

    def enterModl_value_conditional(self, ctx:MODLParser.Modl_value_conditionalContext):
        for i in range(len(ctx.modl_condition_test())):
            condition_test = ConditionTest()
            ctx.modl_condition_test(i).enterRule(condition_test)
            conditional_return = ValueConditionalReturn()
            ctx.modl_value_conditional_return(i).enterRule(conditional_return)
            self.value_conditionals[condition_test] = conditional_return
        num_returns = len(ctx.modl_value_conditional_return())
        num_tests = len(ctx.modl_condition_test())
        if num_returns > num_tests:
            condition_test = ConditionTest()
            conditional_return = ValueConditionalReturn()
            ctx.modl_value_conditional_return(num_returns-1).enterRule(conditional_return)
            self.value_conditionals[condition_test] = conditional_return


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
