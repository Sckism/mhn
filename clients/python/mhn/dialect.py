class Dialect:
    def __init__(
        self,
        delimiter: str = "|",
        level_start: str = ">",
        level_end: str = "<",
        array_start: str = "[",
        array_end: str = "]",
        array_separator: str = "^",
        empty_array: str = "~",
        line_break: str = '\n',
        escape_char: str = "\\"
    ):
        self.delimiter = delimiter
        self.level_start = level_start
        self.level_end = level_end
        self.array_start = array_start
        self.array_end = array_end
        self.array_separator = array_separator
        self.empty_array = empty_array
        self.line_break = line_break
        self.escape_char = escape_char
    
    @property
    def control_chars(self) -> set:
        return set(
            self.level_start
            + self.level_end
            + self.array_start
            + self.array_end
            + self.array_separator
            + self.delimiter
        )
        
    @property
    def escape_mappings(self) -> dict:
        return {
            f"{self.escape_char}{self.array_start}": "___ARRAY_START___",
            f"{self.escape_char}{self.array_end}": "___ARRAY_END___",
            f"{self.escape_char}{self.array_separator}": "___ARRAY_SEPARATOR___",            
            f"{self.escape_char}{self.empty_array}": "___EMPTY_ARRAY___",
            f"{self.escape_char}{self.level_start}": "___LEVEL_START___",
            f"{self.escape_char}{self.level_end}": "___LEVEL_END___",
            f"{self.escape_char}{self.delimiter}": "___DELIMITER___",
        }


default_dialect = Dialect()
