import io
import secrets

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

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
    (UPLOAD_DIR / filename).write_bytes(contents)

    return f"/static/uploads/{filename}"
