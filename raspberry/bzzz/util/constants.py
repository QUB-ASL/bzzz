import json


def constants():
    with open('constants.json') as fd:
        json_data = json.load(fd)
        return json_data


if __name__ == "__main__":
    from pprint import pprint
    pprint(constants())
