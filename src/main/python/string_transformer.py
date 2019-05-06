from typing import Union, List, Dict

from modl_creator import TrueVal, ModlObject, ModlValue, FalseVal, String, Number, Pair
from string_utils import EscapeStrings
from variable_methods import is_variable_method, transform


def is_digit(param):
    return param in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}


def is_letter(char):
    return char.isalpha()


def get_end_of_number(str_to_transform, start_index):
    # We actually need to keep processing this string until we get to an end
    # The end (for the number type) can be a space, or else any non-number character
    # If the end is a ".", then check to see if we have a variable method

    # First, find the end of the number
    curr_index = start_index
    if curr_index == len(str_to_transform):
        return curr_index
    while is_digit(str_to_transform[curr_index]):
        curr_index = curr_index + 1
        if curr_index == len(str_to_transform):
            return curr_index

    # Check the first character after the number
    if not str_to_transform[curr_index] == '.':
        return curr_index

    new_method = ""
    while True:
        curr_index += 1
        if curr_index > len(str_to_transform)-1:
            return curr_index
        next_char = str_to_transform[curr_index]
        if next_char == '.':
            # we come to another "." - in which case keep going and build up a new method name from the characters
            if len(new_method) > 0:
                new_method = ''
            else:
                return curr_index
        else:
            # we don't have any more variable methods that match the lengthened string
            if not is_letter(next_char):
                return curr_index
            if is_variable_method(new_method + next_char):
                new_method += next_char
            else:
                if len(new_method) > 0:
                    return curr_index
                else:
                    return curr_index - 1  # cope with "."


class StringTransformer:
    def __init__(self,
                 value_pairs: Dict[String, ModlValue],
                 variables: Dict[String, ModlValue],
                 numbered_variables: Dict[int, ModlValue]):
        self.value_pairs = value_pairs
        self.variables: dict = variables
        self.numbered_variables = numbered_variables

    def transform(self, input: str) -> Union[None,ModlValue]:
        if input is None:
            return None

        if input.lower() == 'true':
            return TrueVal()
        if input.lower() == 'false':
            return FalseVal()

        # 5: Replace the strings as per the txt document attached "string-replacement.txt"
        input = EscapeStrings().unescape(input)

        # Replace any unicode encodings
        # TODO

        # Implement Elliott's algorithm for string transformation :
        # 1 : Find all parts of the sting that are enclosed in graves, e.g `test` where neither of the graves is prefixed with an escape character ~ (tilde) or \ (backslash).
        grave_parts: List[str] = self.grave_parts_from_string(input)

        # [ 2: If no parts are found, run “Object Referencing detection” ] - basically go to 4:
        # 3 : If parts are found loop through them in turn:
        for grave_part in grave_parts:
            # If a part begins with a % then run “Object Referencing”, else run “Punycode encoded parts”
            new_grave_part = None
            if grave_part.startswith('`%'):
                ret: ModlValue = self.run_object_referencing(grave_part, input, True)
                if isinstance(ret, String):
                    input = str(ret)
                    non_grave_part = grave_part[1:]
                    input = input.replace(grave_part, non_grave_part)
                elif isinstance(ret, Number):
                    if grave_part == input:
                        return ret
                    num_str = str(ret.get_value())
                    input = input.replace(grave_part, num_str)
                else:
                    return ret
            else:
                # else run “Punycode encoded parts”
                # TODO...
                new_grave_part = grave_part  # replacePunycode(grave_part)
                input = input.replace(grave_part, new_grave_part)

        # 4: Find all non-space parts of the string that are prefixed with % (percent sign). These are object references – run “Object Referencing”
        percent_parts = self.get_percent_parts_from_string(input)

        for pct_part in percent_parts:
            ret = self.run_object_referencing(pct_part, input, False)
            if isinstance(ret, String):
                input = str(ret)
            elif isinstance(ret, Number):
                if pct_part == input:
                    return ret
                num_str = str(ret.get_value())  # ?!@?
                input = input.replace(pct_part, num_str)
            else:
                return ret

        return String(input)

    def run_object_referencing(self, percent_part: str, string_to_transform: str, is_graved: bool):
        """
        Object Referencing
        If the reference includes a . (dot / full stop / period) then the reference key should be considered everything to the left of the . (dot / full stop / period).

        If the reference includes any part enclosed in [ and ] this is a deep object reference, see deep object referencing instructions and return back to this section.

        Replace the reference key with the value of that key. We will call this the subject.

        If there was a period in the original string, any part to the right of the first period (until the end of the part not including the end grave) is considered the method chain. Split the method chain by . (dot / full stop / period) and create an array from the methods.

        Loop through the array and pass the subject to the named method, transforming the subject. Repeat the process (with the transformed subject) until all methods in the chain have been applied and the subject is fully transformed.

        Replace the part originally found (including graves) with the transformed subject.
        :param percent_part:
        :param string_to_transform:
        :param is_graved:
        :return:
        """
        start_offset = 1
        end_offset = 0
        if is_graved:
            start_offset = 2
            end_offset = 1

        # modl_obj = ModlObject()
        subject = percent_part[start_offset:len(percent_part)-end_offset]

        method_chain:str = None
        try:
            index_of_dot = percent_part.index('.')
        except ValueError:
            index_of_dot = None  # not found

        if index_of_dot:
            subject = percent_part[start_offset:index_of_dot]
            method_chain = percent_part[index_of_dot + 1:len(percent_part) - end_offset]

        value: ModlValue = self.get_value_for_reference(subject)

        if value is None:
            return String(string_to_transform)
        elif isinstance(value, String):
            subject = str(value)
        else:
            return value

        if method_chain:
            methods = method_chain.split(".")
            if not methods:
                methods = [method_chain]
            for method in methods:
                if '(' in method:
                    # HANDLE TRIM AND REPLACE HERE!!
                    # We need to strip the "(<params>)" and apply the method to the subject AND the params!
                    # TODO (we might need to check for escaped "."s one day...
                    start_params_index = method.index('(')
                    params_str = method[start_params_index + 1 : len(method) - 1]
                    method_str = method[:start_params_index]
                    subject = transform(method_str, f"{subject},{params_str}")
                else:
                    if not is_variable_method(method):
                        # Nothing to do - leave it alone!
                        subject = f"{subject}.{method}"
                    else:
                        subject = transform(method, subject)

        string_to_transform = string_to_transform.replace(percent_part, subject)
        return String(string_to_transform)

    def get_value_for_reference(self, subject) -> ModlValue:
        # Subject might be a nested object reference, so handle it here
        try:
            gt_index = subject.index('>')
        except ValueError:
            gt_index = None

        is_nested = gt_index is not None

        if is_nested:
            remainder = subject[gt_index+1:]
            subject = subject[:gt_index]
        else:
            remainder = None

        # Find the first level object reference, whether nested or not

        value: ModlValue = None
        found = False

        # Make any variable replacements, etc.

        for i in range(0, len(self.numbered_variables)):
            if subject == str(i):
                if isinstance(self.numbered_variables[i], String):
                    value = self.numbered_variables[i]
                else:
                    # Why the dupe?
                    value = self.numbered_variables[i]
                found = True
                break

        if not found:
            for var_key, var_value in self.variables.items():
                if subject == var_key:
                    value = var_value
                    found = True
                    break

        if not found:
            for var_key, var_value in self.value_pairs.items():
                if subject == var_key or subject == '_'+str(var_key):
                    value = var_value
                    found = True
                    break

        # If we have a nested reference follow it recursively until we find the value we need.
        if value and is_nested:
            return self.get_value_for_reference_recursive(value, remainder)

        return value

    def grave_parts_from_string(self, input):
        """
        Find all parts of the sting that are enclosed in graves, e.g `test` where neither of the graves is
        prefixed with an escape character ~ (tilde) or \ (backslash).
        :param input:
        :return:
        """
        grave_parts = []

        curr_index = 0
        finished = False
        while not finished:
            finished = True
            start_index = self.get_next_non_prefixed_grave(input, curr_index)
            if start_index is not None:
                end_index = self.get_next_non_prefixed_grave(input, start_index+1)
                if end_index is not None:
                    grave_part = input[start_index:end_index+1]
                    grave_parts.append(grave_part)
                    curr_index = end_index + 1
                    finished = False
        return grave_parts

    def get_next_non_prefixed_grave(self, input, start_index):
        # From start_index, find the next grave. If it is prefixed by either ~ or \ then ignore it and find the next one
        try:
            index = input.index('`', start_index)
        except ValueError:
            index = None

        if index is None:
            return None

        if index > start_index:
            prefix = input[index-1]
            if prefix == '~' or prefix == '\\':
                return self.get_next_non_prefixed_grave(input, index+1)
            else:
                return index
        else:
            return start_index

    def get_percent_parts_from_string(self, input) -> List:
        # Find all non-space parts of the string that are prefixed with % (percent sign).
        percent_parts = []
        curr_index = 0
        finished = False
        while not finished:
            finished = True
            start_index = self.get_next_percent(input, curr_index)
            if start_index is not None:
                end_index = None
                # If the first character after the % is a number, then keep reading until we get to a non-number (taking account of method chains)
                # If the first character after the % is a letter, then keep reading until we get to a space
                if start_index < len(input)-1 and (not is_digit(input[start_index + 1:start_index + 2])):
                    # Just read to the next space
                    try:
                        space_end_index = input.index(" ", start_index)
                    except ValueError:
                        space_end_index = 99999

                    try:
                        colon_end_index = input.index(":", start_index)
                    except ValueError:
                        colon_end_index = 99999

                    end_index = min(space_end_index, colon_end_index)

                    if end_index > len(input):
                        end_index = len(input)
                elif start_index == len(input) - 1:
                    return percent_parts
                else:
                    end_index = get_end_of_number(input, start_index+1)

                if end_index is not None:
                    if end_index > start_index + 1:
                        grave_part = input[start_index:end_index]
                        percent_parts.append(grave_part)
                        curr_index = end_index + 1
                    finished = False
        return percent_parts


    def get_next_percent(self, input, start_index):
        # From startIndex, find the next grave. If it is prefixed by either ~ or \ then ignore it and find the next one
        try:
            return input.index('%', start_index)
        except ValueError:
            return None

    def get_value_for_reference_recursive(self, ctx: ModlValue, key: str) -> ModlValue:
        """
        For keys such as a>b>c>d>e, each call to this method takes the first part and uses it to find the referenced
        object in the current ctx object, then calls itself with this new object as the context and the remaining part
        of the nested object reference (b>c>d>e in this case) until all the parts of the reference are used up.

        :param ctx: The should contain a value for the given key
        :param key: The key of the object that we need - possibly a nested reference.
        :return: The value that was referenced, or a RuntimeException if the reference is invalid.
        """

        # Check for nested keys
        try:
            gt_index = key.index('>')
        except ValueError:
            gt_index = None

        is_nested = gt_index is not None

        remainder: str = None
        curr_key: str = None

        if is_nested:
            remainder = key[gt_index+1:]
            curr_key = key[:gt_index]
        else:
            remainder = None
            curr_key = key

        # Get the nested value via its name or number
        new_ctx: ModlValue = None
        if curr_key.isdigit():
            index = int(curr_key)
            if isinstance(ctx, Pair):
                if index != 0:
                    raise ValueError("Index should always be zero when reference the value of a Pair")
                new_ctx = ctx.get_value()
            else:
                new_ctx = ctx.get_by_index(index)
        else:
            if isinstance(ctx, Pair):
                if curr_key != ctx.get_key():
                    raise ValueError("Object reference should match the key name for a Pair")
                new_ctx = ctx.get_value()
            else:
                new_ctx = ctx.get_by_name(curr_key)

        # Recurse if we're still nested
        if is_nested:
            return self.get_value_for_reference_recursive(new_ctx, remainder)
        elif not new_ctx:
            # The currentKey number or name must be invalid.
            raise ValueError(f"Invalid Object Reference: {curr_key}")

        # Success, return the value we found.
        return new_ctx

