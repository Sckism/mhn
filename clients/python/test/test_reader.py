import unittest
from io import StringIO
from mhn.dialect import Dialect
from mhn.reader import DictReader

from mhn.schema import generate_schema


class TestDictReader(unittest.TestCase):
    def test_read_flat_structure(self):
        data_str = "Id|Name|Age\n1|Alice|30\n2|Bob|25"
        schema_str = "Id|Name|Age"
        reader = DictReader(StringIO(data_str), read_schema_from_first_row=True)
        expected_data = [
            {"Id": "1", "Name": "Alice", "Age": "30"},
            {"Id": "2", "Name": "Bob", "Age": "25"},
        ]
        result_data = list(reader)
        self.assertEqual(expected_data, result_data)

    def test_read_nested_structure(self):
        data_str = "1|>Alice|30<|USA\n2|>Bob|25<|Canada"
        schema_str = "Id|User>Name|Age<|Country"
        reader = DictReader(StringIO(data_str), schema=schema_str)
        expected_data = [
            {"Id": "1", "User": {"Name": "Alice", "Age": "30"}, "Country": "USA"},
            {"Id": "2", "User": {"Name": "Bob", "Age": "25"}, "Country": "Canada"},
        ]
        result_data = list(reader)
        self.assertEqual(expected_data, result_data)

    def test_read_array_structure(self):
        data_str = "Id|Tags[]|Country\n1|[Python^Django^Flask]|USA\n2|[Java^Spring^Hibernate]|Canada"
        reader = DictReader(StringIO(data_str), read_schema_from_first_row=True)
        expected_data = [
            {"Id": "1", "Tags": ["Python", "Django", "Flask"], "Country": "USA"},
            {"Id": "2", "Tags": ["Java", "Spring", "Hibernate"], "Country": "Canada"},
        ]
        result_data = list(reader)
        self.assertEqual(expected_data, result_data)

    def test_read_combined_structure(self):
        data_str = "1|>Alice|30<|[Python^Django^Flask]|USA\n2|>Bob|25<|[Java^Spring^Hibernate]|Canada"
        schema_str = "Id|User>Name|Age<|Tags[]|Country"
        reader = DictReader(StringIO(data_str), schema=schema_str)
        expected_data = [
            {
                "Id": "1",
                "User": {"Name": "Alice", "Age": "30"},
                "Tags": ["Python", "Django", "Flask"],
                "Country": "USA",
            },
            {
                "Id": "2",
                "User": {"Name": "Bob", "Age": "25"},
                "Tags": ["Java", "Spring", "Hibernate"],
                "Country": "Canada",
            },
        ]
        result_data = list(reader)
        self.assertEqual(expected_data, result_data)

    def test_read_ten_rows_with_double_nested_data(self):
        data_rows = [
            {
                "Id": f"{i}",
                "User": {"Name": f"Name {i}", "Age": f"{20 + i}"},
                "Address": {"City": f"City {i}", "Country": f"Country {i}"},
            }
            for i in range(1, 11)
        ]
        schema = "Id|User>Name|Age<|Address>City|Country<"
        input_data = "\n".join(
            [
                f"{row['Id']}|>{row['User']['Name']}|{row['User']['Age']}<|>{row['Address']['City']}|{row['Address']['Country']}<"
                for row in data_rows
            ]
        )

        input_io = StringIO(input_data)
        reader = DictReader(input_io, schema)

        output_data = [row for row in reader]
        self.assertEqual(data_rows, output_data)

    def test_read_escaped_chars(self):
        expected_output = [
            {
                "Field1": "Value with >",
                "Field2": "Value with <",
                "Field3": "Value with |",
                "Field4": "Value with [",
                "Field5": "Value with ]",
                "Field6": "Value with ^",
                "Nested": {
                    "Field8": "Nested value with >",
                    "Field9": "Nested value with <",
                    "Field10": "Nested value with |",
                    "Field11": "Nested value with [",
                    "Field12": "Nested value with ]",
                    "Field13": "Nested value with ^",
                },
                "Array": [
                    "Value with >",
                    "Value with <",
                    "Value with |",
                    "Value with [",
                    "Value with ]",
                    "Value with ^",
                ],
            }
        ]
        
        schema = generate_schema(expected_output[0])
        
        input_data = (
            schema
            + "\n"
            + r"Value with \>|Value with \<|Value with \||Value with \[|Value with \]|Value with \^|>Nested value with \>|Nested value with \<|Nested value with \||Nested value with \[|Nested value with \]|Nested value with \^|<|Value with \>^Value with \<^Value with \|^Value with \[^Value with \]^Value with \^"
        )
        
        f = StringIO(input_data)
        reader = DictReader(f, read_schema_from_first_row=True)
        output = list(reader)

        self.assertEqual(expected_output, output)

    def test_read_escaped_newlines(self):
        expected_output = [
            {
                "Field1": "Value with newline\ninside",
                "Field2": "Value with newline\n\nand two newlines",
                "Nested": {
                    "Field3": "Nested value with newline\ninside",
                },
                "Array": [
                    "Value with newline\ninside",
                    "Value with two\nnewlines\nhere",
                ],
            }
        ]

        schema = generate_schema(expected_output[0])

        input_data = (
            schema
            + "\n"
            + r"Value with newline\\ninside|Value with newline\\n\\nand two newlines|>Nested value with newline\\ninside|<|Value with newline\\ninside^Value with two\\nnewlines\\nhere"
        )

        f = StringIO(input_data)
        reader = DictReader(f, read_schema_from_first_row=True)
        output = list(reader)

        self.assertEqual(expected_output, output)


if __name__ == "__main__":
    unittest.main()
