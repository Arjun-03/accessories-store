from decimal import Decimal

from app.services import product_service


def test_create_product(db_session, category):
    product = product_service.create_product(
        db_session,
        name="Rose Gold Almond",
        category_id=category.id,
        price=Decimal("1500.00"),
        discount_price=None,
        description="A set.",
        sku="PON-001",
        stock_quantity=10,
        image_url=None,
    )
    assert product.id is not None
    assert product.slug == "rose-gold-almond"
    assert product.stock_quantity == 10


def test_create_product_generates_unique_slug(db_session, category):
    first = product_service.create_product(
        db_session,
        name="Same Name",
        category_id=category.id,
        price=Decimal("100.00"),
        discount_price=None,
        description=None,
        sku=None,
        stock_quantity=1,
        image_url=None,
    )
    second = product_service.create_product(
        db_session,
        name="Same Name",
        category_id=category.id,
        price=Decimal("100.00"),
        discount_price=None,
        description=None,
        sku=None,
        stock_quantity=1,
        image_url=None,
    )
    assert first.slug == "same-name"
    assert second.slug != first.slug  # collision handled
    assert second.slug.startswith("same-name")


def test_update_product_keeps_slug_on_rename(db_session, sample_product):
    original_slug = sample_product.slug
    product_service.update_product(
        db_session,
        sample_product,
        name="Completely New Name",
        category_id=sample_product.category_id,
        price=sample_product.price,
        discount_price=None,
        description=sample_product.description,
        sku=sample_product.sku,
        stock_quantity=sample_product.stock_quantity,
        new_image_url=None,
    )
    assert sample_product.name == "Completely New Name"
    assert sample_product.slug == original_slug  # slug did NOT change


def test_toggle_product_active(db_session, sample_product):
    assert sample_product.is_active is True
    product_service.toggle_product_active(db_session, sample_product)
    assert sample_product.is_active is False
    product_service.toggle_product_active(db_session, sample_product)
    assert sample_product.is_active is True


def test_product_admin_routes_block_anonymous(client, sample_product):
    routes = [
        client.get("/admin/products", follow_redirects=False),
        client.get("/admin/products/new", follow_redirects=False),
        client.get(f"/admin/products/{sample_product.id}/edit", follow_redirects=False),
    ]
    for response in routes:
        assert response.status_code == 303
