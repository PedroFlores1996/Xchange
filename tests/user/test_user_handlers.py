"""Tests for user business logic handlers in __init__.py"""

import pytest
from unittest.mock import patch, MagicMock
from app.user import (
    prepare_dashboard_data,
    handle_add_friend,
    prepare_friends_data,
    prepare_groups_data,
    prepare_balances_data,
    validate_friend_access,
    prepare_user_profile_data,
    validate_friend_for_settlement,
    calculate_friend_debt,
    process_friend_debt_settlement,
)
from app.model.user import User
from app.model.group import Group


class TestPrepareDashboardData:
    """Test the prepare_dashboard_data function"""

    @patch('app.group.get_no_group_debts')
    @patch('app.user.get_user_balances')
    def test_prepare_dashboard_data_success(self, mock_get_balances, mock_get_debts, user_with_groups):
        """Test successful dashboard data preparation"""
        # Mock debts
        mock_debt = MagicMock()
        mock_debt.amount = 50.0
        mock_get_debts.return_value = [mock_debt]
        
        # Mock balances (using the correct NO_GROUP constant)
        from app.model.constants import NO_GROUP
        mock_get_balances.return_value = ({1: 100.0, 2: -50.0, NO_GROUP: 25.0}, 75.0)
        
        result = prepare_dashboard_data(user_with_groups)
        
        assert 'current_user' in result
        assert 'no_group_debts' in result
        assert 'no_group_balance' in result
        assert 'groups' in result
        assert 'group_balances' in result
        assert 'overall_group_balance' in result
        assert 'expenses' in result
        
        assert result['no_group_balance'] == 25.0
        assert result['overall_group_balance'] == 50.0  # 75.0 - 25.0


class TestHandleAddFriend:
    """Test the handle_add_friend function"""

    def test_handle_add_friend_success(self, db_session):
        """Test successful friend addition"""
        user1 = User.create("user1", "user1@example.com", "password")
        user2 = User.create("user2", "user2@example.com", "password")
        db_session.commit()
        
        result = handle_add_friend(user1, "user2@example.com")
        
        assert result['success'] is True
        assert "user2" in result['message']
        assert result['message_type'] == 'success'
        assert result['redirect_to'] == 'user.friends'
        
    def test_handle_add_friend_already_friends(self, db_session):
        """Test adding a user who is already a friend"""
        user1 = User.create("user1", "user1@example.com", "password")
        user2 = User.create("user2", "user2@example.com", "password")
        user1.add_friends(user2)
        db_session.commit()
        
        result = handle_add_friend(user1, "user2@example.com")
        
        assert result['success'] is False
        assert "already your friend" in result['message']
        assert result['message_type'] == 'info'
        assert result['redirect_to'] == 'user.add_friend_form'
        
    def test_handle_add_friend_user_not_found(self, db_session):
        """Test adding a non-existent user"""
        user1 = User.create("user1", "user1@example.com", "password")
        db_session.commit()
        
        result = handle_add_friend(user1, "nonexistent@example.com")
        
        assert result['success'] is False
        assert "No user found" in result['message']
        assert result['message_type'] == 'danger'
        assert result['redirect_to'] == 'user.add_friend_form'


class TestPrepareFriendsData:
    """Test the prepare_friends_data function"""

    @patch('app.group.get_no_group_user_balances')
    def test_prepare_friends_data_success(self, mock_get_balances, user_with_friends):
        """Test successful friends data preparation"""
        mock_get_balances.return_value = {2: 50.0, 3: -25.0}
        
        result = prepare_friends_data(user_with_friends)
        
        assert 'friends' in result
        assert 'debts' in result
        assert len(result['friends']) == 2
        assert result['debts'] == {2: 50.0, 3: -25.0}


class TestPrepareGroupsData:
    """Test the prepare_groups_data function"""

    @patch('app.user.get_user_balances')
    def test_prepare_groups_data_success(self, mock_get_balances, user_with_groups):
        """Test successful groups data preparation"""
        from app.model.constants import NO_GROUP
        mock_get_balances.return_value = ({1: 100.0, 2: -50.0, NO_GROUP: 25.0}, 75.0)
        
        result = prepare_groups_data(user_with_groups)
        
        assert 'current_user' in result
        assert 'groups' in result
        assert 'group_balances' in result
        assert 'overall_balance' in result
        assert result['overall_balance'] == 50.0  # 75.0 - 25.0


class TestPrepareBalancesData:
    """Test the prepare_balances_data function"""

    @patch('app.user.get_user_balances')
    def test_prepare_balances_data_success(self, mock_get_balances, user_with_groups):
        """Test successful balances data preparation"""
        mock_get_balances.return_value = ({1: 100.0, 2: -50.0, 0: 25.0}, 75.0)
        
        result = prepare_balances_data(user_with_groups)
        
        assert 'groups' in result
        assert 'group_balances' in result
        assert 'overall_balance' in result
        assert result['overall_balance'] == 75.0
        
        # Check that balances are sorted by absolute value
        balances_items = list(result['group_balances'].items())
        assert abs(balances_items[0][1]) >= abs(balances_items[1][1])


