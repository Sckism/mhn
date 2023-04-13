import unittest
import io
from mhn.dialect import Dialect
from mhn.writer import DictWriter
from mhn.schema import generate_schema


class TestDictWriter(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
