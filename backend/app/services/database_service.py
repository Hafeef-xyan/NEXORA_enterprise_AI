from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.tables import tables


# Sensitive fields that must not be exposed through the generic API
RESTRICTED_COLUMNS = {
    "users": {"password_hash"},
}


def get_available_tables():
    return list(tables.keys())


def get_table_records(
    db: Session,
    table_name: str,
    columns: list[str] | None = None,
    filters: dict | None = None,
    limit: int = 50,
    offset: int = 0
):

    # Validate table
    if table_name not in tables:
        raise ValueError("Table does not exist")

    table = tables[table_name]

    # Get allowed columns
    restricted = RESTRICTED_COLUMNS.get(table_name, set())

    allowed_columns = [
        column.name
        for column in table.columns
        if column.name not in restricted
    ]

    # Select requested columns
    if columns:
        invalid_columns = set(columns) - set(allowed_columns)

        if invalid_columns:
            raise ValueError(
                f"Invalid or restricted columns: {invalid_columns}"
            )

        selected_columns = [
            table.c[column_name]
            for column_name in columns
        ]

    else:
        selected_columns = [
            table.c[column_name]
            for column_name in allowed_columns
        ]

    query = select(*selected_columns)

    # Apply equality filters
    if filters:
        for column_name, value in filters.items():

            if column_name not in allowed_columns:
                raise ValueError(
                    f"Invalid or restricted filter column: {column_name}"
                )

            query = query.where(
                table.c[column_name] == value
            )

    # Pagination
    query = (
        query
        .order_by(list(table.primary_key.columns)[0])
        .limit(limit)
        .offset(offset)
    )

    result = db.execute(query)

    return [
        dict(row)
        for row in result.mappings().all()
    ]