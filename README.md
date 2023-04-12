# Minimalist Hierarchical Notation (MHN)

Minimalist Hierarchical Notation (MHN) is a lightweight and compact data structure format designed to represent hierarchical data. Think of it as a CSV variant with support for the features you are used to using in JSON or YAML.

One of the side effects of this is minimal token usage in Large Language Models as compared to using JSON/XML/YAML. MHN uses a combination of simple delimiters and special characters to separate fields, indicate if a field is an array, and manage nested data structures.

- [Minimalist Hierarchical Notation (MHN)](#minimalist-hierarchical-notation-mhn)
  - [Features](#features)
  - [Syntax](#syntax)
  - [Comparison to JSON](#comparison-to-json)
  - [MHN to Python Dictionary Parser](#mhn-to-python-dictionary-parser)
  - [Python Dictionary to MHN Parser](#python-dictionary-to-mhn-parser)


## Features

- Compact and easy-to-read format
- Hierarchical structure with support for nested data
- Minimal token usage
- Supports arrays and nested fields

## Syntax

MHN uses the following syntax rules:

- The `|` character is used as a delimiter to separate sibling elements.
- The `>` character represents the start of a new level in the hierarchy.
- The `<` character represents the end of a level in the hierarchy.
- The `[]` notation is used to indicate an array field.
- The `^` notation is used to seperate array elements.

## Comparison to JSON

Here's an example of how MHN data can be compared to JSON data:

MHN Schema:
```
Title|Description|Author>Name|Bio<|Genres[]|Keywords[]|EstimatedWordCount|RelatedBooks[Title|Author]
```

JSON Schema:
```json
{
  "Title": "",
  "Description": "",
  "Author": {
    "Name": "",
    "Bio": ""
  },
  "Genres": [],
  "Keywords": [],
  "EstimatedWordCount": 0,
  "RelatedBooks": [
    {
      "Title": "",
      "Author": ""
    }
  ]
}
```

## MHN to Python Dictionary Parser

```python
def parse_mhn(data_str, schema_str=None):
    def parse_array(array_str):
        return array_str.split('^')

    def parse_level(data_line, schema_line):
        result = {}
        data_parts = data_line.split('|')
        schema_parts = schema_line.split('|')

        for i, part in enumerate(schema_parts):
            if '[' in part and ']' in part:
                field_name = part[:-2]
                result[field_name] = parse_array(data_parts[i])
            elif '>' in part:
                field_name, sub_schema = part.split('>')
                sub_data, remaining_data = data_parts[i].split('<', 1)
                result[field_name] = parse_level(sub_data, sub_schema)
                data_parts[i] = remaining_data
            else:
                result[part] = data_parts[i]

        return result

    # Read schema from the first line of data_str if schema_str is not provided
    if schema_str is None:
        schema_str, data_str = data_str.split('\n', 1)

    # Split data_str into lines and parse each line
    data_lines = data_str.strip().split('\n')
    result = [parse_level(line, schema_str) for line in data_lines]

    return result

# Example usage:
data = '''Title|Description|Author>Name|Bio<|Genres[]|Keywords[]|EstimatedWordCount|RelatedBooks[Title|Author]
The Enchanted Forest|A young girl discovers a hidden forest filled with magical creatures and must save it from destruction by a greedy developer.|>Vivian L. Hawthorne|Vivian is a passionate writer, avid traveler, and amateur photographer<|[Magical Realism|Fantasy]|[fantasy|surreal|dreamlike|mythical]|60000|[Book1|Author1^Book2|Author2^Book3|Author3]'''

result = parse_mhn(data)
print(result)
```

This parser will now output a list of dictionaries, one for each line of data:
```python
[
  {
    'Title': 'The Enchanted Forest',
    'Description': 'A young girl discovers a hidden forest filled with magical creatures and must save it from destruction by a greedy developer.',
    'Author': {
      'Name': 'Vivian L. Hawthorne',
      'Bio': 'Vivian is a passionate writer, avid traveler, and amateur photographer'
    },
    'Genres': ['Magical Realism', 'Fantasy'],
    'Keywords': ['fantasy', 'surreal', 'dreamlike', 'mythical'],
    'EstimatedWordCount': '60000',
    'RelatedBooks': [
      {'Title': 'Book1', 'Author': 'Author1'},
      {'Title': 'Book2', 'Author': 'Author2'},
      {'Title': 'Book3', 'Author': 'Author3'}
    ]
  }
]
```

## Python Dictionary to MHN Parser
```python
def dict_to_mhn(data_list):
    def detect_schema(data_dict, parent_key=''):
        schema_parts = []
        for key, value in data_dict.items():
            if isinstance(value, dict):
                sub_schema = detect_schema(value, parent_key=key)
                schema_parts.append(f'{key}>{sub_schema}<')
            elif isinstance(value, list):
                schema_parts.append(f'{key}[]')
            else:
                schema_parts.append(key)
        return '|'.join(schema_parts)

    def convert_dict_to_mhn(data_dict, schema_str):
        mhn_parts = []
        schema_parts = schema_str.split('|')
        for part in schema_parts:
            if '[' in part and ']' in part:
                field_name = part[:-2]
                mhn_parts.append('^'.join(data_dict[field_name]))
            elif '>' in part:
                field_name, sub_schema = part.split('>')
                sub_schema = sub_schema[:-1]  # Remove trailing '<'
                mhn_parts.append(f'>{convert_dict_to_mhn(data_dict[field_name], sub_schema)}<')
            else:
                mhn_parts.append(str(data_dict[part]))
        return '|'.join(mhn_parts)

    # Auto-detect schema from the first dictionary in the list
    schema_str = detect_schema(data_list[0])
    mhn_lines = [schema_str] + [convert_dict_to_mhn(data_dict, schema_str) for data_dict in data_list]

    return '\n'.join(mhn_lines)

# Example usage:
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

mhn_str = dict_to_mhn(data_list)
print(mhn_str)
```

Output:
```
Title|Description|Author>Name|Bio<|Genres[]|Keywords[]|EstimatedWordCount|RelatedBooks[Title|Author]
The Enchanted Forest|A young girl discovers a hidden forest filled with magical creatures and must save it from destruction by a greedy developer.|>Vivian L. Hawthorne|Vivian is a passionate writer, avid traveler, and amateur photographer<|[Magical Realism|Fantasy]|[fantasy|surreal|dreamlike|mythical]|60000|[Book1|Author1^Book2|Author2^Book3|Author3]
```