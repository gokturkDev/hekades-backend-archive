from os.path import join, dirname

from dotenv import load_dotenv

from main.hekades_logger import configure_logger


def pytest_sessionstart(session):
    """ Load environment variables before test session starts """
    load_dotenv(dotenv_path=join(dirname(__file__), ".env"))
    configure_logger()
