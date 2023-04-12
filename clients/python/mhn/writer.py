from io import IOBase
from .dialect import Dialect
from .mhn import default_dialect

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

    def convert_dict_to_mhn(self, data_dict):
        mhn_parts = []
        schema_parts = self.schema.split(self.dialect.delimiter)
        for part in schema_parts:
            if self.dialect.array_start in part and self.dialect.array_end in part:
                field_name = part[:-2]
                mhn_parts.append(self.dialect.array_separator.join(data_dict[field_name]))
            elif self.dialect.level_start in part:
                field_name, sub_schema = part.split(self.dialect.level_end)
                sub_schema = sub_schema[:-1]  # Remove trailing level_end
                mhn_parts.append(f'{self.dialect.level_start}{self.convert_dict_to_mhn(self, data_dict[field_name], sub_schema)}{self.dialect.level_end}')
            else:
                mhn_parts.append(str(data_dict[part]))
        return self.dialect.delimiter.join(mhn_parts)