import json
import os

import yaml
from jsonschema import validate, ValidationError
import sys

def load_yaml_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"YAML file not found: {file_path}")
        sys.exit(1)

def load_json_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON schema: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Schema file not found: {file_path}")
        sys.exit(1)

def validate_yaml_against_schema(yaml_data, json_schema):
    try:
        validate(instance=yaml_data, schema=json_schema)
        print("Validation successful, the YAML file matches JSON schema")
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Failed at path: {' -> '.join(str(x) for x in e.path)}")
        return False

def main():
    all_changed_files = os.getenv('ALL_CHANGED_FILES', '')
    features_schema_path = os.getenv('FEATURES_JSON_SCHEMA', '')
    yaml_files = [all_changed_files]
    print(all_changed_files)
    print(features_schema_path)
    features_schema = load_json_file(features_schema_path)
    for file_path in yaml_files:
        print(file_path)
        features_file = load_yaml_file(file_path)
        validate_yaml_against_schema(features_file, features_schema)


if __name__ == "__main__":
    main()
