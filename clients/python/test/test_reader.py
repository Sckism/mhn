import unittest
from io import StringIO
from mhn.dialect import Dialect, default_dialect
from mhn.reader import DictReader
from mhn.utilities import unescape, parse_array, unescape_newlines, split_nested
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

    # def test_read_data_with_three_layers_of_arrays_containing_structs(self):
    #     data = {
    #         "Countries": [
    #             {
    #                 "Name": "CountryA",
    #                 "Cities": [
    #                     {
    #                         "Name": "CityA1",
    #                         "Attractions": [
    #                             {"Name": "AttractionA1", "Type": "Museum"},
    #                             {"Name": "AttractionA2", "Type": "Park"},
    #                         ],
    #                     },
    #                     {
    #                         "Name": "CityA2",
    #                         "Attractions": [
    #                             {"Name": "AttractionA3", "Type": "Beach"},
    #                             {"Name": "AttractionA4", "Type": "Zoo"},
    #                         ],
    #                     },
    #                 ],
    #             },
    #             {
    #                 "Name": "CountryB",
    #                 "Cities": [
    #                     {
    #                         "Name": "CityB1",
    #                         "Attractions": [
    #                             {"Name": "AttractionB1", "Type": "Museum"},
    #                             {"Name": "AttractionB2", "Type": "Park"},
    #                         ],
    #                     },
    #                     {
    #                         "Name": "CityB2",
    #                         "Attractions": [
    #                             {"Name": "AttractionB3", "Type": "Beach"},
    #                             {"Name": "AttractionB4", "Type": "Zoo"},
    #                         ],
    #                     },
    #                 ],
    #             },
    #         ],
    #     }
        
    #     schema = generate_schema(data)
    #     expected_output = data
        
    #     input_str = (
    #         f"{schema}\n"
    #         "CountryA|CityA1|AttractionA1|Museum^AttractionA2|Park^CityA2|AttractionA3|Beach^AttractionA4|Zoo^"
    #         "CountryB|CityB1|AttractionB1|Museum^AttractionB2|Park^CityB2|AttractionB3|Beach^AttractionB4|Zoo"
    #     )
    #     input_data = StringIO(input_str)

    #     reader = DictReader(input_data, schema=schema, read_schema_from_first_row=True)
    #     actual_output = list(reader)
        
    #     self.assertEqual(expected_output, actual_output)

class Test_unescape(unittest.TestCase):
    def test_unescape_array_start(self):
        escaped = f"{default_dialect.escape_mappings[default_dialect.escape_char+default_dialect.array_start]}"
        unescaped = default_dialect.array_start
        self.assertEqual(unescape(f"___{escaped}___", default_dialect), f"___{unescaped}___")

    def test_unescape_array_end(self):
        escaped = f"{default_dialect.escape_mappings[default_dialect.escape_char+default_dialect.array_end]}"
        unescaped = default_dialect.array_end
        self.assertEqual(unescape(f"___{escaped}___", default_dialect), f"___{unescaped}___")

    def test_unescape_level_start(self):
        escaped = f"{default_dialect.escape_mappings[default_dialect.escape_char+default_dialect.level_start]}"
        unescaped = default_dialect.level_start
        self.assertEqual(unescape(f"___{escaped}___", default_dialect), f"___{unescaped}___")

    def test_unescape_level_end(self):
        escaped = f"{default_dialect.escape_mappings[default_dialect.escape_char+default_dialect.level_end]}"
        unescaped = default_dialect.level_end
        self.assertEqual(unescape(f"___{escaped}___", default_dialect), f"___{unescaped}___")

    def test_unescape_delimiter(self):
        escaped = f"{default_dialect.escape_mappings[default_dialect.escape_char+default_dialect.delimiter]}"
        unescaped = default_dialect.delimiter
        self.assertEqual(unescape(f"___{escaped}___", default_dialect), f"___{unescaped}___")

    def test_unescape_array_separator(self):
        escaped = f"{default_dialect.escape_mappings[default_dialect.escape_char+default_dialect.array_separator]}"
        unescaped = default_dialect.array_separator
        self.assertEqual(unescape(f"___{escaped}___", default_dialect), f"___{unescaped}___")

class Test_unescape_newline(unittest.TestCase):
    def test_unescape_newlines_single_line(self):
        escaped = f"{default_dialect.escape_char}\\n"
        unescaped = "\n"
        self.assertEqual(unescape_newlines(f"Line 1{escaped}Line 2", default_dialect), f"Line 1{unescaped}Line 2")

    def test_unescape_newlines_multiple_lines(self):
        escaped = f"{default_dialect.escape_char}\\n"
        unescaped = "\n"
        self.assertEqual(
            unescape_newlines(f"Line 1{escaped}Line 2{escaped}Line 3", default_dialect),
            f"Line 1{unescaped}Line 2{unescaped}Line 3",
        )

    def test_unescape_newlines_nested_list(self):
        escaped = f"{default_dialect.escape_char}\\n"
        unescaped = "\n"
        input_data = [["Line 1", f"Line 2{escaped}Line 3"], [f"Line 4{escaped}Line 5"]]
        expected_output = [["Line 1", f"Line 2{unescaped}Line 3"], [f"Line 4{unescaped}Line 5"]]
        self.assertEqual(unescape_newlines(input_data, default_dialect), expected_output)

class Test_parse_array(unittest.TestCase):
    def test_parse_array_simple(self):
        array_str = f"{default_dialect.array_start}item1{default_dialect.array_separator}item2{default_dialect.array_end}"
        expected_output = ["item1", "item2"]
        self.assertEqual(parse_array(array_str, default_dialect), expected_output)

    def test_parse_array_with_empty_items(self):
        array_str = f"{default_dialect.array_start}{default_dialect.array_separator}{default_dialect.array_separator}{default_dialect.array_end}"
        expected_output = ["", "", ""]
        self.assertEqual(parse_array(array_str, default_dialect), expected_output)

    def test_parse_array_empty(self):
        array_str = f"{default_dialect.array_start}~{default_dialect.array_end}"
        expected_output = []
        self.assertEqual(parse_array(array_str, default_dialect), expected_output)

    def test_parse_array_no_start_end(self):
        array_str = f"item1{default_dialect.array_separator}item2"
        expected_output = ["item1", "item2"]
        self.assertEqual(parse_array(array_str, default_dialect), expected_output)

if __name__ == "__main__":
    unittest.main()
