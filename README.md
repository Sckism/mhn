# Minimalist Hierarchical Notation (MHN)

[![Python package](https://github.com/Sckism/mhn/actions/workflows/python-package.yml/badge.svg)](https://github.com/Sckism/mhn/actions/workflows/python-package.yml)


Minimalist Hierarchical Notation (MHN) is a lightweight and compact data structure format designed to represent hierarchical data. Think of it as a CSV variant with support for the features you are used to using in JSON or YAML. One of the side effects of this is minimal token usage in Large Language Models as compared to using JSON/XML/YAML. MHN uses a combination of simple delimiters and special characters to separate fields, indicate if a field is an array, and manage nested data structures.

## Features

- Compact and human-readable format
- Supports nesting and arrays
- Reduces token usage in Large Language Models compared to JSON/XML/YAML

## Installation

```sh
pip install sckism-mhn
```

## Example Usage
```python
import io
from mhn import DictWriter, DictReader, generate_schema

data_list = [
  {
    'Title': 'The Enchanted Forest',
    'Description': 'A young girl discovers a hidden forest filled with magical creatures and must save it from destruction by a greedy developer.',
    'Author': {
      'Name': 'Vivian L. Hawthorne',
      'Bio': 'Vivian is a passionate writer, avid traveler, and amateur photographer'
    },
    'Genres': ['Magical Realism', 'Fantasy'],
    'Keywords': ['fantasy', 'surreal', 'dreamlike', 'mythical'],
    'EstimatedWordCount': 60000,
    'RelatedBooks': [
      {'Title': 'Book1', 'Author': 'Author1'},
      {'Title': 'Book2', 'Author': 'Author2'},
      {'Title': 'Book3', 'Author': 'Author3'}
    ]
  }
]

# Writing data as MHN
schema = generate_schema(data_list[0])
output = io.StringIO()
writer = DictWriter(output, schema)
writer.writeheader()
writer.writerows(data_list)

# Reading MHN data
mhn_str = output.getvalue()
reader = DictReader(io.StringIO(mhn_str), schema=schema)
for row in reader:
    print(row)
```

## Writing Data
Use the `DictWriter` class to write data as MHN:
```python
import io
from mhn import DictWriter, generate_schema

data = {
    "Name": "John",
    "Age": 30,
    "Hobbies": ["reading", "writing", "traveling"],
}
schema = generate_schema(data)
output = io.StringIO()

writer = DictWriter(output, schema)
writer.writeheader()
writer.writerow(data)
```

## Reading Data
Use the `DictReader` class to read MHN data:
```python
from io import StringIO
from mhn import DictReader

data_str = "Id|Name|Age\n1|Alice|30\n2|Bob|25"
reader = DictReader(StringIO(data_str), read_schema_from_first_row=True)

for row in reader:
    print(row)
```

## Running Tests
To run tests, you can use the following commands:
```sh
python -m unittest discover
```

## License
MIT
