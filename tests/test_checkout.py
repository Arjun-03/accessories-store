from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models import Order
from app.services import cart_service, order_service


def test_place_order_creates_order(db_session, cart, sample_product, shipping_details):
    cart_service.add_to_cart(db_session, cart, sample_product.id, 2)

    order = order_service.place_order(db_session, cart, shipping_details)

    assert order.status == "pending"
    assert order.subtotal == sample_product.price * 2
    assert order.total == order.subtotal + order.shipping_fee
    assert len(order.items) == 1
    assert order.items[0].quantity == 2


def test_place_order_decrements_stock(db_session, cart, sample_product, shipping_details):
    starting_stock = sample_product.stock_quantity
    cart_service.add_to_cart(db_session, cart, sample_product.id, 3)

    order_service.place_order(db_session, cart, shipping_details)

    assert sample_product.stock_quantity == starting_stock - 3


def test_place_order_snapshots_price(db_session, cart, sample_product, shipping_details):
    cart_service.add_to_cart(db_session, cart, sample_product.id, 1)
    order = order_service.place_order(db_session, cart, shipping_details)
    snapshotted_price = order.items[0].unit_price

    # Change the product price AFTER the order.
    sample_product.price = Decimal("9999.00")
    db_session.commit()

    # The order's price must NOT change.
    assert order.items[0].unit_price == snapshotted_price
    assert order.items[0].unit_price != Decimal("9999.00")


def test_out_of_stock_checkout_is_rejected(db_session, cart, sample_product, shipping_details):
    # Add within stock, then externally reduce stock below the cart amount.
    cart_service.add_to_cart(db_session, cart, sample_product.id, 5)
    sample_product.stock_quantity = 2
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        order_service.place_order(db_session, cart, shipping_details)

    assert exc.value.status_code == 409


def test_empty_cart_checkout_is_rejected(db_session, cart, shipping_details):
    with pytest.raises(HTTPException) as exc:
        order_service.place_order(db_session, cart, shipping_details)

    assert exc.value.status_code == 400


def test_failed_checkout_rolls_back_stock(db_session, cart, sample_product, shipping_details):
    starting_stock = sample_product.stock_quantity
    cart_service.add_to_cart(db_session, cart, sample_product.id, 2)

    # Force a failure: an invalid payment_method violates the DB CHECK constraint,
    # so commit() will fail *after* stock has been decremented in memory.
    shipping_details.payment_method = "invalid_method"

    with pytest.raises(IntegrityError):
        order_service.place_order(db_session, cart, shipping_details)

    db_session.rollback()
    db_session.refresh(sample_product)

    # Stock must be UNCHANGED — the decrement was rolled back with everything else.
    assert sample_product.stock_quantity == starting_stock
    assert db_session.query(Order).count() == 0
