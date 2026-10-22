from os.path import join, dirname

from dotenv import load_dotenv


class TestLlamaIndex:
    def setup_method(self):
        load_dotenv(dotenv_path=join(dirname(__file__), ".env"))
