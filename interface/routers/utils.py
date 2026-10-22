import json


def get_json_line(json_dict: dict) -> str:
    return json.dumps(json_dict) + "\n"
