import secrets

from slugify import slugify


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def make_slug(text: str) -> str:
    return slugify(text)
