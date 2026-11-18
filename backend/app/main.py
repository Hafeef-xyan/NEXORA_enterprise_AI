from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import health


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


# Register API routes
app.include_router(health.router)


@app.get("/")
def root():

    return {
        "message": "Welcome to NEXORA Enterprise AI Platform",
        "version": settings.APP_VERSION
    }