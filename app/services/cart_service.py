from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cart, CartItem, Product
from app.utils import generate_session_token


def _validate_stock(product: Product, quantity: int) -> None:
    if quantity > product.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not enough stock available",
        )


def get_or_create_cart(db: Session, token: str | None) -> Cart:
    if token:
        cart = db.execute(select(Cart).where(Cart.session_token == token)).scalar_one_or_none()
        if cart is not None:
            return cart

    cart = Cart(session_token=generate_session_token())
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def add_to_cart(db: Session, cart: Cart, product_id: int, quantity: int) -> CartItem:
    product = db.get(Product, product_id)
    if product is None or not product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing = db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    ).scalar_one_or_none()

    current_in_cart = existing.quantity if existing is not None else 0
    new_total = current_in_cart + quantity
    _validate_stock(product, new_total)

    if existing is not None:
        existing.quantity += quantity
        item = existing
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(item)
    return item


def update_quantity(db: Session, cart: Cart, product_id: int, quantity: int) -> None:
    item = db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    ).scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart")

    if quantity <= 0:
        db.delete(item)
    else:
        _validate_stock(item.product, quantity)
        item.quantity = quantity
    db.commit()


def remove_from_cart(db: Session, cart: Cart, product_id: int) -> None:
    item = db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    ).scalar_one_or_none()
    if item is not None:
        db.delete(item)
        db.commit()


def get_cart_item_count(cart: Cart) -> int:
    return sum(item.quantity for item in cart.items)


def calculate_cart_subtotal(cart: Cart) -> Decimal:
    return sum(
        (item.product.effective_price * item.quantity for item in cart.items),
        start=Decimal("0.00"),
    )
