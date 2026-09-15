from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import product_service
from app.templating import templates

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    categories = product_service.list_categories(db)
    new_products = product_service.get_newest_products(db, limit=4)
    return templates.TemplateResponse(
        request, "home.html", {"categories": categories, "new_products": new_products}
    )


@router.get("/products", response_class=HTMLResponse)
def product_list(
    request: Request,
    category: str | None = None,
    q: str | None = None,
    min_price: str | None = None,
    max_price: str | None = None,
    sort: str | None = None,
    db: Session = Depends(get_db),
):
    def parse_price(value: str | None) -> Decimal | None:
        if value is None or value.strip() == "":
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError):
            return None

    min_p = parse_price(min_price)
    max_p = parse_price(max_price)

    products = product_service.get_active_products(
        db,
        category_slug=category,
        search=q,
        min_price=min_p,
        max_price=max_p,
        sort=sort,
    )
    active_category = product_service.get_category_by_slug(db, category) if category else None
    categories = product_service.list_categories(db)
    return templates.TemplateResponse(
        request,
        "products.html",
        {
            "products": products,
            "active_category": active_category,
            "categories": categories,
            "q": q,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort,
        },
    )


@router.get("/products/{slug}", response_class=HTMLResponse)
def product_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    product = product_service.get_product_by_slug(db, slug)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse(request, "product_detail.html", {"product": product})


@router.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, "about.html")


@router.get("/faq", response_class=HTMLResponse)
def faq(request: Request):
    return templates.TemplateResponse(request, "faq.html")


@router.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html")
