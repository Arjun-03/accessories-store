from fastapi import Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import AdminUser, Cart
from app.services import auth_service, cart_service

ADMIN_COOKIE_NAME = "admin_session"
ADMIN_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days, matching session expiry

CART_COOKIE_NAME = "cart_token"
CART_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days, in seconds


class NotAuthenticatedError(Exception):
    """Raised when an admin route is accessed without a valid session."""


def set_admin_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        max_age=ADMIN_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,  # True in production, False in dev
    )


def require_admin(
    request: Request,
    db: Session = Depends(get_db),
) -> AdminUser:
    token = request.cookies.get(ADMIN_COOKIE_NAME)
    session = auth_service.get_valid_session(db, token)
    if session is None:
        raise NotAuthenticatedError()
    return session.admin_user


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
        secure=settings.cookie_secure,  # True in production, False in dev
    )


def cart_redirect(cart: Cart, url: str = "/cart") -> RedirectResponse:
    response = RedirectResponse(url=url, status_code=303)
    set_cart_cookie(response, cart)
    return response
