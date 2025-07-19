"""Tests for group view handler methods in __init__.py"""

from unittest.mock import patch
from app.group import (
    handle_create_group,
    prepare_group_overview_data,
    handle_add_users_to_group,
    prepare_group_users_data,
    prepare_group_balances_data,
)
from app.model.user import User


class TestHandleCreateGroup:
    """Test the handle_create_group function"""

    def test_success_case_with_friend_ids(self, db_session):
        """Test successful group creation with friend_ids"""
        # Create users
        user = User.create("creator", "creator@example.com", "password")
        friend1 = User.create("friend1", "friend1@example.com", "password")
        friend2 = User.create("friend2", "friend2@example.com", "password")
        user.add_friends(friend1)
        user.add_friends(friend2)
        db_session.commit()
        
        # Mock current_user
        with patch('flask_login.current_user', user):
            form_data = {
                'name': 'Test Group',
                'description': 'Test Description',
                'friend_ids': f'{friend1.id},{friend2.id}',
                'users': []
            }
            
            result = handle_create_group(form_data)
            
            assert result['success'] is True
            assert 'group' in result
            assert result['message'] == "Group created successfully!"
            assert result['message_type'] == 'success'

    def test_success_case_with_users_field(self, db_session):
        """Test successful group creation with users field"""
        # Create users
        user = User.create("creator", "creator@example.com", "password")
        friend1 = User.create("friend1", "friend1@example.com", "password")
        db_session.commit()
        
        # Mock current_user
        with patch('flask_login.current_user', user):
            form_data = {
                'name': 'Test Group',
                'description': 'Test Description',
                'friend_ids': '',
                'users': [friend1.id]
            }
            
            result = handle_create_group(form_data)
            
            assert result['success'] is True
            assert 'group' in result

    def test_duplicate_user_ids_removed(self, db_session):
        """Test that duplicate user IDs are removed"""
        # Create users
        user = User.create("creator", "creator@example.com", "password")
        friend1 = User.create("friend1", "friend1@example.com", "password")
        db_session.commit()
        
        # Mock current_user
        with patch('flask_login.current_user', user):
            form_data = {
                'name': 'Test Group',
                'description': 'Test Description',
                'friend_ids': f'{friend1.id},{friend1.id}',  # Duplicate
                'users': [friend1.id]  # Also duplicate
            }
            
            result = handle_create_group(form_data)
            
            assert result['success'] is True
            assert 'group' in result


class TestPrepareGroupOverviewData:
    """Test the prepare_group_overview_data function"""

    @patch('app.group.get_group_user_balances')
    @patch('app.group.get_group_user_debts')
    @patch('app.group.get_group_user_expenses')
    @patch('flask_login.current_user')
    def test_overview_data_preparation(self, mock_current_user, mock_expenses, mock_debts, mock_balances, group_with_users):
        """Test successful group overview data preparation"""
        # Mock current_user
        mock_current_user.id = 1
        
        # Mock the helper functions
        mock_balances.return_value = {1: 50.0, 2: -25.0}
        mock_debts.return_value = {}
        mock_expenses.return_value = []
        
        result = prepare_group_overview_data(group_with_users)
        
        assert 'group' in result
        assert 'balances' in result
        assert 'user_group_balance' in result
        assert 'user_group_debts' in result
        assert 'recent_expenses' in result


class TestHandleAddUsersToGroup:
    """Test the handle_add_users_to_group function"""

    def test_success_case_add_new_users(self, group_with_users, db_session):
        """Test successfully adding new users to group"""
        # Create a new user not in group
        new_user = User.create("newuser", "new@example.com", "password")
        db_session.commit()
        
        form_data = {'friend_ids': str(new_user.id)}
        
        result = handle_add_users_to_group(group_with_users, form_data)
        
        assert result['success'] is True
        assert f"Successfully added {new_user.username} to {group_with_users.name}!" == result['message']
        assert result['message_type'] == 'success'

    def test_no_friend_ids_provided(self, group_with_users):
        """Test handling when no friend IDs are provided"""
        form_data = {'friend_ids': ''}
        
        result = handle_add_users_to_group(group_with_users, form_data)
        
        assert result['success'] is False
        assert "Please select at least one user to add." == result['message']
        assert result['message_type'] == 'warning'

    def test_users_already_in_group(self, group_with_users):
        """Test handling when users are already in group"""
        # Get an existing user from the group
        existing_user = group_with_users.users[0]
        
        form_data = {'friend_ids': str(existing_user.id)}
        
        result = handle_add_users_to_group(group_with_users, form_data)
        
        assert result['success'] is False
        assert "No new users to add or all selected users are already in the group." == result['message']
        assert result['message_type'] == 'warning'


class TestPrepareGroupUsersData:
    """Test the prepare_group_users_data function"""

    def test_friends_data_preparation(self, group_with_users):
        """Test successful friends data preparation"""
        # Mock current_user
        with patch('flask_login.current_user', group_with_users.users[0]):
            result = prepare_group_users_data(group_with_users)
            
            assert 'friends_data' in result
            assert isinstance(result['friends_data'], list)

    def test_no_available_friends(self, group_with_users):
        """Test when user has no available friends to add"""
        user = group_with_users.users[0]
        
        # Mock current_user with no additional friends
        with patch('flask_login.current_user', user):
            with patch.object(user, 'friends', list(group_with_users.users)):
                result = prepare_group_users_data(group_with_users)
                
                assert 'friends_data' in result


class TestPrepareGroupBalancesData:
    """Test the prepare_group_balances_data function"""

    @patch('app.group.get_group_user_balances')
    def test_balances_data_preparation(self, mock_balances, group_with_users):
        """Test successful balances data preparation"""
        mock_balances.return_value = {1: 100.0, 2: -50.0, 3: 25.0}
        
        result = prepare_group_balances_data(group_with_users)
        
        assert 'group' in result
        assert 'balances_abs' in result
        assert 'balances' in result
        assert 'balances_reversed' in result

    @patch('app.group.get_group_user_balances')
    def test_zero_balances_included(self, mock_balances, group_with_users):
        """Test that zero balances are properly handled"""
        mock_balances.return_value = {1: 0.0, 2: 50.0, 3: -25.0}
        
        result = prepare_group_balances_data(group_with_users)
        
        assert 'group' in result
        assert 'balances_abs' in result
        assert 'balances' in result
        assert 'balances_reversed' in result