from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.dependencies import require_admin
from app.models import AdminUser
from app.templating import templates

router = APIRouter(tags=["admin"])


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    admin: AdminUser = Depends(require_admin),
):
    return templates.TemplateResponse(request, "admin/dashboard.html", {"admin": admin})
