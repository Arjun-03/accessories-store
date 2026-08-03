from fastapi import Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Cart
from app.services import cart_service

CART_COOKIE_NAME = "cart_token"
CART_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days, in seconds


def get_cart(
    request: Request,
    db: Session = Depends(get_db),
) -> Cart:
    token = request.cookies.get(CART_COOKIE_NAME)
    return cart_service.get_or_create_cart(db, token)


def set_cart_cookie(response: Response, cart: Cart) -> None:
    response.set_cookie(
        key=CART_COOKIE_NAME,
        value=cart.session_token,
        max_age=CART_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False,  # TODO: set True in production (HTTPS only)
    )


def cart_redirect(cart: Cart, url: str = "/cart") -> RedirectResponse:
    response = RedirectResponse(url=url, status_code=303)
    set_cart_cookie(response, cart)
    return response
