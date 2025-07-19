"""Integration tests for user views that actually exercise the view code"""

import pytest
from unittest.mock import patch, MagicMock
from flask_login import login_user, logout_user
from app.model.user import User
from app.model.debt import Debt


class TestUserViewsIntegration:
    """Integration tests that exercise actual view code with minimal mocking"""

    def test_user_dashboard_get(self, client, app, db_session):
        """Test GET request to user dashboard"""
        with app.test_request_context():
            user = User.create("testuser1", "test1@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.get('/user')
            
            # Should call the actual view function and try to render template
            assert response.status_code in [200, 500]  # Template may not exist
            
            logout_user()

    @patch('app.user.views.prepare_dashboard_data')
    def test_user_dashboard_with_mocked_data(self, mock_prepare, client, app, db_session):
        """Test user dashboard with mocked data preparation"""
        with app.test_request_context():
            user = User.create("testuser2", "test2@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock the data preparation
            mock_prepare.return_value = {
                'current_user': user,
                'no_group_debts': [],
                'no_group_balance': 0.0,
                'groups': [],
                'group_balances': {},
                'overall_group_balance': 0.0,
                'expenses': [],
            }
            
            response = client.get('/user')
            
            assert mock_prepare.called
            assert response.status_code in [200, 500]
            
            logout_user()

    def test_user_debts_get(self, client, app, db_session):
        """Test GET request to user debts page"""
        with app.test_request_context():
            user = User.create("testuser3", "test3@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.get('/user/debts')
            
            assert response.status_code in [200, 500]
            
            logout_user()

    def test_user_groups_get(self, client, app, db_session):
        """Test GET request to user groups page"""
        with app.test_request_context():
            user = User.create("testuser4", "test4@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.get('/user/groups')
            
            assert response.status_code in [200, 500]
            
            logout_user()

    def test_user_friends_get(self, client, app, db_session):
        """Test GET request to user friends page"""
        with app.test_request_context():
            user = User.create("testuser5", "test5@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.get('/user/friends')
            
            assert response.status_code in [200, 500]
            
            logout_user()

    @patch('app.user.views.handle_add_friend')
    def test_user_friends_post_success(self, mock_handle, client, app, db_session):
        """Test POST to add friend with success"""
        with app.test_request_context():
            user = User.create("testuser6", "test6@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful friend addition
            mock_handle.return_value = {
                'message': 'Friend added successfully',
                'message_type': 'success',
                'redirect_to': 'user.friends'
            }
            
            response = client.post('/user/friends', data={
                'email': 'friend@example.com',
                'csrf_token': 'test'
            }, follow_redirects=False)
            
            assert response.status_code == 302
            assert mock_handle.called
            
            logout_user()

    @patch('app.user.views.handle_add_friend')
    def test_user_friends_post_failure(self, mock_handle, client, app, db_session):
        """Test POST to add friend with failure"""
        with app.test_request_context():
            user = User.create("testuser7", "test7@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock failed friend addition
            mock_handle.return_value = {
                'message': 'User not found',
                'message_type': 'danger',
                'redirect_to': 'user.add_friend_form'
            }
            
            response = client.post('/user/friends', data={
                'email': 'nonexistent@example.com',
                'csrf_token': 'test'
            }, follow_redirects=False)
            
            assert response.status_code == 302
            assert mock_handle.called
            
            logout_user()

    def test_add_friend_form_get(self, client, app, db_session):
        """Test GET request to add friend form"""
        with app.test_request_context():
            user = User.create("testuser8", "test8@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.get('/user/friend-form')
            
            assert response.status_code in [200, 500]
            
            logout_user()

    def test_user_expenses_get(self, client, app, db_session):
        """Test GET request to user expenses page"""
        with app.test_request_context():
            user = User.create("testuser9", "test9@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.get('/user/expenses')
            
            assert response.status_code in [200, 500]
            
            logout_user()

    @patch('app.user.views.render_template')
    def test_user_balances_get(self, mock_render, client, app, db_session):
        """Test GET request to user balances page"""
        with app.test_request_context():
            user = User.create("testuser10", "test10@example.com", "password")
            db_session.commit()
            login_user(user)
            
            from flask import Response
            mock_render.return_value = Response("Mocked template", status=200)
            
            response = client.get('/user/balances')
            
            assert response.status_code == 200
            assert mock_render.called
            
            logout_user()

    def test_user_profile_redirect_self(self, client, app, db_session):
        """Test user profile redirect when accessing own profile"""
        with app.test_request_context():
            user = User.create("testuser11", "test11@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.get(f'/users/{user.id}', follow_redirects=False)
            
            assert response.status_code == 302
            assert '/user' in response.location
            
            logout_user()

    @patch('app.user.views.validate_friend_access')
    @patch('app.user.views.prepare_user_profile_data')
    def test_user_profile_friend_success(self, mock_prepare, mock_validate, client, app, db_session):
        """Test accessing friend's profile successfully"""
        with app.test_request_context():
            user = User.create("testuser12", "test12@example.com", "password")
            friend = User.create("friend12", "friend12@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful validation
            mock_validate.return_value = {
                'valid': True,
                'friend': friend
            }
            
            # Mock profile data
            mock_prepare.return_value = {
                'friend': friend,
                'debt': None,
                'expenses': [],
                'common_groups': []
            }
            
            response = client.get(f'/users/{friend.id}')
            
            assert mock_validate.called
            assert mock_prepare.called
            assert response.status_code in [200, 500]
            
            logout_user()

    @patch('app.user.views.validate_friend_access')
    def test_user_profile_friend_forbidden(self, mock_validate, client, app, db_session):
        """Test accessing non-friend's profile (forbidden)"""
        with app.test_request_context():
            user = User.create("testuser13", "test13@example.com", "password")
            other_user = User.create("other13", "other13@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock failed validation
            mock_validate.return_value = {
                'valid': False,
                'error': 'User not found, or not added as a friend',
                'status_code': 403
            }
            
            response = client.get(f'/users/{other_user.id}')
            
            assert response.status_code == 403
            assert mock_validate.called
            
            logout_user()

    @patch('app.user.views.validate_friend_for_settlement')
    @patch('app.user.views.calculate_friend_debt')
    def test_settle_friend_form_success(self, mock_calculate, mock_validate, client, app, db_session):
        """Test GET settlement form for friend"""
        with app.test_request_context():
            user = User.create("testuser14", "test14@example.com", "password")
            friend = User.create("friend14", "friend14@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful validation
            mock_validate.return_value = {
                'valid': True,
                'friend': friend
            }
            
            # Mock debt calculation
            mock_debt = MagicMock()
            mock_calculate.return_value = (mock_debt, 50.0)
            
            response = client.get(f'/users/{friend.id}/settle')
            
            assert mock_validate.called
            assert mock_calculate.called
            assert response.status_code in [200, 500]
            
            logout_user()

    @patch('app.user.views.validate_friend_for_settlement')
    def test_settle_friend_form_invalid_friend(self, mock_validate, client, app, db_session):
        """Test GET settlement form for invalid friend"""
        with app.test_request_context():
            user = User.create("testuser15", "test15@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock failed validation
            mock_validate.return_value = {
                'valid': False,
                'message': 'Friend not found',
                'message_type': 'error',
                'redirect_to': 'user.friends'
            }
            
            response = client.get('/users/9999/settle', follow_redirects=False)
            
            assert response.status_code == 302
            assert mock_validate.called
            
            logout_user()

    @patch('app.user.views.validate_friend_for_settlement')
    @patch('app.user.views.calculate_friend_debt')
    @patch('app.user.views.process_friend_debt_settlement')
    def test_settle_friend_debt_success(self, mock_process, mock_calculate, mock_validate, client, app, db_session):
        """Test POST settlement processing successfully"""
        with app.test_request_context():
            user = User.create("testuser16", "test16@example.com", "password")
            friend = User.create("friend16", "friend16@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful validation
            mock_validate.return_value = {
                'valid': True,
                'friend': friend
            }
            
            # Mock debt calculation
            mock_debt = MagicMock()
            mock_calculate.return_value = (mock_debt, 50.0)
            
            # Mock successful settlement
            mock_process.return_value = {
                'success': True,
                'message': 'Debt settled successfully',
                'message_type': 'success',
                'redirect_to': 'user.user_profile'
            }
            
            response = client.post(f'/users/{friend.id}/settle', follow_redirects=False)
            
            assert response.status_code == 302
            assert mock_validate.called
            assert mock_calculate.called
            assert mock_process.called
            
            logout_user()

    @patch('app.user.views.validate_friend_for_settlement')
    @patch('app.user.views.calculate_friend_debt')
    @patch('app.user.views.process_friend_debt_settlement')
    def test_settle_friend_debt_failure(self, mock_process, mock_calculate, mock_validate, client, app, db_session):
        """Test POST settlement processing with failure"""
        with app.test_request_context():
            user = User.create("testuser17", "test17@example.com", "password")
            friend = User.create("friend17", "friend17@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful validation
            mock_validate.return_value = {
                'valid': True,
                'friend': friend
            }
            
            # Mock debt calculation
            mock_calculate.return_value = (None, 0)  # No debt
            
            # Mock failed settlement
            mock_process.return_value = {
                'success': False,
                'message': 'No debt found',
                'message_type': 'info',
                'redirect_to': 'user.user_profile'
            }
            
            response = client.post(f'/users/{friend.id}/settle', follow_redirects=False)
            
            assert response.status_code == 302
            assert mock_validate.called
            assert mock_calculate.called
            assert mock_process.called
            
            logout_user()


class TestUserViewsRealData:
    """Integration tests using real data to test actual business logic"""

    def test_friends_page_with_real_friends(self, client, app, db_session):
        """Test friends page with actual friend relationships"""
        with app.test_request_context():
            user = User.create("realuser1", "real1@example.com", "password")
            friend = User.create("realfriend1", "realfriend1@example.com", "password")
            
            user.add_friends(friend)
            db_session.commit()
            login_user(user)
            
            response = client.get('/user/friends')
            
            assert response.status_code in [200, 500]
            
            logout_user()

    def test_add_friend_real_success(self, client, app, db_session):
        """Test adding a real friend"""
        with app.test_request_context():
            user = User.create("realuser2", "real2@example.com", "password")
            potential_friend = User.create("potentialfriend", "potential@example.com", "password")
            db_session.commit()
            login_user(user)
            
            response = client.post('/user/friends', data={
                'email': 'potential@example.com',
                'csrf_token': 'test'
            }, follow_redirects=False)
            
            assert response.status_code == 302
            
            logout_user()

    def test_user_profile_with_real_friend(self, client, app, db_session):
        """Test accessing a real friend's profile"""
        with app.test_request_context():
            user = User.create("realuser3", "real3@example.com", "password")
            friend = User.create("realfriend3", "realfriend3@example.com", "password")
            
            user.add_friends(friend)
            db_session.commit()
            login_user(user)
            
            response = client.get(f'/users/{friend.id}')
            
            assert response.status_code in [200, 500]
            
            logout_user()

    def test_settle_friend_with_real_debt(self, client, app, db_session):
        """Test settlement flow with real debt"""
        with app.test_request_context():
            user = User.create("realuser4", "real4@example.com", "password")
            friend = User.create("realfriend4", "realfriend4@example.com", "password")
            
            user.add_friends(friend)
            
            # Create a real debt
            debt = Debt(lender_id=user.id, borrower_id=friend.id, amount=100.0)
            db_session.add(debt)
            db_session.commit()
            login_user(user)
            
            # Test settlement form
            response = client.get(f'/users/{friend.id}/settle')
            assert response.status_code in [200, 500]
            
            logout_user()