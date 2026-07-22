from fastapi import FastAPI

from app.routers import products

app = FastAPI(title="Accessories Store")

app.include_router(products.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Accessories Store"}