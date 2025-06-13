from typing import List

import sqlalchemy
from flask_migrate import stamp
from flask.cli import AppGroup
from app.database import db
from app.split.constants import OWED, PAYED, TOTAL
from app.debt import update_debts
from app.model.group import Group
from app.model.user import User
from app.model.expense import Expense
from app.split import SplitType
from app.expense.mapper import map_balances_to_model
from app.user import update_expenses_in_users

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
    from app.model.expense import Expense
    from app.split import SplitType  # Import SplitType for split types
    from app.expense.mapper import map_balances_to_model
    from app.debt import update_debts
    from app.split.constants import OWED, PAYED, TOTAL

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

    db.session.commit()

    # Pre-existing expenses
    balances = {
        users[0].id: {TOTAL: 100.0, PAYED: 100.0, OWED: 0.0},  # Payer
        users[1].id: {TOTAL: -50.0, PAYED: 0.0, OWED: 50.0},  # Ower
        users[2].id: {TOTAL: -50.0, PAYED: 0.0, OWED: 50.0},  # Ower
    }
    update_debts(balances, group1.id)
    expense1 = Expense.create(
        description="Group 1 Dinner",
        amount=100.0,
        creator_id=users[0].id,
        group_id=group1.id,
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.EQUALLY,
        balances=map_balances_to_model(balances),
    )

    balances = {
        users[8].id: {TOTAL: 200.0, PAYED: 200.0, OWED: 0.0},  # Payer
        users[6].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},  # Ower
        users[7].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},  # Ower
    }
    update_debts(balances, group2.id)
    expense2 = Expense.create(
        description="Group 2 Trip",
        amount=200.0,
        creator_id=users[5].id,
        group_id=group2.id,
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.EQUALLY,
        balances=map_balances_to_model(balances),
    )

    balances = {
        users[0].id: {TOTAL: 20.0, PAYED: 20.0, OWED: 0.0},  # Payer
        users[3].id: {TOTAL: -20.0, PAYED: 0.0, OWED: 20.0},  # Ower
    }
    update_debts(balances, None)
    expense3 = Expense.create(
        description="Coffee",
        amount=20.0,
        creator_id=users[0].id,
        group_id=None,  # No group
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.EQUALLY,
        balances=map_balances_to_model(balances),
    )

    balances = {
        users[6].id: {TOTAL: 50.0, PAYED: 50.0, OWED: 0.0},  # Payer
        users[8].id: {TOTAL: -25.0, PAYED: 0.0, OWED: 25.0},  # Ower
        users[9].id: {TOTAL: -25.0, PAYED: 0.0, OWED: 25.0},  # Ower
    }
    update_debts(balances, None)
    expense4 = Expense.create(
        description="Movie Tickets",
        amount=50.0,
        creator_id=users[4].id,
        group_id=None,  # No group
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.EQUALLY,
        balances=map_balances_to_model(balances),
    )

    # New expenses
    # Expense 5: Payers split by amount, owers split equally
    balances = {
        users[0].id: {TOTAL: 120.0, PAYED: 120.0, OWED: 0.0},  # Payer
        users[1].id: {TOTAL: -60.0, PAYED: 0.0, OWED: 60.0},  # Ower
        users[2].id: {TOTAL: -60.0, PAYED: 0.0, OWED: 60.0},  # Ower
    }
    update_debts(balances, group1.id)
    expense5 = Expense.create(
        description="Team Lunch",
        amount=120.0,
        creator_id=users[0].id,
        group_id=group1.id,
        payers_split=SplitType.AMOUNT,
        owers_split=SplitType.EQUALLY,
        balances=map_balances_to_model(balances),
    )

    # Expense 6: Payers split equally, owers split by percentages
    balances = {
        users[3].id: {TOTAL: 50.0, PAYED: 50.0, OWED: 0.0},  # Payer
        users[4].id: {TOTAL: 50.0, PAYED: 50.0, OWED: 0.0},  # Payer
        users[2].id: {TOTAL: -30.0, PAYED: 0.0, OWED: 30.0},  # Ower (30%)
        users[1].id: {TOTAL: -70.0, PAYED: 0.0, OWED: 70.0},  # Ower (70%)
    }
    update_debts(balances, group1.id)
    expense6 = Expense.create(
        description="Office Supplies",
        amount=100.0,
        creator_id=users[3].id,
        group_id=group1.id,
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.PERCENTAGE,
        balances=map_balances_to_model(balances),
    )

    # Expense 7: Payers split by percentages, owers split equally
    balances = {
        users[7].id: {TOTAL: 120.0, PAYED: 120.0, OWED: 0.0},  # Payer (60%)
        users[8].id: {TOTAL: 80.0, PAYED: 80.0, OWED: 0.0},  # Payer (40%)
        users[9].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},  # Ower
        users[6].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},  # Ower
    }
    update_debts(balances, None)
    expense7 = Expense.create(
        description="Conference Tickets",
        amount=200.0,
        creator_id=users[7].id,
        group_id=None,  # No group
        payers_split=SplitType.PERCENTAGE,
        owers_split=SplitType.EQUALLY,
        balances=map_balances_to_model(balances),
    )

    # Expense 8: Payers split equally, owers split by amount
    balances = {
        users[1].id: {TOTAL: 45.0, PAYED: 45.0, OWED: 0.0},  # Payer
        users[2].id: {TOTAL: 45.0, PAYED: 45.0, OWED: 0.0},  # Payer
        users[3].id: {TOTAL: -30.0, PAYED: 0.0, OWED: 30.0},  # Ower
        users[4].id: {TOTAL: -60.0, PAYED: 0.0, OWED: 60.0},  # Ower
    }
    update_debts(balances, None)
    expense8 = Expense.create(
        description="Shared Taxi",
        amount=90.0,
        creator_id=users[1].id,
        group_id=None,  # No group
        payers_split=SplitType.EQUALLY,
        owers_split=SplitType.AMOUNT,
        balances=map_balances_to_model(balances),
    )

    # Add all expenses to users
    update_expenses_in_users(
        [expense1, expense2, expense3, expense4, expense5, expense6, expense7, expense8]
    )

    db.session.commit()

    print("Test data created successfully.")
