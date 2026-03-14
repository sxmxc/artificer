from fastapi import FastAPI

from app.api import admin_router, public_router
from app.config import Settings
from app.openapi import get_openapi

settings = Settings()

app = FastAPI(title="Cuddly Octo Memory", version="0.1.0")

app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(public_router, prefix="/api", tags=["mock"])

# Override OpenAPI generator to use dynamic definitions.
# Keep a reference to the original generator to avoid recursion.
_original_get_openapi = app.openapi
app.openapi = lambda: get_openapi(app, settings, _original_get_openapi)
