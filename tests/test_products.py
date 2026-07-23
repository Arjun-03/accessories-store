from decimal import Decimal

from app.models import Category, Product


def test_list_products_returns_active_products(client, db_session):
    # Arrange: put a known category + product in the test database
    category = Category(name="Nails", slug="nails")
    db_session.add(category)
    db_session.flush()
    db_session.add(
        Product(
            category_id=category.id,
            name="Test Set",
            slug="test-set",
            price=Decimal("1500.00"),
            stock_quantity=10,
        )
    )
    db_session.commit()

    # Act: call the endpoint
    response = client.get("/api/products")

    # Assert: it worked, and returned our product correctly
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Set"
    assert data[0]["price"] == "1500.00"
    assert data[0]["category"]["name"] == "Nails"


def test_list_products_excludes_inactive_products(client, db_session):
    # Arrange: one active product, one inactive
    category = Category(name="Nails", slug="nails")
    db_session.add(category)
    db_session.flush()
    db_session.add_all(
        [
            Product(
                category_id=category.id,
                name="Visible",
                slug="visible",
                price=Decimal("1500.00"),
                stock_quantity=5,
                is_active=True,
            ),
            Product(
                category_id=category.id,
                name="Hidden",
                slug="hidden",
                price=Decimal("1600.00"),
                stock_quantity=5,
                is_active=False,
            ),
        ]
    )
    db_session.commit()

    # Act
    response = client.get("/api/products")

    # Assert: only the active one comes back
    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert names == ["Visible"]


def test_get_product_by_slug_returns_product(client, sample_product):
    response = client.get("/api/products/rose-gold-almond")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rose Gold Almond"
    assert data["slug"] == "rose-gold-almond"
    assert data["images"] == []


def test_get_product_returns_404_when_not_found(client):
    response = client.get("/api/products/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_get_product_returns_404_when_inactive(client, db_session, sample_product):
    sample_product.is_active = False
    db_session.commit()

    response = client.get("/api/products/rose-gold-almond")

    assert response.status_code == 404
