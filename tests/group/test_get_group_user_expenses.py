"""Tests for get_group_user_expenses function"""

import pytest
from app.group import get_group_user_expenses
from app.model.expense import Expense
from decimal import Decimal


class TestGetGroupUserExpenses:
    """Tests for get_group_user_expenses function"""

    def test_get_group_user_expenses_with_expenses(self, users_and_group, debts_and_expenses):
        """Test getting group expenses for user with expenses"""
        user1, _, _, group = users_and_group
        *_, expense1, _, expense3 = debts_and_expenses
        
        result = get_group_user_expenses(user1, group.id)
        
        assert len(result) == 1
        assert expense1 in result
        assert expense3 not in result  # No-group expense should not be included
        
        # Test sorting (most recent first)
        assert result == [expense1]

    def test_get_group_user_expenses_multiple_expenses(self, users_and_group, debts_and_expenses):
        """Test getting multiple group expenses and sorting"""
        user1, _, _, group = users_and_group
        *_, expense1, _, _ = debts_and_expenses
        
        # Create another expense for user1
        expense4 = Expense.create(
            amount=float(Decimal("50.00")),
            balances=[],
            creator_id=user1.id,
            description="Another group expense",
            group_id=group.id,
        )
        expense4.users.append(user1)
        
        result = get_group_user_expenses(user1, group.id)
        
        assert len(result) == 2
        assert expense1 in result
        assert expense4 in result
        # Should be sorted by created_at descending
        assert result[0].created_at >= result[1].created_at

    def test_get_group_user_expenses_no_expenses(self, users_and_group):
        """Test getting expenses when user has no expenses in group"""
        _, _, user3, group = users_and_group
        
        result = get_group_user_expenses(user3, group.id)
        
        assert result == []

    def test_get_group_user_expenses_wrong_group(self, users_and_group, debts_and_expenses):
        """Test getting expenses for non-existent group"""
        user1, _, _, _ = users_and_group
        
        result = get_group_user_expenses(user1, 999)  # Non-existent group
        
        assert result == []