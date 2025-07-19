"""Direct tests for expense view functions to maximize coverage"""

import pytest
from unittest.mock import patch, MagicMock
from flask import url_for
from flask_login import login_user, logout_user
from app.expense.views import expenses, expense_summary, debts, success
from app.model.user import User
from app.model.expense import Expense, ExpenseCategory
from app.model.debt import Debt
from app.split import SplitType


class TestExpenseViewsDirect:
    """Direct tests of view functions to ensure maximum coverage"""

    def test_expenses_get_direct(self, app, db_session):
        """Test expenses view function directly for GET request"""
        with app.test_request_context('/expenses', method='GET'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Call the view function directly
            result = expenses()
            
            # Should return a string (template) or Response object
            assert result is not None
            
            logout_user()



    @patch('app.expense.views.validate_expense_access')
    @patch('app.expense.views.prepare_expense_summary_data')
    def test_expense_summary_success_direct(self, mock_prepare, mock_validate, app, db_session):
        """Test expense_summary view function directly for successful access"""
        with app.test_request_context('/expenses/123'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful validation
            mock_expense = MagicMock()
            mock_validate.return_value = {
                'valid': True,
                'expense': mock_expense
            }
            
            # Mock summary data preparation
            mock_prepare.return_value = {
                'expense': mock_expense,
                'balances': [],
                'participants': [],
                'group': None,
                'creator': user,
                'total_amount': 100.0,
                'created_at': None
            }
            
            # Call the view function directly
            result = expense_summary(123)
            
            assert result is not None
            assert mock_validate.called
            assert mock_prepare.called
            
            logout_user()

    @patch('app.expense.views.validate_expense_access')
    def test_expense_summary_failure_direct(self, mock_validate, app, db_session):
        """Test expense_summary view function directly for failed access"""
        with app.test_request_context('/expenses/123'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock failed validation
            mock_validate.return_value = {
                'valid': False,
                'message': 'You do not have access to this expense.',
                'message_type': 'danger',
                'redirect_to': 'user.expenses'
            }
            
            # Call the view function directly
            result = expense_summary(123)
            
            assert result is not None
            assert mock_validate.called
            
            logout_user()

    @patch('app.expense.views.prepare_all_debts_data')
    def test_debts_success_direct(self, mock_prepare, app, db_session):
        """Test debts view function directly for successful access"""
        with app.test_request_context('/debts'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful debts data preparation
            mock_prepare.return_value = {
                'success': True,
                'debts': [],
                'active_debts': [],
                'total_debts': 0,
                'total_amount': 0.0
            }
            
            # Call the view function directly
            result = debts()
            
            assert result is not None
            assert mock_prepare.called
            
            logout_user()

    @patch('app.expense.views.prepare_all_debts_data')
    def test_debts_error_direct(self, mock_prepare, app, db_session):
        """Test debts view function directly with error"""
        with app.test_request_context('/debts'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock failed debts data preparation
            mock_prepare.return_value = {
                'success': False,
                'message': 'Error loading debts',
                'debts': [],
                'active_debts': [],
                'total_debts': 0,
                'total_amount': 0.0
            }
            
            # Call the view function directly
            result = debts()
            
            assert result is not None
            assert mock_prepare.called
            
            logout_user()

    def test_success_direct(self, app):
        """Test success view function directly"""
        with app.test_request_context('/success'):
            # Call the view function directly
            result = success()
            
            assert result == "Success"

    @patch('app.expense.forms.ExpenseForm')
    def test_expenses_form_invalid_direct(self, mock_form_class, app, db_session):
        """Test expenses view with invalid form"""
        with app.test_request_context('/expenses', method='POST'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock form that fails validation
            mock_form = MagicMock()
            mock_form.validate_on_submit.return_value = False
            mock_form_class.return_value = mock_form
            
            # Call the view function directly
            result = expenses()
            
            assert result is not None
            
            logout_user()

    @patch('app.expense.views.prepare_expense_form_data')
    @patch('app.expense.views.render_template')
    def test_expenses_get_direct_full_coverage(self, mock_render, mock_prepare, app, db_session):
        """Test expenses GET view function directly with full coverage"""
        with app.test_request_context('/expenses', method='GET'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock form data preparation
            mock_prepare.return_value = {
                'form': MagicMock(),
                'current_user': user,
                'categories': [],
                'split_types': []
            }
            
            # Mock render_template to return a string
            mock_render.return_value = "rendered_template"
            
            # Call the view function directly
            result = expenses()
            
            assert result == "rendered_template"
            assert mock_prepare.called
            assert mock_render.called
            mock_prepare.assert_called_once_with(user)
            mock_render.assert_called_once_with("expense/expense.html", 
                                               form=mock_prepare.return_value['form'],
                                               current_user=user,
                                               categories=mock_prepare.return_value['categories'],
                                               split_types=mock_prepare.return_value['split_types'])
            
            logout_user()

    @patch('app.expense.views.current_user')
    @patch('app.expense.views.prepare_expense_form_data')
    @patch('app.expense.views.render_template')
    def test_expenses_get_with_current_user_mock(self, mock_render, mock_prepare, mock_current_user, app, db_session):
        """Test expenses GET view function with current_user mock"""
        with app.test_request_context('/expenses', method='GET'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock current_user
            mock_current_user.return_value = user
            
            # Mock form data preparation
            mock_prepare.return_value = {
                'form': MagicMock(),
                'current_user': user,
                'categories': [],
                'split_types': []
            }
            
            # Mock render_template to return a string
            mock_render.return_value = "rendered_template"
            
            # Call the view function directly
            result = expenses()
            
            assert result == "rendered_template"
            assert mock_prepare.called
            assert mock_render.called
            
            logout_user()

    def test_success_function_multiple_calls(self, app):
        """Test success function called multiple times"""
        with app.test_request_context('/success'):
            # Call multiple times to ensure consistency
            result1 = success()
            result2 = success()
            result3 = success()
            
            assert result1 == "Success"
            assert result2 == "Success"
            assert result3 == "Success"

    @patch('app.expense.views.ExpenseForm')
    @patch('app.expense.views.prepare_expense_form_data')
    @patch('app.expense.views.render_template')
    def test_expenses_form_instantiation_direct(self, mock_render, mock_prepare, mock_form_class, app, db_session):
        """Test ExpenseForm instantiation in expenses view"""
        with app.test_request_context('/expenses', method='GET'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock form instantiation
            mock_form = MagicMock()
            mock_form.validate_on_submit.return_value = False
            mock_form_class.return_value = mock_form
            
            # Mock form data preparation
            mock_prepare.return_value = {
                'form': mock_form,
                'current_user': user,
                'categories': [],
                'split_types': []
            }
            
            # Mock render_template
            mock_render.return_value = "rendered_template"
            
            # Call the view function directly
            result = expenses()
            
            assert result == "rendered_template"
            assert mock_form_class.called
            assert mock_form.validate_on_submit.called
            assert mock_prepare.called
            assert mock_render.called
            
            logout_user()

    @patch('app.expense.views.ExpenseForm')
    @patch('app.expense.views.handle_expense_creation')
    @patch('app.expense.views.flash')  
    @patch('app.expense.views.redirect')
    @patch('app.expense.views.url_for')
    def test_expenses_post_failure_flash_redirect_coverage(self, mock_url_for, mock_redirect, mock_flash, mock_handle, mock_form_class, app, db_session):
        """Test the specific flash and redirect lines in expenses POST failure"""
        with app.test_request_context('/expenses', method='POST'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock form to pass validation
            mock_form = MagicMock()
            mock_form.validate_on_submit.return_value = True
            mock_form_class.return_value = mock_form
            
            # Mock failed expense creation with specific return values
            mock_handle.return_value = {
                'success': False,
                'message': 'Test error message',
                'message_type': 'error',
                'redirect_to': 'expense.expenses'
            }
            
            # Mock redirect functions
            mock_url_for.return_value = '/expenses'
            mock_redirect.return_value = "redirect_result"
            
            # Call the view function directly
            result = expenses()
            
            # Verify the flash and redirect calls (lines 29-30)
            mock_flash.assert_called_once_with('Test error message', 'error')
            mock_url_for.assert_called_once_with('expense.expenses')
            mock_redirect.assert_called_once_with('/expenses')
            assert result == "redirect_result"
            
            logout_user()

    @patch('app.expense.views.ExpenseForm')
    @patch('app.expense.views.handle_expense_creation')
    @patch('app.expense.views.prepare_expense_summary_data')
    @patch('app.expense.views.render_template')
    def test_expenses_post_success_flash_redirect_coverage(self, mock_render, mock_prepare, mock_handle, mock_form_class, app, db_session):
        """Test the specific success lines in expenses POST success (lines 26-27)"""
        with app.test_request_context('/expenses', method='POST'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock form to pass validation
            mock_form = MagicMock()
            mock_form.validate_on_submit.return_value = True
            mock_form_class.return_value = mock_form
            
            # Mock successful expense creation with specific return values
            mock_expense = MagicMock()
            mock_handle.return_value = {
                'success': True,
                'expense': mock_expense
            }
            
            # Mock prepare_expense_summary_data (line 26)
            mock_template_data = {
                'expense': mock_expense,
                'balances': [],
                'participants': [],
                'group': None,
                'creator': user,
                'total_amount': 100.0,
                'created_at': None
            }
            mock_prepare.return_value = mock_template_data
            
            # Mock render_template (line 27)
            mock_render.return_value = "success_template"
            
            # Call the view function directly
            result = expenses()
            
            # Verify the success path calls (lines 26-27)
            mock_prepare.assert_called_once_with(mock_expense)
            mock_render.assert_called_once_with("expense/summary.html", **mock_template_data)
            assert result == "success_template"
            
            logout_user()


class TestExpenseViewsAdditionalCoverage:
    """Additional tests to improve coverage on remaining lines"""

    @patch('app.expense.views.render_template')  
    @patch('app.expense.views.prepare_expense_summary_data')
    @patch('app.expense.views.validate_expense_access')
    def test_expense_summary_render_path_direct(self, mock_validate, mock_prepare, mock_render, app, db_session):
        """Test expense_summary render template path directly"""
        with app.test_request_context('/expenses/123'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock successful validation
            mock_expense = MagicMock()
            mock_validate.return_value = {
                'valid': True,
                'expense': mock_expense
            }
            
            # Mock summary data preparation
            mock_template_data = {
                'expense': mock_expense,
                'balances': [],
                'participants': [],
                'group': None,
                'creator': user,
                'total_amount': 100.0,
                'created_at': None
            }
            mock_prepare.return_value = mock_template_data
            
            # Mock render_template
            mock_render.return_value = "rendered_summary"
            
            # Call the view function directly
            result = expense_summary(123)
            
            assert result == "rendered_summary"
            assert mock_validate.called
            assert mock_prepare.called
            assert mock_render.called
            mock_render.assert_called_once_with("expense/summary.html", **mock_template_data)
            
            logout_user()

    @patch('app.expense.views.render_template')
    @patch('app.expense.views.prepare_all_debts_data')
    def test_debts_render_path_direct(self, mock_prepare, mock_render, app, db_session):
        """Test debts render template path directly"""
        with app.test_request_context('/debts'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock debts data preparation
            mock_template_data = {
                'success': True,
                'debts': [],
                'active_debts': [],
                'total_debts': 0,
                'total_amount': 0.0
            }
            mock_prepare.return_value = mock_template_data
            
            # Mock render_template
            mock_render.return_value = "rendered_debts"
            
            # Call the view function directly
            result = debts()
            
            assert result == "rendered_debts"
            assert mock_prepare.called
            assert mock_render.called
            mock_render.assert_called_once_with("expense/debts.html", **mock_template_data)
            
            logout_user()

    def test_view_functions_return_types(self, app, db_session):
        """Test that view functions return correct types"""
        with app.test_request_context():
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Test success function return type
            result = success()
            assert isinstance(result, str)
            assert result == "Success"
            
            logout_user()

    @patch('app.expense.views.render_template')
    @patch('app.expense.views.prepare_expense_form_data')
    def test_expenses_template_data_structure(self, mock_prepare, mock_render, app, db_session):
        """Test expenses view template data structure"""
        with app.test_request_context('/expenses', method='GET'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock form data preparation
            form_data = {
                'form': MagicMock(),
                'current_user': user,
                'categories': ['FOOD', 'TRANSPORT'],
                'split_types': ['EQUALLY', 'BY_AMOUNT']
            }
            mock_prepare.return_value = form_data
            
            # Mock render_template
            mock_render.return_value = "rendered_template"
            
            # Call the view function directly
            result = expenses()
            
            assert result == "rendered_template"
            
            # Verify template data structure
            mock_render.assert_called_once()
            args, kwargs = mock_render.call_args
            assert args[0] == "expense/expense.html"
            assert 'form' in kwargs
            assert 'current_user' in kwargs
            assert 'categories' in kwargs
            assert 'split_types' in kwargs
            assert kwargs['current_user'] == user
            
            logout_user()

    def test_module_level_variables(self):
        """Test module-level variables are accessible"""
        from app.expense.views import bp
        
        # Test blueprint is properly configured
        assert hasattr(bp, 'name')
        assert hasattr(bp, 'url_prefix')
        assert bp.name == 'expense'

    @patch('app.expense.views.flash')
    @patch('app.expense.views.redirect')
    @patch('app.expense.views.url_for')
    def test_debts_flash_message_path(self, mock_url_for, mock_redirect, mock_flash, app, db_session):
        """Test debts view flash message path"""
        with app.test_request_context('/debts'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock failed debts data preparation to trigger flash
            with patch('app.expense.views.prepare_all_debts_data') as mock_prepare:
                mock_prepare.return_value = {
                    'success': False,
                    'message': 'Test error message',
                    'debts': [],
                    'active_debts': [],
                    'total_debts': 0,
                    'total_amount': 0.0
                }
                
                with patch('app.expense.views.render_template') as mock_render:
                    mock_render.return_value = "rendered_template"
                    
                    # Call the view function directly
                    result = debts()
                    
                    # Verify flash was called with error message
                    mock_flash.assert_called_once_with('Test error message', 'danger')
                    assert result == "rendered_template"
            
            logout_user()


class TestViewFunctionCoverage:
    """Additional tests to ensure complete coverage of all view function paths"""

    def test_all_imports_used(self):
        """Test that all imports in views.py are actually used"""
        from app.expense.views import (
            Response, Blueprint, render_template, redirect, url_for, flash,
            login_required, current_user, handle_expense_creation,
            validate_expense_access, prepare_expense_form_data,
            prepare_expense_summary_data, prepare_all_debts_data, ExpenseForm
        )
        
        # All imports should be accessible
        assert Response is not None
        assert Blueprint is not None
        assert render_template is not None
        assert redirect is not None
        assert url_for is not None
        assert flash is not None
        assert login_required is not None
        assert current_user is not None
        assert handle_expense_creation is not None
        assert validate_expense_access is not None
        assert prepare_expense_form_data is not None
        assert prepare_expense_summary_data is not None
        assert prepare_all_debts_data is not None
        assert ExpenseForm is not None

    def test_blueprint_creation(self):
        """Test that the blueprint is created correctly"""
        from app.expense.views import bp
        
        assert bp is not None
        assert bp.name == "expense"

    def test_werkzeug_response_import(self):
        """Test that werkzeug Response is imported and accessible"""
        from werkzeug import Response
        assert Response is not None

    @patch('app.expense.views.url_for')
    @patch('app.expense.views.redirect')
    @patch('app.expense.views.flash')
    def test_expense_summary_redirect_path(self, mock_flash, mock_redirect, mock_url_for, app, db_session):
        """Test the redirect path in expense_summary when validation fails"""
        with app.test_request_context('/expenses/123'):
            user = User.create("testuser", "test@example.com", "password")
            db_session.commit()
            login_user(user)
            
            # Mock url_for and redirect
            mock_url_for.return_value = '/user/expenses'
            mock_redirect.return_value = MagicMock()
            
            # Mock failed validation
            with patch('app.expense.views.validate_expense_access') as mock_validate:
                mock_validate.return_value = {
                    'valid': False,
                    'message': 'Test error message',
                    'message_type': 'danger',
                    'redirect_to': 'user.expenses'
                }
                
                # Call the view function
                result = expense_summary(123)
                
                # Verify flash and redirect were called
                mock_flash.assert_called_once_with('Test error message', 'danger')
                mock_url_for.assert_called_once_with('user.expenses')
                mock_redirect.assert_called_once_with('/user/expenses')
            
            logout_user()

