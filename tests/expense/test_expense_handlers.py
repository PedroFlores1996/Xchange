"""Tests for expense business logic handlers in __init__.py"""

import pytest
from unittest.mock import patch, MagicMock
from app.expense import (
    handle_expense_creation,
    validate_expense_access,
    prepare_expense_form_data,
    prepare_expense_summary_data,
    prepare_all_debts_data,
    handle_expense_form_validation,
)
from app.model.user import User
from app.model.expense import Expense, ExpenseCategory
from app.model.debt import Debt
from app.model.group import Group
from app.split import SplitType


class TestHandleExpenseCreation:
    """Test the handle_expense_creation function"""

    @patch('app.expense.submit.submit_expense')
    @patch('app.expense.mapper.map_form_to_expense_data')
    def test_handle_expense_creation_success(self, mock_map_form, mock_submit, db_session):
        """Test successful expense creation"""
        # Create a user and expense
        user = User.create("testuser", "test@example.com", "password")
        db_session.commit()
        
        # Mock form data
        mock_form = MagicMock()
        mock_expense_data = MagicMock()
        mock_expense = MagicMock()
        mock_expense.id = 123
        
        mock_map_form.return_value = mock_expense_data
        mock_submit.return_value = mock_expense
        
        result = handle_expense_creation(mock_form)
        
        assert result['success'] is True
        assert result['expense'] == mock_expense
        assert result['message'] == 'Expense created successfully!'
        assert result['message_type'] == 'success'
        assert result['redirect_to'] == 'expense.expense_summary'
        assert result['expense_id'] == 123

    @patch('app.expense.submit.submit_expense')
    @patch('app.expense.mapper.map_form_to_expense_data')
    def test_handle_expense_creation_failure(self, mock_map_form, mock_submit, db_session):
        """Test expense creation failure"""
        mock_form = MagicMock()
        mock_expense_data = MagicMock()
        
        mock_map_form.return_value = mock_expense_data
        mock_submit.side_effect = Exception("Database error")
        
        result = handle_expense_creation(mock_form)
        
        assert result['success'] is False
        assert "Error creating expense" in result['message']
        assert result['message_type'] == 'danger'
        assert result['redirect_to'] == 'expense.expenses'


class TestValidateExpenseAccess:
    """Test the validate_expense_access function"""

    def test_validate_expense_access_creator(self, db_session):
        """Test validation when user is expense creator"""
        user = User.create("creator", "creator@example.com", "password")
        expense = Expense.create(
            amount=100.0,
            description="Test expense",
            creator_id=user.id,
            category=ExpenseCategory.FOOD,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            group_id=None,
            balances=[]
        )
        db_session.commit()
        
        result = validate_expense_access(expense.id, user)
        
        assert result['valid'] is True
        assert result['expense'] == expense

    def test_validate_expense_access_participant(self, db_session):
        """Test validation when user is expense participant"""
        creator = User.create("creator", "creator@example.com", "password")
        participant = User.create("participant", "participant@example.com", "password")
        
        expense = Expense.create(
            amount=100.0,
            description="Test expense",
            creator_id=creator.id,
            category=ExpenseCategory.FOOD,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            group_id=None,
            balances=[]
        )
        expense.users.append(participant)
        db_session.commit()
        
        result = validate_expense_access(expense.id, participant)
        
        assert result['valid'] is True
        assert result['expense'] == expense

    def test_validate_expense_access_group_member(self, db_session):
        """Test validation when user is in expense group"""
        creator = User.create("creator", "creator@example.com", "password")
        group_member = User.create("member", "member@example.com", "password")
        
        group = Group.create("Test Group", [creator, group_member])
        
        expense = Expense.create(
            amount=100.0,
            description="Test expense",
            creator_id=creator.id,
            category=ExpenseCategory.FOOD,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            group_id=group.id,
            balances=[]
        )
        db_session.commit()
        
        result = validate_expense_access(expense.id, group_member)
        
        assert result['valid'] is True
        assert result['expense'] == expense

    def test_validate_expense_access_not_found(self, db_session):
        """Test validation when expense doesn't exist"""
        user = User.create("testuser", "test@example.com", "password")
        db_session.commit()
        
        result = validate_expense_access(9999, user)
        
        assert result['valid'] is False
        assert result['message'] == 'Expense not found.'
        assert result['message_type'] == 'danger'
        assert result['redirect_to'] == 'user.expenses'

    def test_validate_expense_access_unauthorized(self, db_session):
        """Test validation when user has no access"""
        creator = User.create("creator", "creator@example.com", "password")
        unauthorized_user = User.create("unauthorized", "unauthorized@example.com", "password")
        
        expense = Expense.create(
            amount=100.0,
            description="Test expense",
            creator_id=creator.id,
            category=ExpenseCategory.FOOD,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            group_id=None,
            balances=[]
        )
        db_session.commit()
        
        result = validate_expense_access(expense.id, unauthorized_user)
        
        assert result['valid'] is False
        assert result['message'] == 'You do not have access to this expense.'
        assert result['message_type'] == 'danger'
        assert result['redirect_to'] == 'user.expenses'


