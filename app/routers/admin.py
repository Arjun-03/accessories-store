from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import require_admin
from app.models import ORDER_STATUSES, AdminUser
from app.services import order_service
from app.templating import templates

router = APIRouter(tags=["admin"])


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    admin: AdminUser = Depends(require_admin),
):
    return templates.TemplateResponse(request, "admin/dashboard.html", {"admin": admin})


@router.get("/admin/orders", response_class=HTMLResponse)
def admin_orders(
    request: Request,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    orders = order_service.list_orders(db)
    return templates.TemplateResponse(
        request, "admin/orders.html", {"orders": orders, "admin": admin}
    )


@router.get("/admin/orders/{order_number}", response_class=HTMLResponse)
def admin_order_detail(
    order_number: str,
    request: Request,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = order_service.get_order_by_number(db, order_number)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return templates.TemplateResponse(
        request,
        "admin/order_detail.html",
        {"order": order, "statuses": ORDER_STATUSES, "admin": admin},
    )


@router.post("/admin/orders/{order_number}/status")
def admin_update_order_status(
    order_number: str,
    new_status: str = Form(...),
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = order_service.get_order_by_number(db, order_number)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order_service.update_order_status(db, order, new_status)
    return RedirectResponse(url=f"/admin/orders/{order_number}", status_code=303)
