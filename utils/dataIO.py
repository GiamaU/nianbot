import json
from collections import namedtuple


def get_Info(file: str, namedt: bool = True):
    try:
        with open(file, "r", encoding='utf8') as data:
            if namedt:
                return json.load(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            else:
                return json.load(data)
    except AttributeError:
        print("Unknown argument")
    except FileNotFoundError:
        print(f"JSON {file} wasn't found")


def set_Info(items, file: str, method: str = 'w'):
    try:
        with open(file, method, encoding='utf8') as data:
            data.write(json.dumps(items, indent=4, sort_keys=True))
    except AttributeError:
        print("Unknown argument")
    except FileNotFoundError:
        print(f"JSON {file} wasn't found")


def update_Info(items, file):
    if items is not None:
        data = get_Info(file, False)
        for item in reversed(items):
            data.insert(0, dict(item))
        set_Info(data, file, 'w')


def change_value(file: str, value: str, changeto: str):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    data[value] = changeto
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)
