from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import cart, pages, products
from app.templating import BASE_DIR, templates

app = FastAPI(title="Accessories Store")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(pages.router)
app.include_router(products.router)
app.include_router(cart.router)


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    if exc.status_code == 404:
        return templates.TemplateResponse(request, "404.html", status_code=404)
    return templates.TemplateResponse(
        request,
        "error.html",
        {"detail": exc.detail, "status_code": exc.status_code},
        status_code=exc.status_code,
    )
