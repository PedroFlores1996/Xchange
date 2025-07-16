"""Tests for get_no_group_user_balances function"""

import pytest
from app.group import get_no_group_user_balances
from app.model.user import User


class TestGetNoGroupUserBalances:
    """Tests for get_no_group_user_balances function"""

    def test_get_no_group_user_balances_as_lender(self, users_and_group, debts_and_expenses):
        """Test getting balances when user is a lender"""
        user1, _, user3, _ = users_and_group
        group_balance1, group_balance2, group_balance3, debt3, *_ = debts_and_expenses
        
        result = get_no_group_user_balances(user1)
        
        assert len(result) == 1
        assert result[user3.id] == 20.0  # user1 lent 20 to user3

    def test_get_no_group_user_balances_as_borrower(self, users_and_group, debts_and_expenses):
        """Test getting balances when user is a borrower"""
        user1, _, user3, _ = users_and_group
        group_balance1, group_balance2, group_balance3, debt3, *_ = debts_and_expenses
        
        result = get_no_group_user_balances(user3)
        
        assert len(result) == 1
        assert result[user1.id] == -20.0  # user3 owes 20 to user1

    def test_get_no_group_user_balances_no_debts(self, db_session):
        """Test getting balances when user has no debts"""
        user = User.create("user", "user@test.com", "password")
        
        result = get_no_group_user_balances(user)
        
        assert result == {}