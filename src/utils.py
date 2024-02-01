import json
import yaml

from pathlib import Path


def read_yaml(yaml_path):
    with open(yaml_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def read_json(filepath) -> None | list[dict] | list | list[dict]:
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


def save_data_to_json(data_object: list | list[dict], filepath: Path):
    with open(filepath, "w") as file:
        json.dump(data_object, file)


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


def rename_keys(data, mapping):
    """
    Renames keys in a dictionary according to a mapping.

    Args:
        data (dict): The dictionary to rename keys in.
        mapping (dict): The mapping from old keys to new keys.

    Returns:
        dict: The dictionary with the keys renamed.
    """

    # if isinstance list[dict] apply to each dict in list
    if isinstance(data, list):
        for d in data:
            rename_keys(d, mapping)
        return data

    # Check that the data is a dictionary

    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")

    if not isinstance(mapping, dict):
        raise ValueError("mapping must be a dictionary")

    # Rename the keys
    for key, value in mapping.items():
        data[value] = data.pop(key)
    return data


def clean_text_field(text: str) -> str:
    text = (
        text.replace("description:", "").replace("ref.", "ref ").replace("&amp;", " ")
    )

    text = text.lower()
    return text


def today():
    from datetime import datetime

    return datetime.today().strftime("%Y-%m-%d")


def get_flow(amount: float):
    if amount > 0:
        return "credit"
    elif amount < 0:
        return "debit"
    else:
        raise ValueError()


def get_amount(amount: float):
    if amount > 0:
        return amount
    elif amount < 0:
        return -amount
    else:
        raise ValueError()


def get_balance(balance: float):
    if balance > 0:
        return balance
    elif balance < 0:
        return -balance
    else:
        raise ValueError()
