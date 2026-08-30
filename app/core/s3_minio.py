from datetime import timedelta

from fastapi import UploadFile
from minio import Minio, S3Error

from app.configs import config
from app.constants.upload import ALLOWED_TYPES, MAX_SIZE
from app.logging.logger import logger


class MinioService:
    # Init MinIO connection
    def __init__(self):
        self.client = Minio(
            config.MINIO_HOST,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            region=config.MINIO_REGION,
            secure=config.ENV != "DEV",
        )

    # Get url (download/view file) in a limit time
    def get_url(
        self,
        bucket: str,
        object_name: str,
        expires_hour: int = 1,
    ) -> str | None:
        try:
            return self.client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(hours=expires_hour),
            )
        except Exception as e:
            logger.error(f"Generate url failed: {e}")
            return None

    # Upload image into MinIO
    async def upload_image(
        self,
        bucket: str,
        filename: str,
        image: UploadFile,
        extension: str | None = None,
    ):
        try:
            # Check image type
            if image.content_type not in ALLOWED_TYPES:
                return None, "Invalid image type"

            # Check image size
            file_size = image.size
            if file_size > MAX_SIZE:
                return None, "Image too large"

            # `filename` already contains the full path AND the extension
            # (e.g. books/{book_id}/cover.jpeg), so use it as-is. Appending
            # another extension here caused ".jpeg.jpeg".
            content_type = image.content_type
            file_name = filename

            self.client.put_object(
                bucket_name=bucket,
                object_name=file_name,
                data=image.file,
                length=file_size,
                content_type=content_type,
            )

            return file_name, None
        except S3Error as e:
            logger.info(
                "Upload image to MinIO failed",
                extra={
                    "bucket": bucket,
                    "filename": filename,
                    "error": str(e),
                },
            )
            raise ValueError("Upload image to MinIO failed", str(e)) from e

    # Delete file
    def delete_file(
        self,
        bucket: str,
        object_name: str,
    ):
        self.client.remove_object(bucket, object_name)


minio_service = MinioService()
