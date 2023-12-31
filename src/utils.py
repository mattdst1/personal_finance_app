import json


def read_json(filepath):
    filepath = str(filepath)

    try:
        with open(filepath, "r") as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {filepath}: {e}")
        return None


def to_snake_case_with_dots(column_name):
    result = column_name[0].lower()
    for char in column_name[1:]:
        if char.isupper():
            result += "_" + char.lower()
        elif char == ".":
            result += char
        else:
            result += char
    return result


def keep_text_right_of_dot(column):
    if "." not in column:
        return column

    result = column.split(".")[-1]
    return result


def clean_column_names(data):
    def clean(d):
        return {
            keep_text_right_of_dot(to_snake_case_with_dots(key)): value
            for key, value in d.items()
        }

    if isinstance(data, dict):
        return clean(data)

    if isinstance(data, list):
        cleaned_data = [clean(entry) for entry in data]

    return cleaned_data


def flatten_and_remove_duplicates_from_dictionary(data):
    flattened_data = []
    seen = set()

    for entry in data:
        flattened_entry = {}
        for key, value in entry.items():
            if isinstance(value, dict):
                flattened_entry.update(value)
            else:
                flattened_entry[key] = value

        flattened_tuple = tuple(flattened_entry.items())
        if flattened_tuple not in seen:
            seen.add(flattened_tuple)
            flattened_data.append(flattened_entry)

    return flattened_data
