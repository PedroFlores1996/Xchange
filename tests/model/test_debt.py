import pytest
from sqlalchemy.exc import IntegrityError
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt


def test_update_new_debt(db_session):
    """Simply creates a new debt between two users."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    Debt.update(user1.id, user2.id, 100)

    assert Debt.query.count() == 1
    debt = Debt.find(user1.id, user2.id)
    assert debt.borrower is user1
    assert debt.lender is user2
    assert debt.amount == 100


def test_update_existing_debt(db_session):
    """Updates an existing debt."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    Debt.update(user1.id, user2.id, 100)
    Debt.update(user1.id, user2.id, 50)

    assert Debt.query.count() == 1
    debt = Debt.find(user1.id, user2.id)
    assert debt.amount == 150


def test_update_reverse_debt_settle_partly(db_session):
    """Updates existing debt with a reverse debt for part of the amount."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    Debt.update(user1.id, user2.id, 100)
    Debt.update(user2.id, user1.id, 50)

    assert Debt.query.count() == 1
    debt = Debt.find(user1.id, user2.id)
    assert debt.amount == 50


def test_update_reverse_debt_settle(db_session):
    """Deletes existing debt by updating with a reverse debt for the exact amount."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    Debt.update(user1.id, user2.id, 100)
    Debt.update(user2.id, user1.id, 100)

    assert Debt.query.count() == 0


def test_update_reverse_debt_overflow(db_session):
    """Deletes existing and creates new reverse debt by updating with a reverse debt for a higher amount."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    Debt.update(user1.id, user2.id, 100)
    Debt.update(user2.id, user1.id, 150)

    assert Debt.query.count() == 1
    debt12 = Debt.find(user1.id, user2.id)
    assert debt12 is None
    debt21 = Debt.find(user2.id, user1.id)
    assert debt21.amount == 50


def test_update_individual_debt_only(db_session):
    """Updates individual debts only since group debts are now handled by GroupBalance.
    Only one debt is created between the users.
    """
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")
    group1 = Group.create("group1", [user1])
    group2 = Group.create("group2", [user1])

    # Only individual debts are supported now
    Debt.update(user1.id, user2.id, 100)
    
    # Group debts would be handled by GroupBalance model, not tested here
    assert Debt.query.count() == 1


def test_update_individual_debt_reversed_settle(db_session):
    """Updates individual debt with reverse settlement.
    Since group debts are no longer handled by Debt model,
    this test focuses on individual debt settlement.
    """
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")
    group = Group.create("group_name", [user1])

    # Test individual debt settlement
    Debt.update(user1.id, user2.id, 100)
    Debt.update(user2.id, user1.id, 100)

    assert Debt.query.count() == 0


def test_update_unique_constraint_on_lender_borrower_and_no_group(db_session):
    """
    Creates a debt with no group.
    Unique constraint on lender, borrower, and group is enforced."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")

    Debt.update(user1.id, user2.id, 100)
    with pytest.raises(IntegrityError):
        db_session.add(Debt(borrower=user1, lender=user2, amount=100))
        db_session.commit()


def test_update_unique_constraint_on_lender_borrower_only(db_session):
    """
    Creates an individual debt.
    Unique constraint on lender and borrower is enforced (no group in constraint)."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")
    group = Group.create("group_name", [user1])

    Debt.update(user1.id, user2.id, 100)
    with pytest.raises(IntegrityError):
        db_session.add(Debt(borrower=user1, lender=user2, amount=100))
        db_session.commit()
