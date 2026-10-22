import tempfile
from pathlib import Path

from core.utils.file import File


class TestFileFactory:

    @staticmethod
    def create_test_file_from_string(test_file_name: str, test_content: bytes) -> File:
        test_file = tempfile.NamedTemporaryFile(mode="w+b", delete=False)
        test_file.name = test_file_name
        test_file.write(test_content)
        test_file.seek(0)
        test_file = File(filename=test_file.name, file_io=test_file)
        return test_file

    @staticmethod
    def create_test_file_from_path(test_file_path) -> File:
        test_file_path = Path(test_file_path)
        test_file_name = test_file_path.name
        test_file = File(filename=test_file_name, file_io=open(test_file_path, "rb"))
        return test_file
