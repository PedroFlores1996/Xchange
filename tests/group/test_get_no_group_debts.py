"""Tests for get_no_group_debts function"""

import pytest
from app.group import get_no_group_debts
from app.model.user import User


class TestGetNoGroupDebts:
    """Tests for get_no_group_debts function"""

    def test_get_no_group_debts_with_debts(self, users_and_group, debts_and_expenses):
        """Test getting no-group debts when user has both group and no-group debts"""
        user1, _, _, _ = users_and_group
        debt1, _, debt3, *_ = debts_and_expenses
        
        result = get_no_group_debts(user1)
        
        assert len(result) == 1
        assert debt3 in result
        assert debt1 not in result  # Group debt should not be included

    def test_get_no_group_debts_no_debts(self, db_session):
        """Test getting no-group debts when user has no debts"""
        user = User.create("user", "user@test.com", "password")
        
        result = get_no_group_debts(user)
        
        assert result == []

    def test_get_no_group_debts_only_group_debts(self, users_and_group, debts_and_expenses):
        """Test getting no-group debts when user only has group debts"""
        _, user2, _, _ = users_and_group
        
        result = get_no_group_debts(user2)  # user2 only has group debts
        
        assert result == []