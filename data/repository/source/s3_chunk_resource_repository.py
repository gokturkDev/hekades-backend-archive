import io

import boto3
from botocore.exceptions import NoCredentialsError

from business.repository.source.chunk_resource_repository import ChunkResourceRepository
from core.utils.file import File


class S3ChunkResourceRepository(ChunkResourceRepository):
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket_name = "hekades-chunk-resources"

    def store_chunk_resource(self, source_id: str, chunk_id: str, resource: File):
        try:
            self.s3.upload_fileobj(resource.file_io, self.bucket_name, f'{source_id}/{chunk_id}')
        except NoCredentialsError:
            print("No AWS credentials found")

    def get_chunk_resource(self, source_id: str, chunk_id: str) -> File:
        try:
            resp_file = io.BytesIO()
            self.s3.download_fileobj(self.bucket_name, f'{source_id}/{chunk_id}', resp_file)
            resp_file.seek(0)
            return File(filename=f'{chunk_id}', file_io=resp_file)
        except NoCredentialsError:
            print("No AWS credentials found")

    def get_chunk_resource_url(self, source_id: str, chunk_id: str) -> str:
        return f'https://{self.bucket_name}.s3.amazonaws.com/{source_id}/{chunk_id}'

    def delete_all_chunk_resources_of_source(self, source_id: str):
        try:
            self.s3.delete_objects(Bucket=self.bucket_name, Delete={'Objects': [{'Key': f'{source_id}/'}]})
        except NoCredentialsError:
            print("No AWS credentials found")

    def delete_chunk_resource(self, source_id: str, chunk_id: str):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=f'{source_id}/{chunk_id}')
        except NoCredentialsError:
            print("No AWS credentials found")
