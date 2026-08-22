from pathlib import Path
from django.core.exceptions import ValidationError


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def validate_image_upload(file_obj):
    suffix = Path(file_obj.name).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Unsupported image extension.")
    if file_obj.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError("Image file is too large.")
