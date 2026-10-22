from dataclasses import dataclass

from business.entity.source.source_info import SourceInfo
from core.utils.file import File


@dataclass
class SourceEntity:
    info: SourceInfo
    file: File
