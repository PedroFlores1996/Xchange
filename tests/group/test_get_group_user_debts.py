"""Tests for get_group_user_debts function"""

import pytest
from app.group import get_group_user_debts
from app.model.user import User
from app.model.group import Group
from app.split.constants import OWED, PAYED, TOTAL


class TestGetGroupUserDebts:
    """Tests for get_group_user_debts function"""

    def test_get_group_user_debts_basic(self, users_and_group, debts_and_expenses):
        """Test basic debt calculation for group users"""
        user1, user2, user3, group = users_and_group
        group_balance1, group_balance2, group_balance3, _, *_ = debts_and_expenses
        
        result = get_group_user_debts(group)
        
        # Check structure
        assert isinstance(result, dict)
        assert len(result) == 3  # Three users in group
        
        # Check user1 (has positive balance - is owed 50)
        user1_debts = result[user1.id]
        assert len(user1_debts[PAYED]) == 0  # No individual debt records in new system
        assert len(user1_debts[OWED]) == 0   # No individual debt records in new system
        assert user1_debts[TOTAL] == 50.0
        
        # Check user2 (has negative balance - owes 20)
        user2_debts = result[user2.id]
        assert len(user2_debts[PAYED]) == 0  # No individual debt records in new system
        assert len(user2_debts[OWED]) == 0   # No individual debt records in new system
        assert user2_debts[TOTAL] == -20.0
        
        # Check user3 (has negative balance - owes 30)
        user3_debts = result[user3.id]
        assert len(user3_debts[PAYED]) == 0  # No individual debt records in new system
        assert len(user3_debts[OWED]) == 0   # No individual debt records in new system
        assert user3_debts[TOTAL] == -30.0

    def test_get_group_user_debts_empty_group(self, db_session):
        """Test debt calculation for group with no debts"""
        user = User.create("user", "user@test.com", "password")
        group = Group.create("empty_group", [user])
        
        result = get_group_user_debts(group)
        
        assert len(result) == 1
        user_debts = result[user.id]
        assert user_debts[PAYED] == []
        assert user_debts[OWED] == []
        assert user_debts[TOTAL] == 0.0