import pytest
from app.model.constants import NO_GROUP
from app.model.user import User
from app.model.balance import Balance
from app.model.expense import Expense, ExpenseCategory
from app.model.group import Group
from app.splits import SplitType


def test_create_expense(db_session):
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")
    group = Group.create("group", [user1, user2])
    balance1 = Balance.create(user1.id, owed=50.0, payed=100.0, total=50.0)
    balance2 = Balance.create(user2.id, owed=50.0, payed=0.0, total=-50.0)
    balances = [balance1, balance2]

    expense = Expense.create(
        100.0,
        balances,
        user1.id,
        SplitType.EQUALLY,
        group,
        "description",
        ExpenseCategory.OTHER,
    )

    assert Expense.query.count() == 1
    assert Balance.query.count() == 2
    assert Expense.query.first() is expense
    assert Balance.query.all() == balances

    assert expense.amount == 100.0
    assert expense.balances == balances
    assert expense.group is group
    assert expense.description == "description"
    assert expense.category == ExpenseCategory.OTHER
    assert expense.creator is user1
    assert expense.created_at is not None
    assert expense.updater is None
    assert expense.updated_at is None

    assert balance1.expense is expense
    assert balance2.expense is expense


def test_create_expense_no_group(db_session):
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")
    balance1 = Balance.create(user1.id, owed=50.0, payed=100.0, total=50.0)
    balance2 = Balance.create(user2.id, owed=50.0, payed=0.0, total=-50.0)
    balances = [balance1, balance2]

    expense = Expense.create(100.0, balances, user1.id, SplitType.EQUALLY)

    assert expense.group is None
    assert expense.group_id == NO_GROUP


def test_updating_expense_changes_updated_at(db_session):
    user1 = User.create("user1", "password")
    user2 = User.create("user2", "password")
    balance1 = Balance.create(user1.id, owed=50.0, payed=100.0, total=50.0)
    balance2 = Balance.create(user2.id, owed=50.0, payed=0.0, total=-50.0)
    balances = [balance1, balance2]

    expense = Expense.create(100.0, balances, user1.id, SplitType.EQUALLY)

    assert expense.updater is None
    assert expense.updated_at is None

    expense.description = "updated description"
    expense.updater = user2
    db_session.commit()

    assert expense.updated_at is not None