class TestValidateFriendAccess:
    """Test the validate_friend_access function"""

    def test_validate_friend_access_same_user(self, user_with_friends):
        """Test validation when user_id is the current user"""
        result = validate_friend_access(user_with_friends, user_with_friends.id)
        
        assert result['valid'] is False
        assert result['redirect_required'] is True
        assert result['redirect_to'] == 'user.user_dashboard'
        
    def test_validate_friend_access_valid_friend(self, user_with_friends):
        """Test validation with a valid friend"""
        friend = user_with_friends.friends[0]
        
        result = validate_friend_access(user_with_friends, friend.id)
        
        assert result['valid'] is True
        assert result['friend'] == friend
        
    def test_validate_friend_access_invalid_user(self, user_with_friends):
        """Test validation with non-friend user"""
        result = validate_friend_access(user_with_friends, 9999)
        
        assert result['valid'] is False
        assert 'error' in result
        assert result['status_code'] == 403


class TestPrepareUserProfileData:
    """Test the prepare_user_profile_data function"""

    def test_prepare_user_profile_data_success(self, user_with_friends):
        """Test successful user profile data preparation"""
        user = user_with_friends
        friend = user.friends[0]
        
        # Mock some expenses and debts
        user.expenses = []
        user.lender_debts = []
        user.borrower_debts = []
        user.groups = []
        friend.groups = []
        
        result = prepare_user_profile_data(user, friend)
        
        assert 'friend' in result
        assert 'debt' in result
        assert 'expenses' in result
        assert 'common_groups' in result
        assert result['friend'] == friend


class TestValidateFriendForSettlement:
    """Test the validate_friend_for_settlement function"""

    def test_validate_friend_for_settlement_valid(self, user_with_friends):
        """Test validation with valid friend for settlement"""
        friend = user_with_friends.friends[0]
        
        result = validate_friend_for_settlement(user_with_friends, friend.id)
        
        assert result['valid'] is True
        assert result['friend'] == friend
        
    def test_validate_friend_for_settlement_invalid(self, user_with_friends):
        """Test validation with invalid friend for settlement"""
        result = validate_friend_for_settlement(user_with_friends, 9999)
        
        assert result['valid'] is False
        assert 'message' in result
        assert result['message_type'] == 'error'
        assert result['redirect_to'] == 'user.friends'


class TestCalculateFriendDebt:
    """Test the calculate_friend_debt function"""

    def test_calculate_friend_debt_user_owes(self, user_with_friends, db_session):
        """Test debt calculation when current user owes money"""
        from app.model.debt import Debt
        
        user = user_with_friends
        friend = user.friends[0]
        
        # Create real debt where friend is lender
        debt = Debt(lender_id=friend.id, borrower_id=user.id, amount=100.0)
        db_session.add(debt)
        db_session.commit()
        
        debt_obj, debt_amount = calculate_friend_debt(user, friend)
        
        assert debt_obj.id == debt.id
        assert debt_amount == -100.0  # Negative because user owes
        
    def test_calculate_friend_debt_user_owed(self, user_with_friends, db_session):
        """Test debt calculation when current user is owed money"""
        from app.model.debt import Debt
        
        user = user_with_friends
        friend = user.friends[0]
        
        # Create real debt where user is lender
        debt = Debt(lender_id=user.id, borrower_id=friend.id, amount=50.0)
        db_session.add(debt)
        db_session.commit()
        
        debt_obj, debt_amount = calculate_friend_debt(user, friend)
        
        assert debt_obj.id == debt.id
        assert debt_amount == 50.0  # Positive because user is owed
        
    def test_calculate_friend_debt_no_debt(self, user_with_friends):
        """Test debt calculation when no debt exists"""
        user = user_with_friends
        friend = user.friends[0]
        
        debt_obj, debt_amount = calculate_friend_debt(user, friend)
        
        assert debt_obj is None
        assert debt_amount == 0


class TestProcessFriendDebtSettlement:
    """Test the process_friend_debt_settlement function"""

    @patch('app.expense.submit.submit_expense')
    def test_process_friend_debt_settlement_success(self, mock_submit, user_with_friends):
        """Test successful debt settlement"""
        user = user_with_friends
        friend = user.friends[0]
        
        # Mock debt
        mock_debt = MagicMock()
        mock_debt.lender_id = user.id
        mock_debt.borrower_id = friend.id
        mock_debt.amount = 100.0
        
        # Mock successful expense submission
        mock_expense = MagicMock()
        mock_expense.id = 123
        mock_submit.return_value = mock_expense
        
        result = process_friend_debt_settlement(user, friend, mock_debt)
        
        assert result['success'] is True
        assert "Successfully settled debt" in result['message']
        assert result['message_type'] == 'success'
        assert result['redirect_to'] == 'user.user_profile'
        
    def test_process_friend_debt_settlement_no_debt(self, user_with_friends):
        """Test settlement when no debt exists"""
        user = user_with_friends
        friend = user.friends[0]
        
        result = process_friend_debt_settlement(user, friend, None)
        
        assert result['success'] is False
        assert "No debt found" in result['message']
        assert result['message_type'] == 'info'
        assert result['redirect_to'] == 'user.user_profile'
        
    @patch('app.expense.submit.submit_expense')
    @patch('app.database.db')
    def test_process_friend_debt_settlement_error(self, mock_db, mock_submit, user_with_friends):
        """Test settlement when an error occurs"""
        user = user_with_friends
        friend = user.friends[0]
        
        # Mock debt
        mock_debt = MagicMock()
        mock_debt.lender_id = user.id
        mock_debt.borrower_id = friend.id
        mock_debt.amount = 100.0
        
        # Mock exception during expense submission
        mock_submit.side_effect = Exception("Database error")
        
        result = process_friend_debt_settlement(user, friend, mock_debt)
        
        assert result['success'] is False
        assert "Error settling debt" in result['message']
        assert result['message_type'] == 'error'
        assert result['redirect_to'] == 'user.user_profile'
        mock_db.session.rollback.assert_called_once()