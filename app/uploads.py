import io
import secrets

import boto3
from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.config import settings
from app.templating import BASE_DIR

UPLOAD_DIR = BASE_DIR / "static" / "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
EXTENSION_FOR_FORMAT = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def save_product_image(file: UploadFile) -> str:
    contents = file.file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be 5 MB or smaller.",
        )

    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid image.",
        ) from None

    if image.format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be JPEG, PNG, or WebP.",
        )

    filename = secrets.token_hex(16) + EXTENSION_FOR_FORMAT[image.format]

    if settings.use_s3:
        return _save_to_s3(contents, filename, image.format)
    return _save_to_disk(contents, filename)


def _save_to_disk(contents: bytes, filename: str) -> str:
    (UPLOAD_DIR / filename).write_bytes(contents)
    return f"/static/uploads/{filename}"


def _save_to_s3(contents: bytes, filename: str, image_format: str) -> str:
    key = f"uploads/{filename}"
    content_type = f"image/{image_format.lower()}"
    s3 = boto3.client("s3", region_name=settings.aws_region)
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=contents,
        ContentType=content_type,
    )
    return f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"
