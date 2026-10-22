from os.path import join, dirname


class DummyFile:
    file = open(join(dirname(__file__), "dummy"), "rt")
