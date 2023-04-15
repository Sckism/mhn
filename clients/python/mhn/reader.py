from io import IOBase
from typing import Dict, List, Union
from .dialect import Dialect, default_dialect
from .schema import generate_schema
from .utilities import unescape, parse_array, unescape_newlines, split_nested


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

    def __iter__(self):
        return self

    def __next__(self) -> Dict[str, Union[str, List[str]]]:
        line = self.input.readline().rstrip()
        if not line:
            raise StopIteration

        row_data = self._parse_mhn_string(line, self.schema)
        return row_data
    
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
    
    def _parse_level(self, data_line, schema_line):
        result = {}
        data_parts = split_nested(
            data_line,
            self.dialect
        )
        schema_parts = split_nested(
            schema_line,
            self.dialect
        )

        for i, part in enumerate(schema_parts):
            if self.dialect.array_start in part and self.dialect.array_end in part:
                field_name = part[:-2]
                result[field_name] = [unescape_newlines(unescape(val, self.dialect), self.dialect) for val in parse_array(data_parts[i], self.dialect)]
            elif self.dialect.level_start in part:
                field_name, remaining_parts = part.split(self.dialect.level_start)
                sub_data, remaining_data = data_parts[i].split(
                    self.dialect.level_end, 1
                )
                sub_data = sub_data.lstrip(
                    self.dialect.level_start
                )  # Remove leading level_start
                sub_schema = remaining_parts.rstrip(
                    self.dialect.level_end
                )  # Remove trailing level_end
                result[field_name] = self._parse_level(sub_data, sub_schema)
                data_parts[i] = remaining_data
            else:
                val = data_parts[i]
                # Replace temporary placeholders with original characters
                for control_char, replace_char in self.dialect.escape_mappings.items():
                    val = val.replace(replace_char, control_char.lstrip(self.dialect.escape_char))

                field_name = part.split(self.dialect.array_start)[0]
                result[field_name] = unescape_newlines(unescape(val, self.dialect), self.dialect)


        return result

    def _parse_mhn_string(self, data_str, schema_str):
        # Replace escaped characters with temporary placeholders
        for control_char, replace_char in self.dialect.escape_mappings.items():
            data_str = data_str.replace(control_char, replace_char)

        # Parse single line of data
        parsed_data = self._parse_level(data_str.strip(), schema_str)

        return parsed_data