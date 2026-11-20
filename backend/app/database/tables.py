# this metadata fetch all tables in database
from sqlalchemy import MetaData

from app.database.connection import engine


metadata = MetaData()

# Automatically inspect all existing database tables
metadata.reflect(bind=engine)

# All reflected tables are available here
tables = metadata.tables