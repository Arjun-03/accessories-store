from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.services import cart_service


def test_add_to_cart(db_session, cart, sample_product):
    cart_service.add_to_cart(db_session, cart, sample_product.id, 2)

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2


def test_adding_same_product_increases_quantity(db_session, cart, sample_product):
    cart_service.add_to_cart(db_session, cart, sample_product.id, 2)
    cart_service.add_to_cart(db_session, cart, sample_product.id, 3)

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5


def test_adding_more_than_stock_is_rejected(db_session, cart, sample_product):
    too_many = sample_product.stock_quantity + 1
    with pytest.raises(HTTPException) as exc:
        cart_service.add_to_cart(db_session, cart, sample_product.id, too_many)

    assert exc.value.status_code == 409


def test_accumulated_quantity_over_stock_is_rejected(db_session, cart, sample_product):
    stock = sample_product.stock_quantity
    cart_service.add_to_cart(db_session, cart, sample_product.id, stock)  # fill to stock

    with pytest.raises(HTTPException) as exc:
        cart_service.add_to_cart(db_session, cart, sample_product.id, 1)  # one over

    assert exc.value.status_code == 409
    assert cart.items[0].quantity == stock  # unchanged


def test_remove_from_cart(db_session, cart, sample_product):
    cart_service.add_to_cart(db_session, cart, sample_product.id, 2)
    cart_service.remove_from_cart(db_session, cart, sample_product.id)

    assert len(cart.items) == 0


def test_subtotal_uses_discounted_price(db_session, cart, sample_product):
    sample_product.discount_price = Decimal("1200.00")
    db_session.commit()

    cart_service.add_to_cart(db_session, cart, sample_product.id, 2)
    subtotal = cart_service.calculate_cart_subtotal(cart)

    assert subtotal == sample_product.discount_price * 2
