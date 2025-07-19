"""Unit tests for settlement views with mocking"""

import pytest
from unittest.mock import patch, MagicMock
from flask_login import login_user, logout_user


class TestSettleDebtsPreviewView:
    """Test the settle_debts_preview view endpoint"""

    @patch('app.group.views.calculate_group_settlement_transactions')
    @patch('app.group.views.check_group_has_balances')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_settle_debts_preview_success(self, mock_render, mock_get_group, mock_check_balances, mock_calculate, client, app, db_session):
        """Test successful settlement preview"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser17", "test17@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group with balances
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_check_balances.return_value = True
            mock_calculate.return_value = [{'amount': 50.0}]
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123/settle')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_check_balances.assert_called_once_with(mock_group)
            mock_calculate.assert_called_once_with(mock_group)
            assert mock_render.called
            
            logout_user()

    @patch('app.group.views.check_group_has_balances')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    def test_settle_debts_preview_no_balances(self, mock_flash, mock_get_group, mock_check_balances, client, app, db_session):
        """Test settlement preview when no balances exist"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser18", "test18@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group without balances
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_check_balances.return_value = False
            
            response = client.get('/groups/123/settle', follow_redirects=False)
            
            assert response.status_code == 302
            mock_flash.assert_called_once_with("No Active Debts to Settle", "info")
            
            logout_user()


class TestSettleDebtsProcessView:
    """Test the settle_debts_process view endpoint"""

    @patch('app.group.views.handle_settle_debts_process')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    @patch('app.group.views.render_template')
    def test_settle_debts_process_success(self, mock_render, mock_flash, mock_get_group, mock_handle, client, app, db_session):
        """Test successful debt settlement processing"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser19", "test19@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group and successful processing
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_handle.return_value = {
                'success': True,
                'message': 'Settlement successful',
                'message_type': 'success',
                'settlement_expenses': []
            }
            mock_render.return_value = "mocked template"
            
            response = client.post('/groups/123/settle')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_handle.assert_called_once_with(mock_group)
            mock_flash.assert_called_once_with('Settlement successful', 'success')
            assert mock_render.called
            
            logout_user()

    @patch('app.group.views.handle_settle_debts_process')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    def test_settle_debts_process_failure(self, mock_flash, mock_get_group, mock_handle, client, app, db_session):
        """Test debt settlement processing failure"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser20", "test20@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group and failed processing
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_handle.return_value = {
                'success': False,
                'message': 'No debts to settle',
                'message_type': 'info'
            }
            
            response = client.post('/groups/123/settle', follow_redirects=False)
            
            assert response.status_code == 302
            mock_flash.assert_called_once_with('No debts to settle', 'info')
            
            logout_user()


class TestIndividualBalanceConfirmationView:
    """Test the settle_individual_balance_confirmation view endpoint"""

    @patch('app.group.views.handle_individual_balance_confirmation')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_individual_balance_confirmation_success(self, mock_render, mock_get_group, mock_handle, client, app, db_session):
        """Test successful individual balance confirmation"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser21", "test21@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group and successful confirmation
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_user = MagicMock()
            mock_handle.return_value = {
                'success': True,
                'user': mock_user,
                'user_balance': 50.0,
                'settlement_transactions': []
            }
            mock_render.return_value = "mocked template"
            
            response = client.get('/groups/123/settle/456')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_handle.assert_called_once_with(mock_group, 456)
            assert mock_render.called
            
            logout_user()

    @patch('app.group.views.handle_individual_balance_confirmation')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    def test_individual_balance_confirmation_failure(self, mock_flash, mock_get_group, mock_handle, client, app, db_session):
        """Test individual balance confirmation failure"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser22", "test22@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group and failed confirmation
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_handle.return_value = {
                'success': False,
                'message': 'No balance to settle',
                'message_type': 'info'
            }
            
            response = client.get('/groups/123/settle/456', follow_redirects=False)
            
            assert response.status_code == 302
            mock_flash.assert_called_once_with('No balance to settle', 'info')
            
            logout_user()


class TestIndividualBalanceProcessView:
    """Test the settle_individual_balance_process view endpoint"""

    @patch('app.group.views.handle_individual_balance_process')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.render_template')
    def test_individual_balance_process_success(self, mock_render, mock_get_group, mock_handle, client, app, db_session):
        """Test successful individual balance processing"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser23", "test23@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group and successful processing
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_user = MagicMock()
            mock_handle.return_value = {
                'success': True,
                'user': mock_user,
                'settlement_expenses': []
            }
            mock_render.return_value = "mocked template"
            
            response = client.post('/groups/123/settle/456')
            
            assert response.status_code == 200
            mock_get_group.assert_called_once_with(123)
            mock_handle.assert_called_once_with(mock_group, 456)
            assert mock_render.called
            
            logout_user()

    @patch('app.group.views.handle_individual_balance_process')
    @patch('app.group.views.get_authorized_group')
    @patch('app.group.views.flash')
    def test_individual_balance_process_failure(self, mock_flash, mock_get_group, mock_handle, client, app, db_session):
        """Test individual balance processing failure"""
        with app.test_request_context():
            # Create and login user
            from app.model.user import User
            user = User.create("testuser24", "test24@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock authorized group and failed processing
            mock_group = MagicMock()
            mock_get_group.return_value = mock_group
            mock_handle.return_value = {
                'success': False,
                'message': 'User not found',
                'message_type': 'danger'
            }
            
            response = client.post('/groups/123/settle/456', follow_redirects=False)
            
            assert response.status_code == 302
            mock_flash.assert_called_once_with('User not found', 'danger')
            
            logout_user()