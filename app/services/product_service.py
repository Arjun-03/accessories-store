from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Product, ProductImage
from app.utils import make_unique_slug


def get_active_products(db: Session) -> list[Product]:
    stmt = (
        select(Product)
        .where(Product.is_active.is_(True))
        .options(joinedload(Product.category), joinedload(Product.images))
        .order_by(Product.created_at.desc())
    )
    return list(db.execute(stmt).unique().scalars().all())


def get_product_by_slug(db: Session, slug: str) -> Product | None:
    stmt = (
        select(Product)
        .where(Product.slug == slug, Product.is_active.is_(True))
        .options(joinedload(Product.category), joinedload(Product.images))
    )
    return db.execute(stmt).unique().scalars().first()


def list_all_products(db: Session) -> list[Product]:
    stmt = select(Product).options(joinedload(Product.category)).order_by(Product.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def create_product(
    db: Session,
    *,
    name: str,
    category_id: int,
    price: Decimal,
    discount_price: Decimal | None,
    description: str | None,
    sku: str | None,
    stock_quantity: int,
    image_url: str | None,
) -> Product:
    product = Product(
        name=name,
        slug=make_unique_slug(db, name),
        category_id=category_id,
        price=price,
        discount_price=discount_price,
        description=description,
        sku=sku or None,
        stock_quantity=stock_quantity,
    )
    db.add(product)
    db.flush()  # assign product.id before creating the image

    if image_url:
        db.add(ProductImage(product_id=product.id, url=image_url, is_primary=True))

    db.commit()
    db.refresh(product)
    return product
