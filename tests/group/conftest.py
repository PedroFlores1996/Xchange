"""Shared fixtures for group tests"""

import pytest
from flask_login import login_user, logout_user
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt
from app.model.expense import Expense
from app.model.constants import NO_GROUP
from decimal import Decimal


@pytest.fixture
def logged_in_user(db_session):
    """Create and log in a user for testing"""
    user = User.create("user1", "email1", "password")
    login_user(user)
    yield user
    logout_user()


@pytest.fixture
def users_and_group(db_session):
    """Create test users and group for testing"""
    user1 = User.create("user1", "user1@test.com", "password")
    user2 = User.create("user2", "user2@test.com", "password")
    user3 = User.create("user3", "user3@test.com", "password")
    group = Group.create("test_group", [user1, user2, user3])
    return user1, user2, user3, group


@pytest.fixture
def debts_and_expenses(users_and_group, db_session):
    """Create test debts and expenses"""
    user1, user2, user3, group = users_and_group
    
    # Create group debts using Debt.update (which creates if not exists)
    Debt.update(user2.id, user1.id, float(Decimal("50.00")), group.id)
    Debt.update(user3.id, user2.id, float(Decimal("30.00")), group.id)
    
    # Create no-group debts
    Debt.update(user3.id, user1.id, float(Decimal("20.00")), NO_GROUP)
    
    db_session.commit()
    
    # Fetch created debts
    debt1 = Debt.find(user2.id, user1.id, group.id)
    debt2 = Debt.find(user3.id, user2.id, group.id)
    debt3 = Debt.find(user3.id, user1.id, NO_GROUP)
    
    # Create expenses
    expense1 = Expense.create(
        amount=float(Decimal("100.00")),
        balances=[],
        creator_id=user1.id,
        description="Group expense 1",
        group_id=group.id,
    )
    expense1.users.append(user1)
    
    expense2 = Expense.create(
        amount=float(Decimal("75.00")),
        balances=[],
        creator_id=user2.id,
        description="Group expense 2",
        group_id=group.id,
    )
    expense2.users.append(user2)
    
    expense3 = Expense.create(
        amount=float(Decimal("25.00")),
        balances=[],
        creator_id=user1.id,
        description="No group expense",
        group_id=NO_GROUP,
    )
    expense3.users.append(user1)
    
    db_session.commit()
    
    return debt1, debt2, debt3, expense1, expense2, expense3