import secrets
from datetime import UTC, datetime

from slugify import slugify
from sqlalchemy.orm import Session

from app.models import Product


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def make_slug(text: str) -> str:
    return slugify(text)


def make_unique_slug(db: Session, name: str) -> str:
    base = make_slug(name)
    slug = base
    while db.query(Product).filter_by(slug=slug).first() is not None:
        slug = f"{base}-{secrets.token_hex(2)}"
    return slug


def generate_order_number() -> str:
    now = datetime.now(UTC)
    random_part = secrets.token_hex(3).upper()
    return f"ORD-{now:%Y%m%d}-{random_part}"
