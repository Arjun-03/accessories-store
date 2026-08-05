from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.dependencies import get_cart, set_cart_cookie
from app.models import Cart, Order
from app.services import cart_service, order_service
from app.services.order_service import ShippingDetails
from app.templating import templates

router = APIRouter(tags=["checkout"])


@router.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request, cart: Cart = Depends(get_cart), db: Session = Depends(get_db)):
    if not cart.items:
        return RedirectResponse(url="/cart", status_code=303)

    subtotal = cart_service.calculate_cart_subtotal(cart)
    shipping = Decimal(settings.shipping_flat_rate)
    total = subtotal + shipping

    response = templates.TemplateResponse(
        request,
        "checkout.html",
        {"cart": cart, "subtotal": subtotal, "shipping": shipping, "total": total},
    )
    set_cart_cookie(response, cart)
    return response


@router.post("/checkout")
def place_order(
    request: Request,
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    customer_phone: str = Form(...),
    shipping_address_line1: str = Form(...),
    shipping_address_line2: str | None = Form(None),
    shipping_city: str = Form(...),
    shipping_postal_code: str | None = Form(None),
    payment_method: str = Form(...),
    cart: Cart = Depends(get_cart),
    db: Session = Depends(get_db),
):
    details = ShippingDetails(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        shipping_address_line1=shipping_address_line1,
        shipping_address_line2=shipping_address_line2,
        shipping_city=shipping_city,
        shipping_postal_code=shipping_postal_code,
        payment_method=payment_method,
    )
    order = order_service.place_order(db, cart, details)
    return RedirectResponse(url=f"/order/{order.order_number}", status_code=303)


@router.get("/order/{order_number}", response_class=HTMLResponse)
def order_confirmation(order_number: str, request: Request, db: Session = Depends(get_db)):
    order = db.execute(select(Order).where(Order.order_number == order_number)).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return templates.TemplateResponse(request, "order_confirmation.html", {"order": order})
