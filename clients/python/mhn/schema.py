from .dialect import Dialect, default_dialect


def generate_schema(
    data_dict: dict, dialect: Dialect = default_dialect, parent_key=""
) -> str:
    schema_parts = []
    for key, value in data_dict.items():
        if isinstance(value, dict):
            sub_schema = generate_schema(value, dialect=dialect, parent_key=key)
            schema_parts.append(
                f"{key}{dialect.level_start}{sub_schema}{dialect.level_end}"
            )
        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            # handle arrays of nested objects
            sub_schema = generate_schema(value[0], dialect=dialect, parent_key="")
            schema_parts.append(f"{key}{dialect.array_start}{sub_schema}{dialect.array_end}")
        elif isinstance(value, list):
            schema_parts.append(f"{key}{dialect.array_start}{dialect.array_end}")
        else:
            schema_parts.append(key)
    return dialect.delimiter.join(schema_parts)

def parse_schema_parts(schema_str:str, dialect:Dialect):
    parts = []
    part_start = 0
    nesting_level = 0

    for idx, char in enumerate(schema_str):
        if char == dialect.level_start or char == dialect.array_start:
            nesting_level += 1
        elif char == dialect.level_end or char == dialect.array_end:
            nesting_level -= 1
        elif char == dialect.delimiter and nesting_level == 0:
            parts.append(schema_str[part_start:idx])
            part_start = idx + 1

    parts.append(schema_str[part_start:])
    return parts