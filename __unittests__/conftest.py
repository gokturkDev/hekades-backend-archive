# conftest.py
import pytest
from dotenv import load_dotenv
from os.path import join, dirname


def pytest_sessionstart(session):
    """ Load environment variables before test session starts """
    load_dotenv(dotenv_path=join(dirname(__file__), ".env"))
