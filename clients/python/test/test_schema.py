import unittest
from mhn.dialect import Dialect
from mhn.schema import generate_schema


class TestGenerateSchema(unittest.TestCase):
    def test_generate_schema_with_single_field(self):
        data = {"Title": "The Enchanted Forest"}
        expected_schema = "Title"
        generated_schema = generate_schema(data)
        self.assertEqual(expected_schema, generated_schema)

    def test_generate_schema_with_nested_fields(self):
        data = {
            "Author": {
                "Name": "Vivian L. Hawthorne",
                "Bio": "Vivian is a passionate writer, avid traveler, and amateur photographer",
            }
        }
        expected_schema = "Author>Name|Bio<"
        generated_schema = generate_schema(data)
        self.assertEqual(expected_schema, generated_schema)

    def test_generate_schema_with_array_field(self):
        data = {"Genres": ["Magical Realism", "Fantasy"]}
        expected_schema = "Genres[]"
        generated_schema = generate_schema(data)
        self.assertEqual(expected_schema, generated_schema)

    def test_generate_schema_with_multiple_fields_and_nested_fields(self):
        data = {
            "Title": "The Enchanted Forest",
            "Author": {"Name": "Vivian L. Hawthorne"},
            "EstimatedWordCount": 60000,
        }
        expected_schema = "Title|Author>Name<|EstimatedWordCount"
        generated_schema = generate_schema(data)
        self.assertEqual(expected_schema, generated_schema)

    def test_generate_schema_with_five_layers_of_nesting(self):
        data = {
            "Level1": {
                "Value1": "Value",
                "Array1": ["A", "B", "C"],
                "Level2": {
                    "Value2": "Value",
                    "Array2": ["D", "E", "F"],
                    "Level3": {
                        "Value3": "Value",
                        "Array3": ["G", "H", "I"],
                        "Level4": {
                            "Value4": "Value",
                            "Array4": ["J", "K", "L"],
                            "Level5": {"Value5": "Value", "Array5": ["M", "N", "O"]},
                        },
                    },
                },
            }
        }
        expected_schema = (
            "Level1>Value1|Array1[]|Level2>Value2|Array2[]|Level3>Value3|Array3[]|"
            "Level4>Value4|Array4[]|Level5>Value5|Array5[]<<<<<"
        )
        generated_schema = generate_schema(data)
        self.assertEqual(expected_schema, generated_schema)

    def test_generate_schema_with_custom_dialect(self):
        data = {
            "Title": "The Enchanted Forest",
            "Author": {
                "Name": "Vivian L. Hawthorne",
                "Bio": "Vivian is a passionate writer, avid traveler, and amateur photographer",
            },
            "Genres": ["Magical Realism", "Fantasy"],
            "Keywords": ["fantasy", "surreal", "dreamlike", "mythical"],
            "EstimatedWordCount": 60000,
        }
        custom_dialect = Dialect(
            delimiter=";",
            level_start="(",
            level_end=")",
            array_start="{",
            array_end="}",
            array_separator=",",
        )
        expected_schema = (
            "Title;Author(Name;Bio);Genres{};Keywords{};EstimatedWordCount"
        )
        generated_schema = generate_schema(data, dialect=custom_dialect)
        self.assertEqual(expected_schema, generated_schema)

    def test_generate_schema_with_array_of_nested_objects(self):
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
        expected_schema = "books[Title|Author>Name<|EstimatedWordCount]"
        generated_schema = generate_schema(data)
        self.assertEqual(expected_schema, generated_schema)


if __name__ == "__main__":
    unittest.main()
