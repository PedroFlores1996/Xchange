"""Shared fixtures for user tests"""

import pytest
from flask_login import login_user, logout_user
from app.model.user import User
from app.model.group import Group
from app.model.expense import Expense
from app.model.balance import Balance
from app.model.debt import Debt
from app.model.constants import NO_GROUP
from decimal import Decimal


@pytest.fixture
def logged_in_user(db_session):
    """Create and log in a user for testing"""
    user = User.create("testuser", "test@test.com", "password")
    login_user(user)
    yield user
    logout_user()


@pytest.fixture
def users_and_groups(db_session):
    """Create test users and groups for testing"""
    user1 = User.create("user1", "user1@test.com", "password")
    user2 = User.create("user2", "user2@test.com", "password")
    user3 = User.create("user3", "user3@test.com", "password")
    
    group1 = Group.create("group1", [user1, user2])
    group2 = Group.create("group2", [user1, user3])
    
    return user1, user2, user3, group1, group2


@pytest.fixture
def expenses_and_balances(users_and_groups, db_session):
    """Create test expenses and balances"""
    user1, user2, user3, group1, group2 = users_and_groups
    
    # Create balance for expense1
    balance1 = Balance.create(
        user_id=user2.id,
        owed=30.0,
        payed=20.0,
        total=10.0
    )
    
    # Create balance for expense2
    balance2 = Balance.create(
        user_id=user3.id,
        owed=25.0,
        payed=15.0,
        total=10.0
    )
    
    # Create expenses
    expense1 = Expense.create(
        amount=50.0,
        balances=[balance1],
        creator_id=user1.id,
        description="Group expense 1",
        group_id=group1.id
    )
    
    expense2 = Expense.create(
        amount=40.0,
        balances=[balance2],
        creator_id=user1.id,
        description="Group expense 2",
        group_id=group2.id
    )
    
    expense3 = Expense.create(
        amount=25.0,
        balances=[],
        creator_id=user1.id,
        description="No group expense",
        group_id=NO_GROUP
    )
    
    # Update balance relationships
    balance1.expense_id = expense1.id
    balance2.expense_id = expense2.id
    
    db_session.commit()
    
    return expense1, expense2, expense3, balance1, balance2