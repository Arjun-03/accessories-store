from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ProductDetail, ProductRead
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return product_service.get_active_products(db)


@router.get("/{slug}", response_model=ProductDetail)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = product_service.get_product_by_slug(db, slug)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product
