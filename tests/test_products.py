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
    assert response.headers["content-type"] == "application/json"
    assert response.json()["detail"] == "Product not found"


def test_get_product_returns_404_when_inactive(client, db_session, sample_product):
    sample_product.is_active = False
    db_session.commit()

    response = client.get("/api/products/rose-gold-almond")

    assert response.status_code == 404


def _make_product(db, name, price, description="", category=None):
    if category is None:
        category = Category(name="Cat", slug="cat")
        db.add(category)
        db.flush()
    p = Product(
        category_id=category.id,
        name=name,
        slug=name.lower().replace(" ", "-"),
        description=description,
        price=Decimal(price),
        stock_quantity=5,
    )
    db.add(p)
    db.commit()
    return p


def test_search_matches_name(client, db_session):
    cat = Category(name="Cat", slug="cat")
    db_session.add(cat)
    db_session.flush()
    _make_product(db_session, "Gold Hoops", "1000.00", category=cat)
    _make_product(db_session, "Silver Ring", "800.00", category=cat)

    response = client.get("/products?q=gold")
    assert response.status_code == 200
    assert "Gold Hoops" in response.text
    assert "Silver Ring" not in response.text


def test_search_matches_description(client, db_session):
    cat = Category(name="Cat", slug="cat")
    db_session.add(cat)
    db_session.flush()
    _make_product(db_session, "Hoops", "1000.00", description="warm gold finish", category=cat)
    _make_product(db_session, "Ring", "800.00", description="cool silver tone", category=cat)

    response = client.get("/products?q=gold")
    assert "Hoops" in response.text
    assert "Ring" not in response.text


def test_price_range_filters(client, db_session):
    cat = Category(name="Cat", slug="cat")
    db_session.add(cat)
    db_session.flush()
    _make_product(db_session, "Cheap", "500.00", category=cat)
    _make_product(db_session, "Expensive", "5000.00", category=cat)

    response = client.get("/products?min_price=1000&max_price=3000")
    assert "Cheap" not in response.text
    assert "Expensive" not in response.text  # both outside 1000-3000


def test_sort_price_ascending(client, db_session):
    cat = Category(name="Cat", slug="cat")
    db_session.add(cat)
    db_session.flush()
    _make_product(db_session, "Pricey", "5000.00", category=cat)
    _make_product(db_session, "Budget", "500.00", category=cat)

    response = client.get("/products?sort=price_asc")
    # cheaper product should appear before pricier in the HTML
    assert response.text.index("Budget") < response.text.index("Pricey")


def test_empty_price_does_not_error(client, db_session):
    # The bug we hit: empty price fields submitted as "" must not 422
    response = client.get("/products?q=gold&min_price=&max_price=&sort=")
    assert response.status_code == 200


def test_garbage_price_ignored(client, db_session):
    # Defensive: non-numeric price in URL should be ignored, not crash
    response = client.get("/products?min_price=abc")
    assert response.status_code == 200
