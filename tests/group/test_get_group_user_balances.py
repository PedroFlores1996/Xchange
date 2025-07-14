"""Tests for get_group_user_balances function"""

import pytest
from app.group import get_group_user_balances
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt
from decimal import Decimal


class TestGetGroupUserBalances:
    """Tests for get_group_user_balances function"""

    def test_get_group_user_balances_with_debts(self, users_and_group, debts_and_expenses):
        """Test getting user balances in group with debts"""
        user1, user2, user3, group = users_and_group
        
        result = get_group_user_balances(group)
        
        assert isinstance(result, dict)
        assert len(result) == 3
        
        # user1: lent 50 to user2
        assert result[user1] == 50.0
        
        # user2: owes 50 to user1, lent 30 to user3
        assert result[user2] == -20.0  # 30 - 50
        
        # user3: owes 30 to user2
        assert result[user3] == -30.0

    def test_get_group_user_balances_empty_group(self, db_session):
        """Test getting balances for group with no debts"""
        user = User.create("user", "user@test.com", "password")
        group = Group.create("empty_group", [user])
        
        result = get_group_user_balances(group)
        
        assert result == {}

    def test_get_group_user_balances_multiple_debts_same_users(self, users_and_group, db_session):
        """Test getting balances with multiple debts between same users"""
        user1, user2, _, group = users_and_group
        
        # Create multiple debts between same users
        Debt.update(user2.id, user1.id, float(Decimal("50.00")), group.id)
        Debt.update(user2.id, user1.id, float(Decimal("30.00")), group.id)
        db_session.commit()
        
        result = get_group_user_balances(group)
        
        # user1 should have total lent amount
        assert result[user1] == 80.0  # 50 + 30
        
        # user2 should have total owed amount
        assert result[user2] == -80.0  # -(50 + 30)