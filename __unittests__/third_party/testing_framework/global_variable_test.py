from os.path import join, dirname

file = open(join(dirname(__file__), "dummy"), "rt")


def read_file() -> str:
    result = ""
    for line in file:
        result += line
    return result
