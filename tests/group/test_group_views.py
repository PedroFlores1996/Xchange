"""Unit tests for group views with mocking to achieve complete code coverage"""

import pytest
from unittest.mock import patch, MagicMock
from flask import url_for
from flask_login import login_user, logout_user


class TestCreateGroupView:
    """Test the create_group view endpoint"""

    @patch('app.group.views.handle_create_group')
    @patch('app.group.views.flash')
    def test_create_group_success(self, mock_flash, mock_handle, client, app, db_session):
        """Test successful group creation"""
        with app.test_request_context():
            # Mock successful group creation
            mock_group = MagicMock()
            mock_group.id = 123
            mock_handle.return_value = {
                'success': True,
                'group': mock_group,
                'message': 'Group created successfully!',
                'message_type': 'success'
            }
            
            # Create and login user
            from app.model.user import User
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Make request
            response = client.post('/groups', data={
                'name': 'Test Group',
                'description': 'Test Description',
                'csrf_token': 'test'
            }, follow_redirects=False)
            
            # Verify mocks were called
            assert mock_handle.called
            mock_flash.assert_called_once_with('Group created successfully!', 'success')
            
            # Verify redirect
            assert response.status_code == 302
            assert '/groups/123' in response.location
            
            logout_user()

    @patch('app.group.views.render_template')
    def test_create_group_invalid_form(self, mock_render, client, app, db_session):
        """Test group creation with invalid form data"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser2", "test2@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock the render_template to avoid template not found error
            from flask import Response
            mock_render.return_value = Response("Mocked template with errors", status=400)
            
            # Make request with invalid data (missing required fields)
            response = client.post('/groups', data={
                'csrf_token': 'test'
                # Missing name which is required
            })
            
            # Should return 400 due to form validation failure
            assert response.status_code == 400
            assert mock_render.called
            
            logout_user()


class TestCreateGroupFormView:
    """Test the create_group_form view endpoint"""

    @patch('app.group.views.render_template')
    def test_create_group_form_get(self, mock_render, client, app, db_session):
        """Test GET request to create group form"""
        with app.test_request_context():
            # Create user with friends
            from app.model.user import User
            user = User.create("testuser3", "test3@example.com", "password")
            friend = User.create("friend", "friend@example.com", "password")
            user.add_friends(friend)
            db_session.commit()
            login_user(user)
            
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/create_group_form')
            
            assert response.status_code == 200
            assert mock_render.called
            
            # Verify template was called with correct parameters
            call_args = mock_render.call_args
            assert call_args[0][0] == "group/create_group_form.html"
            assert 'form' in call_args[1]
            assert 'friends_data' in call_args[1]
            
            logout_user()


class TestGetGroupOverviewView:
    """Test the get_group_overview view endpoint"""

    @patch('app.group.views.prepare_group_overview_data')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_get_group_overview_success(self, mock_render, mock_get_group, mock_prepare, client, app, db_session):
        """Test successful group overview retrieval"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser4", "test4@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            
            # Mock template data
            mock_template_data = {
                'group': mock_group,
                'balances': {},
                'user_group_balance': 0.0,
                'user_group_debts': [],
                'recent_expenses': []
            }
            mock_prepare.return_value = mock_template_data
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_prepare.assert_called_once_with(mock_group)
            mock_render.assert_called_once_with("group/overview.html", **mock_template_data)
            
            logout_user()

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.jsonify')
    def test_get_group_overview_unauthorized(self, mock_jsonify, mock_get_group, client, app, db_session):
        """Test group overview with unauthorized access"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser5", "test5@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock unauthorized access
            mock_get_group.return_value = None
            mock_jsonify.return_value = MagicMock()
            
            response = client.get('/groups/999')
            
            mock_get_group.assert_called_once_with(999)
            mock_jsonify.assert_called_once_with({"error": "Group not found or access denied"})
            
            logout_user()


class TestGetGroupUsersView:
    """Test the get_group_users view endpoint"""

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_get_group_users_get(self, mock_render, mock_get_group, client, app, db_session):
        """Test GET request to group users page"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser6", "test6@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123/users')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_render.assert_called_once_with('group/users.html', group=mock_group)
            
            logout_user()

    @patch('app.group.views.handle_add_users_to_group')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    def test_get_group_users_post_success(self, mock_flash, mock_get_group, mock_handle, client, app, db_session):
        """Test POST request to add users to group"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser7", "test7@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            
            # Mock successful user addition
            mock_handle.return_value = {
                'success': True,
                'message': 'Users added successfully!',
                'message_type': 'success'
            }
            
            response = client.post('/groups/123/add-users', data={
                'friend_ids': '456,789',
                'csrf_token': 'test'
            }, follow_redirects=False)
            
            assert response.status_code == 302
            mock_handle.assert_called_once()
            mock_flash.assert_called_once_with('Users added successfully!', 'success')
            
            logout_user()

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    def test_get_group_users_unauthorized(self, mock_flash, mock_get_group, client, app, db_session):
        """Test group users page with unauthorized access"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser8", "test8@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock unauthorized access
            mock_get_group.return_value = None
            
            response = client.get('/groups/999/users', follow_redirects=False)
            
            assert response.status_code == 302
            mock_flash.assert_called_once_with("Group not found or access denied.", "danger")
            
            logout_user()


