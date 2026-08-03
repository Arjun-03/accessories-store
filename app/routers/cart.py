from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import cart_redirect, get_cart, set_cart_cookie
from app.models import Cart
from app.services import cart_service
from app.templating import templates

router = APIRouter(tags=["cart"])


@router.get("/cart", response_class=HTMLResponse)
def view_cart(request: Request, cart: Cart = Depends(get_cart), db: Session = Depends(get_db)):
    subtotal = cart_service.calculate_cart_subtotal(cart)
    response = templates.TemplateResponse(
        request, "cart.html", {"cart": cart, "subtotal": subtotal}
    )
    set_cart_cookie(response, cart)
    return response


@router.post("/cart/add")
def add_item(
    product_id: int = Form(...),
    quantity: int = Form(1),
    cart: Cart = Depends(get_cart),
    db: Session = Depends(get_db),
):
    cart_service.add_to_cart(db, cart, product_id, quantity)
    return cart_redirect(cart)


@router.post("/cart/update")
def update_item(
    product_id: int = Form(...),
    quantity: int = Form(...),
    cart: Cart = Depends(get_cart),
    db: Session = Depends(get_db),
):
    cart_service.update_quantity(db, cart, product_id, quantity)
    return cart_redirect(cart)


@router.post("/cart/remove")
def remove_item(
    product_id: int = Form(...),
    cart: Cart = Depends(get_cart),
    db: Session = Depends(get_db),
):
    cart_service.remove_from_cart(db, cart, product_id)
    return cart_redirect(cart)
