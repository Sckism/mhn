
"""
mhn.py - read/write/investigate MHN files
"""

from .dialect import Dialect

default_dialect = Dialect()

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

def dict_to_mhn(data_list):

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