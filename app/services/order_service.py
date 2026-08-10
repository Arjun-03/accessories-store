from dataclasses import dataclass
from decimal import Decimal

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import ORDER_STATUSES, Cart, Order, OrderItem
from app.utils import generate_order_number


@dataclass
class ShippingDetails:
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address_line1: str
    shipping_address_line2: str | None
    shipping_city: str
    shipping_postal_code: str | None
    payment_method: str


def place_order(db: Session, cart: Cart, details: ShippingDetails) -> Order:
    if not cart.items:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    # 1. Re-validate stock strictly, before changing anything.
    for item in cart.items:
        if item.quantity > item.product.stock_quantity:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Not enough stock for {item.product.name}",
            )

    # 2. Compute authoritative totals.
    subtotal = sum(
        (item.product.effective_price * item.quantity for item in cart.items),
        start=Decimal("0.00"),
    )
    shipping_fee = Decimal(settings.shipping_flat_rate)
    total = subtotal + shipping_fee

    # 3. Build the order.
    order = Order(
        order_number=generate_order_number(),
        customer_name=details.customer_name,
        customer_email=details.customer_email,
        customer_phone=details.customer_phone,
        shipping_address_line1=details.shipping_address_line1,
        shipping_address_line2=details.shipping_address_line2,
        shipping_city=details.shipping_city,
        shipping_postal_code=details.shipping_postal_code,
        payment_method=details.payment_method,
        status="pending",
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total=total,
    )
    db.add(order)

    # 4. Snapshot each cart item into an order item, and decrement stock.
    for item in cart.items:
        order.items.append(
            OrderItem(
                product_id=item.product_id,
                product_name=item.product.name,
                product_sku=item.product.sku,
                unit_price=item.product.effective_price,
                quantity=item.quantity,
            )
        )
        item.product.stock_quantity -= item.quantity

    # 5. Remove the cart — it is now an order.
    db.delete(cart)

    # 6. Commit everything as one transaction.
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order


def list_orders(db: Session) -> list[Order]:
    stmt = select(Order).order_by(Order.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_order_by_number(db: Session, order_number: str) -> Order | None:
    stmt = select(Order).where(Order.order_number == order_number).options(joinedload(Order.items))
    return db.execute(stmt).unique().scalar_one_or_none()


def update_order_status(db: Session, order: Order, new_status: str) -> Order:
    if new_status not in ORDER_STATUSES:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}",
        )
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order
