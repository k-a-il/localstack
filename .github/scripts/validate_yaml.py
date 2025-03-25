import os
import yaml
import json
from jsonschema import validate, ValidationError
import sys



def main():
    all_changed_files = os.getenv('ALL_CHANGED_FILES', '')
    features_json_schema = os.getenv('FEATURES_JSON_SCHEMA', '')
    print(all_changed_files)
    print(features_json_schema)

