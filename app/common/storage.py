import uuid

import boto3
from fastapi import File, UploadFile

from app.core.config import settings

session = boto3.session.Session()
client = session.client(
    "s3",
    region_name="fra1",  # Your region
    endpoint_url=settings.bucket_endpoint,
    aws_access_key_id=settings.bucket_access_key_id,
    aws_secret_access_key=settings.bucket_access_key,
)


class FileStorage:
    bucket_name: str

    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name

    def upload(self, file: UploadFile = File(...)) -> str:
        key = f"{file.filename}-{uuid.uuid4()}"
        client.put_object(
            Bucket=self.bucket_name, Key=key, Body=file.file, ACL="public-read", ContentType=file.content_type
        )
        file_url = f"{settings.bucket_endpoint}/{self.bucket_name}/{key}"
        return file_url


def upload_test_result(results_photo: UploadFile) -> str:
    return FileStorage(bucket_name=settings.test_results_bucket_name).upload(results_photo)
