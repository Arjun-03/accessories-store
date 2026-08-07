from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import ADMIN_COOKIE_NAME, set_admin_cookie
from app.services import auth_service
from app.templating import templates

router = APIRouter(tags=["admin-auth"])


@router.get("/admin/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "admin/login.html")


@router.post("/admin/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    admin = auth_service.authenticate(db, email, password)
    if admin is None:
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Invalid email or password."},
            status_code=401,
        )
    session = auth_service.create_session(db, admin)
    response = RedirectResponse(url="/admin", status_code=303)
    set_admin_cookie(response, session.session_token)
    return response


@router.post("/admin/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(ADMIN_COOKIE_NAME)
    if token:
        auth_service.delete_session(db, token)
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return response
