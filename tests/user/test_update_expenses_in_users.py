"""Tests for update_expenses_in_users function"""

import pytest
from app.user import update_expenses_in_users
from app.model.user import User
from app.model.expense import Expense
from app.model.balance import Balance
from app.model.constants import NO_GROUP


class TestUpdateExpensesInUsers:
    """Tests for update_expenses_in_users function"""

    def test_update_expenses_in_users_multiple_expenses(self, users_and_groups, expenses_and_balances):
        """Test updating multiple expenses in users"""
        user1, user2, user3, _, _ = users_and_groups
        expense1, expense2, expense3, _, _ = expenses_and_balances
        
        # Initially users should not have any expenses
        assert expense1 not in user1.expenses
        assert expense1 not in user2.expenses
        assert expense2 not in user1.expenses
        assert expense2 not in user3.expenses
        assert expense3 not in user1.expenses
        
        expenses = [expense1, expense2, expense3]
        update_expenses_in_users(expenses)
        
        # After update, users should have appropriate expenses
        # expense1: creator=user1, balance=user2
        assert expense1 in user1.expenses
        assert expense1 in user2.expenses
        
        # expense2: creator=user1, balance=user3  
        assert expense2 in user1.expenses
        assert expense2 in user3.expenses
        
        # expense3: creator=user1, no balances
        assert expense3 in user1.expenses

    def test_update_expenses_in_users_empty_list(self, users_and_groups):
        """Test updating with empty expenses list"""
        user1, user2, user3, _, _ = users_and_groups
        
        initial_user1_expenses = len(user1.expenses)
        initial_user2_expenses = len(user2.expenses)
        initial_user3_expenses = len(user3.expenses)
        
        update_expenses_in_users([])
        
        # No changes should occur
        assert len(user1.expenses) == initial_user1_expenses
        assert len(user2.expenses) == initial_user2_expenses
        assert len(user3.expenses) == initial_user3_expenses

    def test_update_expenses_in_users_single_expense(self, users_and_groups, expenses_and_balances):
        """Test updating single expense in list"""
        user1, user2, user3, _, _ = users_and_groups
        expense1, _, _, _, _ = expenses_and_balances
        
        # Initially users should not have the expense
        assert expense1 not in user1.expenses
        assert expense1 not in user2.expenses
        
        update_expenses_in_users([expense1])
        
        # After update, appropriate users should have the expense
        assert expense1 in user1.expenses  # creator
        assert expense1 in user2.expenses  # balance user
        assert expense1 not in user3.expenses  # no relation

    def test_update_expenses_in_users_duplicate_expenses(self, users_and_groups, expenses_and_balances):
        """Test updating with duplicate expenses in list"""
        user1, user2, user3, _, _ = users_and_groups
        expense1, _, _, _, _ = expenses_and_balances
        
        # Initially users should not have the expense
        assert expense1 not in user1.expenses
        assert expense1 not in user2.expenses
        
        # Pass the same expense multiple times
        update_expenses_in_users([expense1, expense1, expense1])
        
        # After update, users should have the expense only once
        assert expense1 in user1.expenses  # creator
        assert expense1 in user2.expenses  # balance user
        
        # Count should be 1 (no duplicates)
        user1_expense1_count = user1.expenses.count(expense1)
        user2_expense1_count = user2.expenses.count(expense1)
        assert user1_expense1_count == 1
        assert user2_expense1_count == 1

    def test_update_expenses_in_users_mixed_expense_types(self, users_and_groups, db_session):
        """Test updating expenses with different balance configurations"""
        user1, user2, user3, group1, _ = users_and_groups
        
        # Create expense with balance
        balance1 = Balance.create(
            user_id=user2.id,
            owed=30.0,
            payed=20.0,
            total=10.0
        )
        
        expense_with_balance = Expense.create(
            amount=50.0,
            balances=[balance1],
            creator_id=user1.id,
            description="Expense with balance",
            group_id=group1.id
        )
        balance1.expense_id = expense_with_balance.id
        
        # Create expense without balance
        expense_without_balance = Expense.create(
            amount=30.0,
            balances=[],
            creator_id=user1.id,
            description="Expense without balance",
            group_id=NO_GROUP
        )
        
        db_session.commit()
        
        # Initially users should not have any expenses
        assert expense_with_balance not in user1.expenses
        assert expense_with_balance not in user2.expenses
        assert expense_without_balance not in user1.expenses
        
        expenses = [expense_with_balance, expense_without_balance]
        update_expenses_in_users(expenses)
        
        # After update
        # expense_with_balance: creator + balance user
        assert expense_with_balance in user1.expenses
        assert expense_with_balance in user2.expenses
        assert expense_with_balance not in user3.expenses
        
        # expense_without_balance: only creator
        assert expense_without_balance in user1.expenses
        assert expense_without_balance not in user2.expenses
        assert expense_without_balance not in user3.expenses