class TestPrepareExpenseFormData:
    """Test the prepare_expense_form_data function"""

    def test_prepare_expense_form_data_success(self, db_session):
        """Test successful expense form data preparation"""
        user = User.create("testuser", "test@example.com", "password")
        db_session.commit()
        
        result = prepare_expense_form_data(user)
        
        assert 'form' in result
        assert result['current_user'] == user
        assert 'categories' in result
        assert 'split_types' in result
        assert isinstance(result['categories'], list)
        assert isinstance(result['split_types'], list)


class TestPrepareExpenseSummaryData:
    """Test the prepare_expense_summary_data function"""

    def test_prepare_expense_summary_data_success(self, db_session):
        """Test successful expense summary data preparation"""
        user = User.create("testuser", "test@example.com", "password")
        
        expense = Expense.create(
            amount=100.0,
            description="Test expense",
            creator_id=user.id,
            category=ExpenseCategory.FOOD,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            group_id=None,
            balances=[]
        )
        db_session.commit()
        
        result = prepare_expense_summary_data(expense)
        
        assert result['expense'] == expense
        assert result['balances'] == expense.balances
        assert result['participants'] == expense.users
        assert result['group'] is None  # No group for this expense
        assert result['creator'] == expense.creator
        assert result['total_amount'] == expense.amount
        assert 'created_at' in result

    def test_prepare_expense_summary_data_with_group(self, db_session):
        """Test expense summary data preparation with group"""
        user = User.create("testuser", "test@example.com", "password")
        group = Group.create("Test Group", [user])
        
        expense = Expense.create(
            amount=100.0,
            description="Test expense",
            creator_id=user.id,
            category=ExpenseCategory.FOOD,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            group_id=group.id,
            balances=[]
        )
        db_session.commit()
        
        result = prepare_expense_summary_data(expense)
        
        assert result['expense'] == expense
        assert result['group'] == expense.group


class TestPrepareAllDebtsData:
    """Test the prepare_all_debts_data function"""

    def test_prepare_all_debts_data_success(self, db_session):
        """Test successful debts data preparation"""
        user1 = User.create("user1", "user1@example.com", "password")
        user2 = User.create("user2", "user2@example.com", "password")
        user3 = User.create("user3", "user3@example.com", "password")
        
        # Create some debts with different lender-borrower pairs to avoid unique constraint
        debt1 = Debt(lender_id=user1.id, borrower_id=user2.id, amount=50.0)
        debt2 = Debt(lender_id=user2.id, borrower_id=user1.id, amount=30.0)
        debt3 = Debt(lender_id=user1.id, borrower_id=user3.id, amount=0.0)  # Settled debt
        
        db_session.add(debt1)
        db_session.add(debt2)
        db_session.add(debt3)
        db_session.commit()
        
        result = prepare_all_debts_data()
        
        assert result['success'] is True
        assert len(result['debts']) == 3
        assert len(result['active_debts']) == 2  # Only non-zero debts
        assert result['total_debts'] == 3
        assert result['total_amount'] == 80.0  # 50 + 30

    def test_prepare_all_debts_data_empty(self, db_session):
        """Test debts data preparation with no debts"""
        result = prepare_all_debts_data()
        
        assert result['success'] is True
        assert len(result['debts']) == 0
        assert len(result['active_debts']) == 0
        assert result['total_debts'] == 0
        assert result['total_amount'] == 0.0

    @patch('app.model.debt.Debt.query')
    def test_prepare_all_debts_data_error(self, mock_query):
        """Test debts data preparation with database error"""
        mock_query.all.side_effect = Exception("Database error")
        
        result = prepare_all_debts_data()
        
        assert result['success'] is False
        assert "Error loading debts" in result['message']
        assert result['debts'] == []
        assert result['active_debts'] == []
        assert result['total_debts'] == 0
        assert result['total_amount'] == 0


class TestHandleExpenseFormValidation:
    """Test the handle_expense_form_validation function"""

    def test_handle_expense_form_validation_success(self):
        """Test successful form validation"""
        mock_form = MagicMock()
        mock_form.validate_on_submit.return_value = True
        
        result = handle_expense_form_validation(mock_form)
        
        assert result['valid'] is True
        assert result['form'] == mock_form

    def test_handle_expense_form_validation_failure(self):
        """Test form validation failure"""
        mock_form = MagicMock()
        mock_form.validate_on_submit.return_value = False
        mock_form.errors = {
            'amount': ['Amount is required'],
            'description': ['Description is required']
        }
        
        result = handle_expense_form_validation(mock_form)
        
        assert result['valid'] is False
        assert len(result['errors']) == 2
        assert 'amount: Amount is required' in result['errors']
        assert 'description: Description is required' in result['errors']
        assert result['message'] == 'Please correct the form errors.'
        assert result['message_type'] == 'warning'

    def test_handle_expense_form_validation_no_errors(self):
        """Test form validation failure with no errors"""
        mock_form = MagicMock()
        mock_form.validate_on_submit.return_value = False
        mock_form.errors = {}
        
        result = handle_expense_form_validation(mock_form)
        
        assert result['valid'] is False
        assert result['errors'] == []
        assert result['message'] == 'Please correct the form errors.'
        assert result['message_type'] == 'warning'