from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Product


def get_active_products(db: Session) -> list[Product]:
    stmt = (
        select(Product)
        .where(Product.is_active.is_(True))
        .options(joinedload(Product.category))
        .order_by(Product.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())
