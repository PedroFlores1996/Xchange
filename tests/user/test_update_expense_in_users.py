"""Tests for update_expense_in_users function"""

import pytest
from app.user import update_expense_in_users
from app.model.user import User
from app.model.expense import Expense
from app.model.balance import Balance
from app.model.constants import NO_GROUP


class TestUpdateExpenseInUsers:
    """Tests for update_expense_in_users function"""

    def test_update_expense_in_users_with_balances(self, users_and_groups, expenses_and_balances):
        """Test updating expense for users with balances"""
        user1, user2, user3, _, _ = users_and_groups
        expense1, _, _, balance1, _ = expenses_and_balances
        
        # Initially users should not have the expense
        assert expense1 not in user2.expenses
        assert expense1 not in user1.expenses  # creator
        
        update_expense_in_users(expense1)
        
        # After update, users with balances should have the expense
        assert expense1 in user2.expenses  # user with balance
        assert expense1 in user1.expenses  # creator
        
    def test_update_expense_in_users_no_balances(self, users_and_groups, expenses_and_balances):
        """Test updating expense with no balances (only creator)"""
        user1, user2, user3, _, _ = users_and_groups
        _, _, expense3, _, _ = expenses_and_balances
        
        # Initially creator should not have the expense
        assert expense3 not in user1.expenses
        
        update_expense_in_users(expense3)
        
        # After update, only creator should have the expense
        assert expense3 in user1.expenses  # creator
        assert expense3 not in user2.expenses  # no balance
        assert expense3 not in user3.expenses  # no balance

    def test_update_expense_in_users_creator_already_has_expense(self, users_and_groups, expenses_and_balances):
        """Test updating expense when creator already has the expense"""
        user1, user2, user3, _, _ = users_and_groups
        expense1, _, _, _, _ = expenses_and_balances
        
        # Manually add expense to creator first
        user1.add_expense(expense1)
        assert expense1 in user1.expenses
        
        # Count expenses before
        initial_creator_expense_count = len(user1.expenses)
        
        update_expense_in_users(expense1)
        
        # Creator should still have the expense (no duplicates)
        assert expense1 in user1.expenses
        assert len(user1.expenses) == initial_creator_expense_count  # No duplicate
        
        # User with balance should have the expense
        assert expense1 in user2.expenses

    def test_update_expense_in_users_multiple_balances(self, users_and_groups, db_session):
        """Test updating expense with multiple balances"""
        user1, user2, user3, group1, _ = users_and_groups
        
        # Create balance for user2
        balance1 = Balance.create(
            user_id=user2.id,
            owed=30.0,
            payed=20.0,
            total=10.0
        )
        
        # Create balance for user3
        balance2 = Balance.create(
            user_id=user3.id,
            owed=25.0,
            payed=15.0,
            total=10.0
        )
        
        # Create expense with multiple balances
        expense = Expense.create(
            amount=60.0,
            balances=[balance1, balance2],
            creator_id=user1.id,
            description="Multi-balance expense",
            group_id=group1.id
        )
        
        # Update balance relationships
        balance1.expense_id = expense.id
        balance2.expense_id = expense.id
        db_session.commit()
        
        # Initially no users should have the expense
        assert expense not in user1.expenses
        assert expense not in user2.expenses
        assert expense not in user3.expenses
        
        update_expense_in_users(expense)
        
        # After update, all users (balances + creator) should have the expense
        assert expense in user1.expenses  # creator
        assert expense in user2.expenses  # balance user
        assert expense in user3.expenses  # balance user

    def test_update_expense_in_users_empty_balances_list(self, users_and_groups, db_session):
        """Test updating expense with empty balances list"""
        user1, _, _, _, _ = users_and_groups
        
        # Create expense with no balances
        expense = Expense.create(
            amount=30.0,
            balances=[],
            creator_id=user1.id,
            description="No balance expense",
            group_id=NO_GROUP
        )
        
        db_session.commit()
        
        # Initially creator should not have the expense
        assert expense not in user1.expenses
        
        update_expense_in_users(expense)
        
        # After update, only creator should have the expense
        assert expense in user1.expenses