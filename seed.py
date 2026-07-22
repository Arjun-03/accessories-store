from decimal import Decimal

from app.db import SessionLocal
from app.models import Category, Product
from app.utils import make_slug


def seed():
    db = SessionLocal()
    try:
        category = db.query(Category).filter_by(slug="press-on-nails").first()
        if category is None:
            category = Category(
                name="Press-on Nails",
                slug=make_slug("Press-on Nails"),
                description="Handmade, reusable press-on nail sets.",
            )
            db.add(category)
            db.flush()
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")

        products = [
            {
                "name": "Rose Gold Almond",
                "price": "1500.00",
                "stock_quantity": 12,
                "sku": "PON-RGA-001",
                "description": "Almond-shaped set with a rose gold shimmer.",
            },
            {
                "name": "Matte Black Coffin",
                "price": "1800.00",
                "stock_quantity": 5,
                "sku": "PON-MBC-002",
                "description": "Bold matte black in a long coffin shape.",
            },
            {
                "name": "French Tip Classic",
                "price": "1400.00",
                "stock_quantity": 20,
                "sku": "PON-FTC-003",
                "discount_price": "1200.00",
                "description": "Timeless French tips, everyday wear.",
            },
        ]

        created = 0
        for data in products:
            slug = make_slug(data["name"])
            if db.query(Product).filter_by(slug=slug).first() is not None:
                continue
            db.add(
                Product(
                    category_id=category.id,
                    name=data["name"],
                    slug=slug,
                    description=data["description"],
                    price=Decimal(data["price"]),
                    discount_price=Decimal(data["discount_price"])
                    if "discount_price" in data
                    else None,
                    sku=data["sku"],
                    stock_quantity=data["stock_quantity"],
                )
            )
            created += 1

        db.commit()
        print(f"Seed complete. Products created this run: {created}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
