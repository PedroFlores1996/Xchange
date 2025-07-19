"""Tests for view handler functions in app.group.__init__"""

import pytest
from flask_login import login_user, logout_user
from app.group import (
    handle_create_group,
    prepare_group_overview_data,
    handle_add_users_to_group,
    prepare_group_users_data,
    prepare_group_balances_data,
)
from app.model.user import User
from app.model.group import Group
from app.model.group_balance import GroupBalance


class TestHandleCreateGroup:
    """Test the handle_create_group function"""

    def test_success_case_with_friend_ids(self, app, db_session):
        """Test successful group creation with friend IDs"""
        with app.test_request_context():
            # Create users
            user1 = User.create("creator", "creator@example.com", "password")
            user2 = User.create("friend1", "friend1@example.com", "password")
            user3 = User.create("friend2", "friend2@example.com", "password")
            db_session.commit()
            
            # Login the creator
            login_user(user1)
            
            form_data = {
                'name': 'Test Group',
                'description': 'A test group',
                'friend_ids': f'{user2.id},{user3.id}',
                'users': None
            }
            
            result = handle_create_group(form_data)
            
            assert result['success'] is True
            assert result['group'].name == 'Test Group'
            assert result['message'] == "Group created successfully!"
            assert result['message_type'] == 'success'
            assert len(result['group'].users) == 3  # creator + 2 friends
            
            logout_user()

    def test_success_case_with_users_field(self, app, db_session):
        """Test successful group creation with users field (backwards compatibility)"""
        with app.test_request_context():
            user1 = User.create("creator2", "creator2@example.com", "password")
            user2 = User.create("user2", "user2@example.com", "password")
            db_session.commit()
            
            login_user(user1)
            
            form_data = {
                'name': 'Test Group 2',
                'description': 'Another test group',
                'friend_ids': None,
                'users': [user2.id]
            }
            
            result = handle_create_group(form_data)
            
            assert result['success'] is True
            assert result['group'].name == 'Test Group 2'
            assert len(result['group'].users) == 2  # creator + 1 user
            
            logout_user()

    def test_duplicate_user_ids_removed(self, app, db_session):
        """Test that duplicate user IDs are removed"""
        with app.test_request_context():
            user1 = User.create("creator3", "creator3@example.com", "password")
            user2 = User.create("duplicate", "duplicate@example.com", "password")
            db_session.commit()
            
            login_user(user1)
            
            form_data = {
                'name': 'Duplicate Test Group',
                'description': 'Testing duplicates',
                'friend_ids': f'{user2.id}',
                'users': [user2.id]  # Same user in both fields
            }
            
            result = handle_create_group(form_data)
            
            assert result['success'] is True
            assert len(result['group'].users) == 2  # creator + 1 unique user
            
            logout_user()


class TestPrepareGroupOverviewData:
    """Test the prepare_group_overview_data function"""

    def test_overview_data_preparation(self, app, users_and_group, db_session):
        """Test that overview data is prepared correctly"""
        with app.test_request_context():
            user1, user2, user3, group = users_and_group
            
            # Create some group balances
            GroupBalance.update_balance(user1.id, group.id, 50.0)
            GroupBalance.update_balance(user2.id, group.id, -30.0)
            db_session.commit()
            
            login_user(user1)
            
            result = prepare_group_overview_data(group)
            
            assert result['group'] == group
            assert 'balances' in result
            assert 'user_group_balance' in result
            assert 'user_group_debts' in result
            assert 'recent_expenses' in result
            assert isinstance(result['user_group_debts'], list)
            
            logout_user()


