from io import IOBase
from typing import Dict, List, Union
from .dialect import Dialect, default_dialect
from .schema import generate_schema


class DictReader:
    def __init__(
        self,
        f: IOBase,
        schema: str = None,
        dialect: Dialect = default_dialect,
        read_schema_from_first_row: bool = False,
    ) -> None:
        self.input = f
        self.dialect = dialect
        self.read_schema_from_first_row = read_schema_from_first_row

        if read_schema_from_first_row:
            self.schema = self.input.readline().rstrip()
        elif schema:
            self.schema = schema
        else:
            raise ValueError("A schema must be provided or read from the first row")
        
        # Create a mapping of escape+control character to replacement string
        self.escape_mapping = {
            f"{self.dialect.escape_char}{self.dialect.array_start}": "___ARRAY_START___",
            f"{self.dialect.escape_char}{self.dialect.array_end}": "___ARRAY_END___",
            f"{self.dialect.escape_char}{self.dialect.level_start}": "___LEVEL_START___",
            f"{self.dialect.escape_char}{self.dialect.level_end}": "___LEVEL_END___",
            f"{self.dialect.escape_char}{self.dialect.delimiter}": "___DELIMITER___",
            f"{self.dialect.escape_char}{self.dialect.array_separator}": "___ARRAY_SEPARATOR___",
        }

    def __iter__(self):
        return self

    def __next__(self) -> Dict[str, Union[str, List[str]]]:
        line = self.input.readline().rstrip()
        if not line:
            raise StopIteration

        row_data = self.parse_mhn_string(line, self.schema)
        return row_data
    
    def unescape(self, value):
        for control_char, replace_char in self.escape_mapping.items():
            value = value.replace(replace_char, control_char.lstrip(self.dialect.escape_char))
        return value

    def parse_mhn_string(self, data_str, schema_str):
        def parse_array(array_str):
            if array_str.startswith(self.dialect.array_start) and array_str.endswith(
                self.dialect.array_end
            ):
                array_str = array_str[1:-1]
            return array_str.split(self.dialect.array_separator)

        def split_nested(data, delimiter, level_start, level_end):
            parts = []
            current_part = []
            nesting_level = 0

            for char in data:
                if char == level_start:
                    nesting_level += 1
                elif char == level_end:
                    nesting_level -= 1
                elif char == delimiter and nesting_level == 0:
                    parts.append("".join(current_part))
                    current_part = []
                    continue

                current_part.append(char)

            parts.append("".join(current_part))
            return parts
        
        def unescape_newlines(value, dialect: Dialect):
            if isinstance(value, str):
                return value.replace(f"{dialect.escape_char}\\n", "\n")
            elif isinstance(value, list):
                return [unescape_newlines(v, dialect) for v in value]
            else:
                return value

        def parse_level(data_line, schema_line, escape_mapping):
            result = {}
            data_parts = split_nested(
                data_line,
                self.dialect.delimiter,
                self.dialect.level_start,
                self.dialect.level_end,
            )
            schema_parts = split_nested(
                schema_line,
                self.dialect.delimiter,
                self.dialect.level_start,
                self.dialect.level_end,
            )

            for i, part in enumerate(schema_parts):
                if self.dialect.array_start in part and self.dialect.array_end in part:
                    field_name = part[:-2]
                    result[field_name] = [unescape_newlines(self.unescape(val), self.dialect) for val in parse_array(data_parts[i])]
                elif self.dialect.level_start in part:
                    field_name, sub_schema = part.split(self.dialect.level_start)
                    sub_data, remaining_data = data_parts[i].split(
                        self.dialect.level_end, 1
                    )
                    sub_data = sub_data.lstrip(
                        self.dialect.level_start
                    )  # Remove leading level_start
                    sub_schema = sub_schema.rstrip(
                        self.dialect.level_end
                    )  # Remove trailing level_end
                    result[field_name] = parse_level(sub_data, sub_schema, escape_mapping)
                    data_parts[i] = remaining_data
                else:
                    val = data_parts[i]
                    # Replace temporary placeholders with original characters
                    for control_char, replace_char in escape_mapping.items():
                        val = val.replace(replace_char, control_char.lstrip(self.dialect.escape_char))

                    result[part] = unescape_newlines(val, self.dialect)

            return result

        # Replace escaped characters with temporary placeholders
        for control_char, replace_char in self.escape_mapping.items():
            data_str = data_str.replace(control_char, replace_char)

        # Parse single line of data
        parsed_data = parse_level(data_str.strip(), schema_str, self.escape_mapping)

        return parsed_data