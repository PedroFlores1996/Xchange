import sqlalchemy
from flask_migrate import stamp
from flask.cli import AppGroup
from app.database import db

cli = AppGroup('database', help="Database commands.")

def is_db_empty():
    table_names = sqlalchemy.inspect(db.get_engine()).get_table_names()
    print(table_names)
    return len(table_names) == 0 or (len(table_names) == 1 and table_names[0] == 'alembic_version')

@cli.command('create_tables')
def create_tables():
    """Create all database tables."""
    if is_db_empty():
        db.create_all()
        print("All tables created successfully.")
        stamp()
