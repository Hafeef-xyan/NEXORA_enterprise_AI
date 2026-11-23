from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import health, data, rag


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


app.include_router(health.router)
app.include_router(data.router)
app.include_router(rag.router, prefix="/api/v1")


@app.get("/")
def root():

    return {
        "message": "Welcome to NEXORA Enterprise AI Platform",
        "version": settings.APP_VERSION
    }