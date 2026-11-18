# engine	Manages the connection pool to PostgreSQL
#SessionLocal	Creates database sessions
#Base	Parent class for future SQLAlchemy models
#get_db()	Provides a session to API endpoints and closes it afterward
#pool_pre_ping	Checks connections before using them 


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)


# Database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Base class for ORM models
class Base(DeclarativeBase):
    pass


# Dependency for database sessions
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()