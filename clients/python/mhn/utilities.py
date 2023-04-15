from .dialect import Dialect

def unescape(value, dialect:Dialect):
    """
    Replaces escaped characters in a string with their original characters according to the provided dialect.

    Args:
        value (str): The string containing escaped characters.
        dialect (Dialect): The dialect defining the escape characters and mappings.

    Returns:
        str: The unescaped string.
    """
    for control_char, replace_char in dialect.escape_mappings.items():
        value = value.replace(replace_char, control_char.lstrip(dialect.escape_char))
    return value

def split_nested(data, dialect:Dialect):
    parts = []
    current_part = []
    nesting_level = 0

    for char in data:
        if char == dialect.level_start:
            nesting_level += 1
        elif char == dialect.level_end:
            nesting_level -= 1
        elif char == dialect.delimiter and nesting_level == 0:
            parts.append("".join(current_part))
            current_part = []
            continue

        current_part.append(char)

    parts.append("".join(current_part))
    return parts

def parse_array(array_str, dialect:Dialect):
    """
    Parses a string representing an array and returns a list of unescaped strings.

    Args:
        array_str (str): The string representing the array, including delimiters.
        dialect (Dialect): The dialect defining the array start and end characters, as well as the separator.

    Returns:
        List[str]: The unescaped array items as a list of strings.
    """
    if array_str.startswith(dialect.array_start) and array_str.endswith(
        dialect.array_end
    ):
        array_str = array_str[1:-1]    
    
    if array_str == dialect.empty_array:
        return []
    array_items = array_str.split(dialect.array_separator)
    # Unescape escaped control characters in array items
    array_items = [unescape(item, dialect) for item in array_items]
    return array_items

def unescape_newlines(value, dialect: Dialect):
    """
    Replaces escaped newline characters with actual newline characters in a string or list of strings.

    Args:
        value (Union[str, List[str]]): The string or list of strings containing escaped newline characters.
        dialect (Dialect): The dialect defining the escape characters and mappings.

    Returns:
        Union[str, List[str]]: The string or list of strings with the newline characters unescaped.
    """
    if isinstance(value, str):
        return value.replace(f"{dialect.escape_char}\\n", "\n")
    elif isinstance(value, list):
        return [unescape_newlines(v, dialect) for v in value]
    else:
        return value

def escape_newlines(value, dialect:Dialect):
    if isinstance(value, str):
        return value.replace(dialect.line_break, "\\n")
    elif isinstance(value, list):
        return [escape_newlines(v, dialect) for v in value]
    else:
        return value

def escape(value, dialect):
    if isinstance(value, str):
        for control_char in dialect.control_chars:
            value = value.replace(control_char, f"{dialect.escape_char}{control_char}")
    elif isinstance(value, list):
        value = [escape(v, dialect) for v in value]
    return value

def escape_control_chars(data, dialect: Dialect):
    return [escape(v, dialect) for v in data]