from typing import List

import sqlalchemy
from flask_migrate import stamp
from flask.cli import AppGroup
from app.database import db

cli = AppGroup("database", help="Database commands.")


def is_db_empty() -> bool:
    table_names: List[str] = sqlalchemy.inspect(db.get_engine()).get_table_names()
    return len(table_names) == 0 or (
        len(table_names) == 1 and table_names[0] == "alembic_version"
    )


@cli.command("create_tables")
def create_tables() -> None:
    """Create all database tables."""
    if is_db_empty():
        db.create_all()
        print("All tables created successfully.")
        stamp()
