from __unittests__.third_party.testing_framework.dummy_file import DummyFile


def read_file() -> str:
    file = DummyFile.file
    result = ""
    for line in file:
        result += line
    return result
