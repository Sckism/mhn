import unittest
from io import StringIO
from mhn.dialect import Dialect
from mhn.reader import DictReader


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


if __name__ == "__main__":
    unittest.main()
