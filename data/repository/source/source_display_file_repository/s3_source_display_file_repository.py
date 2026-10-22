import os
from io import BytesIO

import boto3
from botocore.client import BaseClient

from core.utils.file import File
from data.repository.source.source_display_file_repository.source_display_file_repository import \
    SourceDisplayFileRepository


class S3SourceDisplayFileRepository(SourceDisplayFileRepository):

    def __init__(self):
        self._client: BaseClient = boto3.client(
            "s3",
            region_name="eu-north-1",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )
        self._bucket_name = "hekades-source-bucket"

    def add_source_file(self, source_id: str, file: File):
        extra_args = {"Metadata": {"filename": file.filename}}
        self._client.upload_fileobj(file.file_io, self._bucket_name, source_id, ExtraArgs=extra_args)

    def get_source_file(self, source_id: str) -> File:
        try:
            file_obj = self._get_file_obj(source_id)
            metadata = self._get_file_metadata(source_id)
            filename = metadata['filename']
            return File(filename=filename, file_io=file_obj)
        except Exception as e:
            raise FileNotFoundError(f"File with source_id {source_id} not found") from e

    def _get_file_obj(self, source_id: str):
        file_obj = BytesIO()
        self._client.download_fileobj(self._bucket_name, source_id, file_obj)
        file_obj.seek(0)
        return file_obj

    def _get_file_metadata(self, source_id):
        response = self._client.head_object(Bucket=self._bucket_name, Key=source_id)
        metadata = response['Metadata']
        return metadata

    def delete_source_file(self, source_id: str):
        self._client.delete_object(Bucket=self._bucket_name, Key=source_id)
