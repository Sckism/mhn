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
        elif isinstance(value, list):
            schema_parts.append(f"{key}{dialect.array_start}{dialect.array_end}")
        else:
            schema_parts.append(key)
    return dialect.delimiter.join(schema_parts)
