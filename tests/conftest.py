from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import AdminUser, Cart, Category, Product
from app.security import hash_password
from app.services import order_service
from app.services.order_service import ShippingDetails

TEST_DATABASE_URL = (
    f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/accessories_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_product(db_session):
    category = Category(name="Nails", slug="nails")
    db_session.add(category)
    db_session.flush()
    product = Product(
        category_id=category.id,
        name="Rose Gold Almond",
        slug="rose-gold-almond",
        description="Almond-shaped set.",
        price=Decimal("1500.00"),
        stock_quantity=12,
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture()
def cart(db_session):
    c = Cart(session_token="test-token-12345")
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture()
def shipping_details():
    return ShippingDetails(
        customer_name="Test Customer",
        customer_email="test@example.com",
        customer_phone="0771234567",
        shipping_address_line1="123 Test Lane",
        shipping_address_line2=None,
        shipping_city="Colombo",
        shipping_postal_code=None,
        payment_method="cod",
    )


@pytest.fixture()
def admin_user(db_session):
    admin = AdminUser(email="admin@test.com", password_hash=hash_password("testpass123"))
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture()
def placed_order(db_session, cart, sample_product, shipping_details):
    from app.services import cart_service

    cart_service.add_to_cart(db_session, cart, sample_product.id, 2)
    return order_service.place_order(db_session, cart, shipping_details)


@pytest.fixture()
def admin_client(client, admin_user):
    client.post(
        "/admin/login",
        data={"email": "admin@test.com", "password": "testpass123"},
    )
    return client
