from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import product_service
from app.templating import templates

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@router.get("/products", response_class=HTMLResponse)
def product_list(request: Request, db: Session = Depends(get_db)):
    products = product_service.get_active_products(db)
    return templates.TemplateResponse(request, "products.html", {"products": products})


@router.get("/products/{slug}", response_class=HTMLResponse)
def product_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    product = product_service.get_product_by_slug(db, slug)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse(request, "product_detail.html", {"product": product})
