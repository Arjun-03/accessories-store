from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import require_admin
from app.models import ORDER_STATUSES, AdminUser, Category, Product
from app.services import order_service, product_service
from app.templating import templates
from app.uploads import save_product_image

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


@router.get("/admin/products", response_class=HTMLResponse)
def admin_products(
    request: Request,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    products = product_service.list_all_products(db)
    return templates.TemplateResponse(
        request, "admin/products.html", {"products": products, "admin": admin}
    )


@router.get("/admin/products/new", response_class=HTMLResponse)
def new_product_form(
    request: Request,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    categories = db.execute(select(Category)).scalars().all()
    return templates.TemplateResponse(
        request,
        "admin/product_form.html",
        {"categories": categories, "admin": admin, "product": None},
    )


@router.post("/admin/products/new")
def create_product(
    request: Request,
    name: str = Form(...),
    category_id: int = Form(...),
    price: Decimal = Form(...),
    discount_price: Decimal | None = Form(None),
    description: str = Form(""),
    sku: str = Form(""),
    stock_quantity: int = Form(0),
    image: UploadFile | None = File(None),
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    image_url = None
    if image is not None and image.filename:
        image_url = save_product_image(image)

    product_service.create_product(
        db,
        name=name,
        category_id=category_id,
        price=price,
        discount_price=discount_price,
        description=description or None,
        sku=sku,
        stock_quantity=stock_quantity,
        image_url=image_url,
    )
    return RedirectResponse(url="/admin/products", status_code=303)


@router.get("/admin/products/{product_id}/edit", response_class=HTMLResponse)
def edit_product_form(
    product_id: int,
    request: Request,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    categories = db.execute(select(Category)).scalars().all()
    return templates.TemplateResponse(
        request,
        "admin/product_form.html",
        {"product": product, "categories": categories, "admin": admin},
    )


@router.post("/admin/products/{product_id}/edit")
def update_product(
    product_id: int,
    request: Request,
    name: str = Form(...),
    category_id: int = Form(...),
    price: Decimal = Form(...),
    discount_price: Decimal | None = Form(None),
    description: str = Form(""),
    sku: str = Form(""),
    stock_quantity: int = Form(...),
    image: UploadFile | None = File(None),
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    new_image_url = None
    if image is not None and image.filename:
        new_image_url = save_product_image(image)

    product_service.update_product(
        db,
        product,
        name=name,
        category_id=category_id,
        price=price,
        discount_price=discount_price,
        description=description or None,
        sku=sku,
        stock_quantity=stock_quantity,
        new_image_url=new_image_url,
    )
    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/admin/products/{product_id}/toggle")
def toggle_product(
    product_id: int,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product_service.toggle_product_active(db, product)
    return RedirectResponse(url="/admin/products", status_code=303)
