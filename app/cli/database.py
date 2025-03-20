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


@cli.command("create-tables")
def create_tables() -> None:
    """Create all database tables."""
    if is_db_empty():
        db.create_all()
        print("All tables created successfully.")
        stamp()


@cli.command("clear-data")
def clear_data() -> None:
    """Clear all data from the database tables."""
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f"Clearing table {table.name}...")
        db.session.execute(table.delete())
    db.session.commit()
    print("All data cleared successfully.")


@cli.command("test-data")
def test_data() -> None:
    """Create test data."""
    from app.model.user import User
    from app.model.group import Group

    # Create 10 users
    users = []
    for i in range(1, 11):
        user = User.create(
            username=f"user{i}", email=f"{i}@email.com", password="password"
        )
        users.append(user)

    # Create 2 groups
    group1 = Group(name="Group 1")
    group2 = Group(name="Group 2")
    db.session.add(group1)
    db.session.add(group2)
    db.session.commit()

    # Add 5 users to each group
    for user in users[:5]:
        user.add_to_group(group1)
    for user in users[5:]:
        user.add_to_group(group2)

    # Make all users friends with each other
    for user in users:
        for friend in users:
            if user != friend:  # Avoid adding a user as their own friend
                user.add_friends(friend)

    print("Test data created successfully.")
