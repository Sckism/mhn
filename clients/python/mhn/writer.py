from io import IOBase
from .dialect import Dialect, default_dialect


class DictWriter:
    """
    A writer class for writing dictionaries as MHN formatted data.

    Example:
        writer = DictWriter(output_file, 'Field1|Field2|Field3')
        writer.writeheader()
        writer.writerow({'Field1': 'Value 1', 'Field2': 'Value 2', 'Field3': 'Value 3'})

    """
    def __init__(
        self, f: IOBase, schema: str, dialect: Dialect = default_dialect
    ) -> None:
        """
        Initialize a new instance of DictWriter.

        Args:
            f (IOBase): A file-like object to write the MHN data to.
            schema (str): The schema to use when writing the MHN data.
            dialect (Dialect, optional): The dialect to use when writing the MHN data.
                Defaults to the default dialect.

        Raises:
            ValueError: Raised if the schema is empty.
        """
        self.output = f
        self.schema = schema
        self.dialect = dialect

    def writeheader(self) -> None:
        """
        Write the schema to the output file.
        """
        self.output.writelines([self.schema])

    def writerow(self, row: dict) -> None:
        """
        Write a row of data to the output file.

        Args:
            row (dict): A dictionary of key/value pairs to write to the output file.
        """
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

        mhn_parts = []
        schema_parts = parse_schema_parts(sub_schema or self.schema)

        for part in schema_parts:
            field_name = part.split(self.dialect.array_start)[0].split(
                self.dialect.level_start
            )[0]

            if self.dialect.array_start in part and self.dialect.array_end in part:
                mhn_parts.append(
                    self.dialect.array_separator.join(escape_control_chars(escape_newlines(data_dict[field_name], self.dialect), self.dialect))
                )
            elif self.dialect.level_start in part:
                field_name = part.split(self.dialect.level_start)[0]
                _, nested_schema = part.split(self.dialect.level_start)
                nested_schema = nested_schema[:-1]  # Remove trailing level_end
                mhn_parts.append(
                    f"{self.dialect.level_start}{self.convert_dict_to_mhn(data_dict[field_name], sub_schema=nested_schema)}{self.dialect.level_end}"
                )
            else:
                mhn_parts.append(escape(escape_newlines(str(data_dict[field_name]), self.dialect), self.dialect))

        return self.dialect.delimiter.join(mhn_parts)
