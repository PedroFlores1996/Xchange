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
        debt1, debt2, _, *_ = debts_and_expenses
        
        result = get_group_user_debts(group)
        
        # Check structure
        assert isinstance(result, dict)
        assert len(result) == 3  # Three users in group
        
        # Check user1 (lender of debt1)
        user1_debts = result[user1.id]
        assert len(user1_debts[PAYED]) == 1
        assert user1_debts[PAYED][0] == debt1
        assert len(user1_debts[OWED]) == 0
        assert user1_debts[TOTAL] == 50.0
        
        # Check user2 (borrower of debt1, lender of debt2)
        user2_debts = result[user2.id]
        assert len(user2_debts[PAYED]) == 1
        assert user2_debts[PAYED][0] == debt2
        assert len(user2_debts[OWED]) == 1
        assert user2_debts[OWED][0] == debt1
        assert user2_debts[TOTAL] == -20.0  # 30 - 50
        
        # Check user3 (borrower of debt2)
        user3_debts = result[user3.id]
        assert len(user3_debts[PAYED]) == 0
        assert len(user3_debts[OWED]) == 1
        assert user3_debts[OWED][0] == debt2
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