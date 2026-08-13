from app.configs import config
from app.core.s3_minio import minio_service


# Convert MinIO Object to URL
def resolve_images(image_name: str | None) -> str | None:
    """Convert MinIO object name to presigned URL."""

    if not image_name:
        return image_name

    url = minio_service.get_url(config.MINIO_BUCKET, image_name)
    return url if url else image_name
