from dataclasses import dataclass
from typing import IO


@dataclass
class File:
    filename: str
    file_io: IO

    def is_empty(self) -> bool:
        current_position = self.file_io.tell()
        is_empty = len(self.file_io.read(1)) == 0
        self.file_io.seek(current_position)
        return is_empty

    @property
    def file_extension(self) -> str:
        if "." not in self.filename:
            return ""
        return self.filename.split(".")[-1]
