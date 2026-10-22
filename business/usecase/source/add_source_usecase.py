import shutil
from tempfile import SpooledTemporaryFile

from fastapi.exceptions import RequestValidationError

from business.ai.source_indexer import SourceIndexer
from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import SourceInfo, IndexingStatus, SourceType
from business.repository.source.source_repository import SourceRepository
from business.usecase.source.use_case_with_source_repo import UsecaseWithSourceRepository
from core.utils.file import File


class AddSourceUsecase(UsecaseWithSourceRepository):

    def __init__(self, source_repository: SourceRepository, indexer: SourceIndexer):
        super().__init__(source_repository)
        self.indexer = indexer

    def execute(self, name: str, link: str, source_uuid: str, index_file: File, display_file: File):
        self._raise_error_if_files_not_valid(index_file, display_file)

        display_source = SourceEntity(
            info=SourceInfo(
                id=source_uuid,
                status=IndexingStatus.NOT_STARTED,
                name=name,
                type=SourceType.DISPLAY,
                link=link
            ),
            file=display_file
        )

        self._repo.add_source(display_source)
        index_source = SourceEntity(
            info=SourceInfo(
                id=source_uuid,
                status=IndexingStatus.NOT_STARTED,
                name=name,
                type=SourceType.INDEX
            ),
            file=index_file
        )
        self.indexer.index_source(index_source, self._indexing_finished_callback)

    def _indexing_finished_callback(self, info: SourceInfo):
        self._repo.update_source_info(info)

    @staticmethod
    def _copy_file(source_file: File) -> File:
        # Assuming `source_file` is your SpooledTemporaryFile
        source_file.file_io.seek(0)  # Ensure you're at the start of the file

        # Create a new SpooledTemporaryFile
        destination_file_io = SpooledTemporaryFile()

        # Copy the content
        shutil.copyfileobj(source_file.file_io, destination_file_io)

        # Reset the file pointers
        source_file.file_io.seek(0)
        destination_file_io.seek(0)
        return File(
            filename=source_file.filename,
            file_io=destination_file_io
        )

    @staticmethod
    def _raise_error_if_files_not_valid(index_file: File, display_file: File):
        if not index_file or not display_file:
            raise RequestValidationError("Both index and display files are required.")
        if index_file.is_empty() or display_file.is_empty():
            raise RequestValidationError("Both index and display files should not be empty.")
        if index_file.file_extension == "" or display_file.file_extension == "":
            raise RequestValidationError("Both index and display files should have a valid extension.")