class TestHandleAddUsersToGroup:
    """Test the handle_add_users_to_group function"""

    def test_success_case_add_new_users(self, users_and_group, db_session):
        """Test successfully adding new users to group"""
        user1, user2, user3, group = users_and_group
        
        # Create a new user not in the group
        user4 = User.create("newuser", "newuser@example.com", "password")
        db_session.commit()
        
        form_data = {'friend_ids': str(user4.id)}
        
        result = handle_add_users_to_group(group, form_data)
        
        assert result['success'] is True
        assert result['message_type'] == 'success'
        assert 'newuser' in result['message']

    def test_no_friend_ids_provided(self, users_and_group, db_session):
        """Test when no friend IDs are provided"""
        user1, user2, user3, group = users_and_group
        
        form_data = {'friend_ids': None}
        
        result = handle_add_users_to_group(group, form_data)
        
        assert result['success'] is False
        assert result['message'] == "Please select at least one user to add."
        assert result['message_type'] == 'warning'

    def test_users_already_in_group(self, users_and_group, db_session):
        """Test when selected users are already in the group"""
        user1, user2, user3, group = users_and_group
        
        form_data = {'friend_ids': str(user2.id)}  # user2 is already in group
        
        result = handle_add_users_to_group(group, form_data)
        
        assert result['success'] is False
        assert result['message'] == "No new users to add or all selected users are already in the group."
        assert result['message_type'] == 'warning'


class TestPrepareGroupUsersData:
    """Test the prepare_group_users_data function"""

    def test_friends_data_preparation(self, app, users_and_group, db_session):
        """Test that friends data is prepared correctly"""
        with app.test_request_context():
            user1, user2, user3, group = users_and_group
            
            # Create a friend not in the group
            friend = User.create("friend", "friend@example.com", "password")
            user1.add_friends(friend)  # Fix: pass single friend, not list
            db_session.commit()
            
            login_user(user1)
            
            result = prepare_group_users_data(group)
            
            assert 'friends_data' in result
            assert isinstance(result['friends_data'], list)
            # friend should be in the list since they're not in the group
            friend_ids = [f['id'] for f in result['friends_data']]
            assert friend.id in friend_ids
            
            logout_user()

    def test_no_available_friends(self, app, users_and_group, db_session):
        """Test when there are no available friends to add"""
        with app.test_request_context():
            user1, user2, user3, group = users_and_group
            
            login_user(user1)
            
            result = prepare_group_users_data(group)
            
            assert 'friends_data' in result
            assert isinstance(result['friends_data'], list)
            # Should be empty since all friends are already in the group or no friends exist
            
            logout_user()


class TestPrepareGroupBalancesData:
    """Test the prepare_group_balances_data function"""

    def test_balances_data_preparation(self, users_and_group, db_session):
        """Test that balances data is prepared with correct sorting"""
        user1, user2, user3, group = users_and_group
        
        # Create balances with different values
        GroupBalance.update_balance(user1.id, group.id, 50.0)   # Most positive
        GroupBalance.update_balance(user2.id, group.id, -30.0)  # Most negative
        GroupBalance.update_balance(user3.id, group.id, 10.0)   # Middle positive
        db_session.commit()
        
        result = prepare_group_balances_data(group)
        
        assert result['group'] == group
        assert 'balances_abs' in result
        assert 'balances' in result
        assert 'balances_reversed' in result
        
        # Check that sorting works correctly
        balances_list = list(result['balances'].values())
        assert balances_list == sorted(balances_list)  # Should be sorted ascending
        
        balances_reversed_list = list(result['balances_reversed'].values())
        assert balances_reversed_list == sorted(balances_reversed_list, reverse=True)  # Should be sorted descending

    def test_zero_balances_included(self, users_and_group, db_session):
        """Test that users with zero balances are included"""
        user1, user2, user3, group = users_and_group
        
        # Only set balance for one user, others should have zero
        GroupBalance.update_balance(user1.id, group.id, 25.0)
        db_session.commit()
        
        result = prepare_group_balances_data(group)
        
        # All users should be in the result
        assert len(result['balances']) == 3
        assert len(result['balances_abs']) == 3
        assert len(result['balances_reversed']) == 3