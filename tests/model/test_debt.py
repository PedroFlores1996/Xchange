import pytest
from sqlalchemy.exc import IntegrityError
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt


def test_update_new_debt(db_session):
    """Simply creates a new debt between two users."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")

    Debt.update(user1, user2, 100)

    assert Debt.query.count() == 1
    debt = Debt.find(user1, user2)
    assert debt.lender == user1
    assert debt.borrower == user2
    assert debt.amount == 100


def test_update_existing_debt(db_session):
    """Updates an existing debt."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")

    Debt.update(user1, user2, 100)
    Debt.update(user1, user2, 50)

    assert Debt.query.count() == 1
    debt = Debt.find(user1, user2)
    assert debt.amount == 150


def test_update_reverse_debt_settle_partly(db_session):
    """Updates existing debt with a reverse debt for part of the amount."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")

    Debt.update(user1, user2, 100)
    Debt.update(user2, user1, 50)

    assert Debt.query.count() == 1
    debt = Debt.find(user1, user2)
    assert debt.amount == 50


def test_update_reverse_debt_settle(db_session):
    """Deletes existing debt by updating with a reverse debt for the exact amount."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")

    Debt.update(user1, user2, 100)
    Debt.update(user2, user1, 100)

    assert Debt.query.count() == 0


def test_update_reverse_debt_overflow(db_session):
    """Deletes existing and creates new reverse debt by updating with a reverse debt for a higher amount."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")

    Debt.update(user1, user2, 100)
    Debt.update(user2, user1, 150)

    assert Debt.query.count() == 1
    debt12 = Debt.find(user1, user2)
    assert debt12 == None
    debt21 = Debt.find(user2, user1)
    assert debt21.amount == 50


def test_update_group_debt(db_session):
    """Updates a debt with no group.
    Updates a debt with a group between same users.
    Updates a debt with another group between same users but reversed.
    Three separate debts are created.
    """
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")
    group1 = Group.create_group("group1")
    group2 = Group.create_group("group2")

    Debt.update(user1, user2, 100)
    Debt.update(user1, user2, 100, group=group1)
    Debt.update(user2, user1, 100, group=group2)

    assert Debt.query.count() == 3


def test_update_group_debt_reversed_settle(db_session):
    """Updates a debt with no group.
    Updates a debt with a group between same users.
    Updates a debt with another group between same users but reversed.
    Updates the second debt with the exact amount.
    Two separate debts are created.
    """
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")
    group = Group.create_group("group")

    Debt.update(user1, user2, 100, group=group)
    Debt.update(user2, user1, 100, group=group)

    assert Debt.query.count() == 0


def test_update_unique_constraint_on_lender_borrower_and_no_group(db_session):
    """
    Creates a debt with no group.
    Unique constraint on lender, borrower, and group is enforced."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")

    Debt.update(user1, user2, 100)
    with pytest.raises(IntegrityError):
        db_session.add(Debt(lender=user1, borrower=user2, amount=100))
        db_session.commit()


def test_update_unique_constraint_on_lender_borrower_and_group(db_session):
    """
    Creates a debt with a group.
    Unique constraint on lender, borrower, and group is enforced."""
    user1 = User.create_user("user1", "password")
    user2 = User.create_user("user2", "password")
    group = Group.create_group("group")

    Debt.update(user1, user2, 100, group=group)
    with pytest.raises(IntegrityError):
        db_session.add(Debt(lender=user1, borrower=user2, amount=100, group=group))
        db_session.commit()
