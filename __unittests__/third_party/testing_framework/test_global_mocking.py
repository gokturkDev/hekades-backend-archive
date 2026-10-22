from unittest import mock

from . import global_class_import_test
from . import global_variable_test

test_content = "Hey there!"


class MockDummyFile:
    file = list(test_content)


class TestGlobalVariableMocking:

    def test_global_variable_mock(self):
        mock_file = mock.patch.object(
            global_variable_test, 'file', list(test_content)
        )
        with mock_file:
            assert global_variable_test.read_file() == test_content

    def test_global_class_mock(self):
        mock_dummy_file = mock.patch.object(
            global_class_import_test, 'DummyFile', MockDummyFile
        )
        with mock_dummy_file:
            assert global_class_import_test.read_file() == test_content
