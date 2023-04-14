import unittest
import io
from mhn.dialect import Dialect
from mhn.writer import DictWriter
from mhn.schema import generate_schema


class TestDictWriter(unittest.TestCase):
    def test_write_single_field_array(self):
        data = {
            "Hobbies": ["reading", "writing", "traveling"],
        }
        expected_output = (
            "Hobbies[]\n"
            "reading^writing^traveling"
        )

        schema = generate_schema(data)
        output = io.StringIO()
        writer = DictWriter(output, schema)
        writer.writeheader()
        writer.writerow(data)

        self.assertEqual(expected_output, output.getvalue())
        
    def test_write_single_nested_object(self):
        data = {
            "Author": {"Name": "Vivian L. Hawthorne", "Age": 42},
        }
        expected_output = (
            "Author>Name|Age<\n"
            ">Vivian L. Hawthorne|42<"
        )

        schema = generate_schema(data)
        output = io.StringIO()
        writer = DictWriter(output, schema)
        writer.writeheader()
        writer.writerow(data)

        self.assertEqual(expected_output, output.getvalue())
        
    def test_write_single_row_with_default_dialect(self):
        data = {
            "Name": "John",
            "Age": 30,
            "Hobbies": ["reading", "writing", "traveling"],
        }
        schema = generate_schema(data)
        expected_output = "Name|Age|Hobbies[]\nJohn|30|reading^writing^traveling"

        output = io.StringIO()
        writer = DictWriter(output, schema)
        writer.writeheader()
        writer.writerow(data)
        self.assertEqual(expected_output, output.getvalue())

    def test_write_single_row_with_custom_dialect(self):
        data = {
            "Name": "John",
            "Age": 30,
            "Hobbies": ["reading", "writing", "traveling"],
        }
        custom_dialect = Dialect(
            delimiter=";",
            level_start="(",
            level_end=")",
            array_start="{",
            array_end="}",
            array_separator=",",
        )
        schema = generate_schema(data, dialect=custom_dialect)
        expected_output = "Name;Age;Hobbies{}\nJohn;30;reading,writing,traveling"

        output = io.StringIO()
        writer = DictWriter(output, schema, dialect=custom_dialect)
        writer.writeheader()
        writer.writerow(data)
        self.assertEqual(expected_output, output.getvalue())

    def test_write_ten_rows_with_double_nested_data(self):
        data_rows = [
            {
                "Id": i,
                "User": {"Name": f"Name {i}", "Age": 20 + i},
                "Address": {"City": f"City {i}", "Country": f"Country {i}"},
            }
            for i in range(1, 11)
        ]
        schema = "Id|User>Name|Age<|Address>City|Country<"
        expected_output = ["Id|User>Name|Age<|Address>City|Country<"]
        expected_output.extend(
            [f"{i}|>Name {i}|{20 + i}<|>City {i}|Country {i}<" for i in range(1, 11)]
        )
        expected_output = "\n".join(expected_output)

        output = io.StringIO()
        writer = DictWriter(output, schema)
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)
        self.assertEqual(expected_output, output.getvalue())

    def test_write_with_newlines(self):
        data_rows = [
            {
                "Id": 1,
                "Name": "John",
                "Address": {
                    "Line1": "123 Main St.",
                    "Line2": "Apt. 5B\nBig City",
                    "ZipCode": 12345,
                },
                "Tags": ["Python", "Django\nORM", "Flask"],
            },
            {
                "Id": 2,
                "Name": "Jane",
                "Address": {
                    "Line1": "456 Elm St.\nSuite 12",
                    "Line2": "",
                    "ZipCode": 54321,
                },
                "Tags": ["Java", "Spring", "Hibernate\nORM"],
            },
        ]

        expected_output = (
            "Id|Name|Address>Line1|Line2|ZipCode<|Tags[]\n"
            "1|John|>123 Main St.|Apt. 5B\\nBig City|12345<|Python^Django\\nORM^Flask\n"
            "2|Jane|>456 Elm St.\\nSuite 12||54321<|Java^Spring^Hibernate\\nORM"
        )

        output = io.StringIO()
        writer = DictWriter(
            output, schema="Id|Name|Address>Line1|Line2|ZipCode<|Tags[]"
        )
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)

        self.assertEqual(expected_output, output.getvalue())

    def test_write_with_control_chars(self):
        self.maxDiff = None
        data = {
            "Field1": "Value with >",
            "Field2": "Value with <",
            "Field3": "Value with |",
            "Field4": "Value with [",
            "Field5": "Value with ]",
            "Field6": "Value with ^",
            "Field7": "Value with \n",
            "Nested": {
                "Field8": "Nested value with >",
                "Field9": "Nested value with <",
                "Field10": "Nested value with |",
                "Field11": "Nested value with [",
                "Field12": "Nested value with ]",
                "Field13": "Nested value with ^",
                "Field14": "Nested value with \n",
            },
            "Array": [
                "Value with >",
                "Value with <",
                "Value with |",
                "Value with [",
                "Value with ]",
                "Value with ^",
                "Value with \n",
            ],
        }

        schema = generate_schema(data)

        expected_output = (
            schema
            + "\n"
            + r"Value with \>|Value with \<|Value with \||Value with \[|Value with \]|Value with \^|Value with \n|>Nested value with \>|Nested value with \<|Nested value with \||Nested value with \[|Nested value with \]|Nested value with \^|Nested value with \n<|Value with \>^Value with \<^Value with \|^Value with \[^Value with \]^Value with \^^Value with \n"
        )

        output = io.StringIO()
        writer = DictWriter(output, schema)
        writer.writeheader()
        writer.writerow(data)

        self.assertEqual(expected_output, output.getvalue().strip())

    def test_write_data_with_array_of_nested_objects(self):
        data = {
            "books": [
                {
                    "Title": "The Enchanted Forest",
                    "Author": {"Name": "Vivian L. Hawthorne"},
                    "EstimatedWordCount": 60000,
                },
                {
                    "Title": "The Invisible Man",
                    "Author": {"Name": "H.G. Wells"},
                    "EstimatedWordCount": 40000,
                },
            ]
        }

        expected_output = (
            "books[Title|Author>Name<|EstimatedWordCount]\n"
            "The Enchanted Forest|>Vivian L. Hawthorne<|60000^"
            "The Invisible Man|>H.G. Wells<|40000"
        )

        schema = "books[Title|Author>Name<|EstimatedWordCount]"
        output = io.StringIO()
        writer = DictWriter(output, schema)
        writer.writeheader()
        writer.writerow(data)

        self.assertEqual(expected_output, output.getvalue())

    def test_write_data_with_three_layers_of_arrays_containing_structs(self):
        self.maxDiff = None
        data = {
            "Countries": [
                {
                    "Name": "CountryA",
                    "Cities": [
                        {
                            "Name": "CityA1",
                            "Attractions": [
                                {"Name": "AttractionA1", "Type": "Museum"},
                                {"Name": "AttractionA2", "Type": "Park"},
                            ],
                        },
                        {
                            "Name": "CityA2",
                            "Attractions": [
                                {"Name": "AttractionA3", "Type": "Beach"},
                                {"Name": "AttractionA4", "Type": "Zoo"},
                            ],
                        },
                    ],
                },
                {
                    "Name": "CountryB",
                    "Cities": [
                        {
                            "Name": "CityB1",
                            "Attractions": [
                                {"Name": "AttractionB1", "Type": "Museum"},
                                {"Name": "AttractionB2", "Type": "Park"},
                            ],
                        },
                        {
                            "Name": "CityB2",
                            "Attractions": [
                                {"Name": "AttractionB3", "Type": "Beach"},
                                {"Name": "AttractionB4", "Type": "Zoo"},
                            ],
                        },
                    ],
                },
            ],
        }

        schema = generate_schema(data)
        expected_output = (
            f"{schema}\n"
            "CountryA|CityA1|AttractionA1|Museum^AttractionA2|Park^CityA2|AttractionA3|Beach^AttractionA4|Zoo^"
            "CountryB|CityB1|AttractionB1|Museum^AttractionB2|Park^CityB2|AttractionB3|Beach^AttractionB4|Zoo"
        )

        output = io.StringIO()
        writer = DictWriter(output, schema)
        writer.writeheader()
        writer.writerow(data)

        self.assertEqual(expected_output, output.getvalue())


if __name__ == "__main__":
    unittest.main()
