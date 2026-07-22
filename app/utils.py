from slugify import slugify


def make_slug(text: str) -> str:
    return slugify(text)
