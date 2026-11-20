import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.database_service import (
    get_available_tables,
    get_table_records
)


router = APIRouter(
    prefix="/api/data",
    tags=["Database"]
)


@router.get("/tables")
def list_tables():

    return {
        "count": len(get_available_tables()),
        "tables": get_available_tables()
    }


@router.get("/{table_name}")
def retrieve_table_data(
    table_name: str,
    columns: str | None = None,
    filters: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):

    try:
        selected_columns = (
            [column.strip() for column in columns.split(",")]
            if columns else None
        )

        parsed_filters = json.loads(filters) if filters else None

        if parsed_filters is not None and not isinstance(parsed_filters, dict):
            raise ValueError("Filters must be a JSON object")

        records = get_table_records(
            db=db,
            table_name=table_name,
            columns=selected_columns,
            filters=parsed_filters,
            limit=limit,
            offset=offset
        )

        return {
            "table": table_name,
            "count": len(records),
            "data": records
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve database records"
        )