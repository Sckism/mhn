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

    def __iter__(self):
        return self

    def __next__(self) -> Dict[str, Union[str, List[str]]]:
        line = self.input.readline().rstrip()
        if not line:
            raise StopIteration

        row_data = self.parse_mhn_string(line, self.schema)
        return row_data

    def parse_mhn_string(self, data_str, schema_str):
        def parse_array(array_str):
            if array_str.startswith(self.dialect.array_start) and array_str.endswith(self.dialect.array_end):
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

        def parse_level(data_line, schema_line):
            result = {}
            data_parts = split_nested(data_line, self.dialect.delimiter, self.dialect.level_start, self.dialect.level_end)
            schema_parts = split_nested(schema_line, self.dialect.delimiter, self.dialect.level_start, self.dialect.level_end)

            for i, part in enumerate(schema_parts):
                if self.dialect.array_start in part and self.dialect.array_end in part:
                    field_name = part[:-2]
                    result[field_name] = parse_array(data_parts[i])
                elif self.dialect.level_start in part:
                    field_name, sub_schema = part.split(self.dialect.level_start)
                    sub_data, remaining_data = data_parts[i].split(self.dialect.level_end, 1)
                    sub_data = sub_data.lstrip(self.dialect.level_start)  # Remove leading level_start
                    sub_schema = sub_schema.rstrip(self.dialect.level_end)  # Remove trailing level_end
                    result[field_name] = parse_level(sub_data, sub_schema)
                    data_parts[i] = remaining_data
                else:
                    result[part] = data_parts[i]

            return result

        # Parse single line of data
        return parse_level(data_str.strip(), schema_str)