class TestGetGroupBalancesView:
    """Test the get_group_balances view endpoint"""

    @patch('app.group.views.prepare_group_balances_data')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_get_group_balances_success(self, mock_render, mock_get_group, mock_prepare, client, app, db_session):
        """Test successful group balances retrieval"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser9", "test9@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            
            # Mock template data
            mock_template_data = {
                'group': mock_group,
                'balances_abs': {},
                'balances': {},
                'balances_reversed': {}
            }
            mock_prepare.return_value = mock_template_data
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123/balances')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_prepare.assert_called_once_with(mock_group)
            mock_render.assert_called_once_with("group/balances.html", **mock_template_data)
            
            logout_user()

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.jsonify')
    def test_get_group_balances_unauthorized(self, mock_jsonify, mock_get_group, client, app, db_session):
        """Test group balances with unauthorized access"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser10", "test10@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock unauthorized access
            mock_get_group.return_value = None
            mock_jsonify.return_value = MagicMock()
            
            response = client.get('/groups/999/balances')
            
            mock_get_group.assert_called_once_with(999)
            mock_jsonify.assert_called_once_with({"error": "Group not found or access denied"})
            
            logout_user()


class TestGroupExpensesView:
    """Test the group_expenses view endpoint"""

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_group_expenses_success(self, mock_render, mock_get_group, client, app, db_session):
        """Test successful group expenses retrieval"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser11", "test11@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123/expenses')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_render.assert_called_once_with("group/expenses.html", group=mock_group)
            
            logout_user()

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.jsonify')
    def test_group_expenses_unauthorized(self, mock_jsonify, mock_get_group, client, app, db_session):
        """Test group expenses with unauthorized access"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser12", "test12@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock unauthorized access
            mock_get_group.return_value = None
            mock_jsonify.return_value = MagicMock()
            
            response = client.get('/groups/999/expenses')
            
            mock_get_group.assert_called_once_with(999)
            mock_jsonify.assert_called_once_with({"error": "Group not found or access denied"})
            
            logout_user()


class TestGroupDebtsView:
    """Test the get_group_debts view endpoint"""

    @patch('app.group.views.get_group_user_debts')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_get_group_debts_success(self, mock_render, mock_get_group, mock_get_debts, client, app, db_session):
        """Test successful group debts retrieval"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser13", "test13@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group and debts
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_user_debts = {}
            mock_get_debts.return_value = mock_user_debts
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123/debts')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_get_debts.assert_called_once_with(mock_group)
            mock_render.assert_called_once_with("group/debts.html", group=mock_group, user_debts=mock_user_debts)
            
            logout_user()

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.jsonify')
    def test_get_group_debts_unauthorized(self, mock_jsonify, mock_get_group, client, app, db_session):
        """Test group debts with unauthorized access"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser14", "test14@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock unauthorized access
            mock_get_group.return_value = None
            mock_jsonify.return_value = MagicMock()
            
            response = client.get('/groups/999/debts')
            
            mock_get_group.assert_called_once_with(999)
            mock_jsonify.assert_called_once_with({"error": "Group not found or access denied"})
            
            logout_user()


class TestNewGroupExpenseView:
    """Test the new_group_expense view endpoint"""

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_new_group_expense_success(self, mock_render, mock_get_group, client, app, db_session):
        """Test successful new group expense form"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser15", "test15@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123/new-expense')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            assert mock_render.called
            
            # Verify template was called with correct parameters
            call_args = mock_render.call_args
            assert call_args[0][0] == "expense/expense.html"
            assert 'form' in call_args[1]
            assert 'group' in call_args[1]
            assert 'pre_selected_group_id' in call_args[1]
            
            logout_user()

    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    def test_new_group_expense_unauthorized(self, mock_flash, mock_get_group, client, app, db_session):
        """Test new group expense with unauthorized access"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser16", "test16@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock unauthorized access
            mock_get_group.return_value = None
            
            response = client.get('/groups/999/new-expense', follow_redirects=False)
            
            assert response.status_code == 302
            mock_flash.assert_called_once_with("Group not found or access denied.", "danger")
            
            logout_user()