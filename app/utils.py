import secrets
from datetime import UTC, datetime

from slugify import slugify


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def make_slug(text: str) -> str:
    return slugify(text)


def generate_order_number() -> str:
    now = datetime.now(UTC)
    random_part = secrets.token_hex(3).upper()
    return f"ORD-{now:%Y%m%d}-{random_part}"
