"""Tests for get_group_user_balances function"""

import pytest
from app.group import get_group_user_balances
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt
from app.model.group_balance import GroupBalance
from decimal import Decimal


class TestGetGroupUserBalances:
    """Tests for get_group_user_balances function"""

    def test_get_group_user_balances_with_debts(self, users_and_group, debts_and_expenses):
        """Test getting user balances in group with debts"""
        user1, user2, user3, group = users_and_group
        
        result = get_group_user_balances(group)
        
        assert isinstance(result, dict)
        assert len(result) == 3
        
        # user1: has positive balance of 50
        assert result[user1] == 50.0
        
        # user2: has negative balance of 20
        assert result[user2] == -20.0
        
        # user3: has negative balance of 30
        assert result[user3] == -30.0

    def test_get_group_user_balances_empty_group(self, db_session):
        """Test getting balances for group with no debts"""
        user = User.create("user", "user@test.com", "password")
        group = Group.create("empty_group", [user])
        
        result = get_group_user_balances(group)
        
        # Should include all users with zero balance
        assert len(result) == 1
        assert result[user] == 0.0

    def test_get_group_user_balances_multiple_updates_same_users(self, users_and_group, db_session):
        """Test getting balances with multiple balance updates for same users"""
        user1, user2, _, group = users_and_group
        
        # Create multiple balance updates for same users
        GroupBalance.update_balance(user1.id, group.id, float(Decimal("50.00")))
        GroupBalance.update_balance(user1.id, group.id, float(Decimal("30.00")))
        GroupBalance.update_balance(user2.id, group.id, float(Decimal("-80.00")))
        db_session.commit()
        
        result = get_group_user_balances(group)
        
        # user1 should have total balance amount
        assert result[user1] == 80.0  # 50 + 30
        
        # user2 should have total owed amount
        assert result[user2] == -80.0