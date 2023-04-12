from io import IOBase
from .dialect import Dialect, default_dialect

class DictWriter:
    # Init
    def __init__(self, f:IOBase, schema:str, dialect:Dialect = default_dialect) -> None:
        self.output = f
        self.schema = schema
        self.dialect = dialect

    def writeheader(self) -> None:
        self.output.writelines([self.schema])

    def writerow(self, row:dict) -> None:
        mhn_str = self.convert_dict_to_mhn(row)
        self.output.writelines([self.dialect.line_break, mhn_str])
        pass

    def convert_dict_to_mhn(self, data_dict, sub_schema=None):
        def parse_schema_parts(schema_str):
            parts = []
            part_start = 0
            nesting_level = 0

            for idx, char in enumerate(schema_str):
                if char == self.dialect.level_start:
                    nesting_level += 1
                elif char == self.dialect.level_end:
                    nesting_level -= 1
                elif char == self.dialect.delimiter and nesting_level == 0:
                    parts.append(schema_str[part_start:idx])
                    part_start = idx + 1

            parts.append(schema_str[part_start:])
            return parts

        mhn_parts = []
        schema_parts = parse_schema_parts(sub_schema or self.schema)

        for part in schema_parts:
            field_name = part.split(self.dialect.array_start)[0].split(self.dialect.level_start)[0]

            if self.dialect.array_start in part and self.dialect.array_end in part:
                mhn_parts.append(self.dialect.array_separator.join(data_dict[field_name]))
            elif self.dialect.level_start in part:
                field_name = part.split(self.dialect.level_start)[0]
                _, nested_schema = part.split(self.dialect.level_start)
                nested_schema = nested_schema[:-1]  # Remove trailing level_end
                mhn_parts.append(f'{self.dialect.level_start}{self.convert_dict_to_mhn(data_dict[field_name], sub_schema=nested_schema)}{self.dialect.level_end}')
            else:
                mhn_parts.append(str(data_dict[field_name]))

        return self.dialect.delimiter.join(mhn_parts)

