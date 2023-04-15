from io import IOBase
from .dialect import Dialect, default_dialect
from .schema import parse_schema_parts
from .utilities import escape_newlines, escape, escape_control_chars


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
        def handle_array(part, array_items):
            if isinstance(array_items[0], dict):
                end_index = part.rfind(self.dialect.array_end)
                sub_schema = part[:end_index].split(self.dialect.array_start, 1)[1]
                return self.dialect.array_separator.join([
                    self.convert_dict_to_mhn(item, sub_schema=sub_schema) for item in array_items
                ])
            else:
                return self.dialect.array_separator.join(escape_control_chars(escape_newlines(array_items, self.dialect), self.dialect))

        def handle_nested_object(part, field_name):
            _, nested_schema = part.split(self.dialect.level_start)
            nested_schema = nested_schema[:-1]  # Remove trailing level_end
            return f"{self.dialect.level_start}{self.convert_dict_to_mhn(data_dict[field_name], sub_schema=nested_schema)}{self.dialect.level_end}"

        def handle_regular_field(field_name):
            return escape(escape_newlines(str(data_dict[field_name]), self.dialect), self.dialect)

        mhn_parts = []
        schema_parts = parse_schema_parts(sub_schema or self.schema, self.dialect)

        for part in schema_parts:
            field_name = part.split(self.dialect.array_start)[0].split(
                self.dialect.level_start
            )[0]

            if self.dialect.array_start in part and self.dialect.array_end in part:
                mhn_parts.append(handle_array(part, data_dict[field_name]))
            elif self.dialect.level_start in part:
                mhn_parts.append(handle_nested_object(part, field_name))
            else:
                mhn_parts.append(handle_regular_field(field_name))

        return self.dialect.delimiter.join(mhn_parts)
