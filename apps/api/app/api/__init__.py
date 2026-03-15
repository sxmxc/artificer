from app.routes.admin import router as admin_router
from app.routes.public import router as public_router
from app.routes.site import router as site_router

__all__ = ["admin_router", "public_router", "site_router"]
