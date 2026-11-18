from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
def health_check():

    return {
        "status": "healthy",
        "service": "NEXORA Backend"
    }


@router.get("/database")
def database_status(db: Session = Depends(get_db)):

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "connected",
            "database": "PostgreSQL",
            "message": "Database connection successful"
        }

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )