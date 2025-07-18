"""Tests for settlement handler functions in app.group.__init__"""

import pytest
from app.group import (
    handle_settle_debts_process,
    handle_individual_balance_confirmation,
    handle_individual_balance_process,
)
from app.model.group_balance import GroupBalance
from app.model.user import User


class TestHandleSettleDebtsProcess:
    """Test the handle_settle_debts_process function"""

    def test_success_case_with_active_debts(self, debts_and_expenses, db_session):
        """Test successful debt settlement processing"""
        # Use the existing fixture which creates group balances
        _, _, _, _, _, _, _ = debts_and_expenses
        # Get the group from the users_and_group fixture
        user1, user2, user3, group = debts_and_expenses.__self__.users_and_group if hasattr(debts_and_expenses, '__self__') else (None, None, None, None)
        
        # Since we can't easily access the group from debts_and_expenses, let's create our own scenario
        from app.model.group import Group
        test_user1 = User.create("test1", "test1@example.com", "password")
        test_user2 = User.create("test2", "test2@example.com", "password") 
        test_user3 = User.create("test3", "test3@example.com", "password")
        test_group = Group.create("Test Group", [test_user1, test_user2, test_user3])
        
        # Create some balances
        GroupBalance.update_balance(test_user1.id, test_group.id, -30.0)
        GroupBalance.update_balance(test_user2.id, test_group.id, 20.0)
        GroupBalance.update_balance(test_user3.id, test_group.id, 10.0)
        db_session.commit()
        
        result = handle_settle_debts_process(test_group)
        
        assert result['success'] is True
        assert result['message_type'] == 'success'
        assert 'settlement transactions' in result['message']
        assert 'settlement_expenses' in result
        assert len(result['settlement_expenses']) > 0

    def test_no_debts_to_settle(self, users_and_group, db_session):
        """Test when there are no debts to settle"""
        user1, user2, user3, group = users_and_group
        
        result = handle_settle_debts_process(group)
        
        assert result['success'] is False
        assert result['message'] == "No Active Debts to Settle"
        assert result['message_type'] == 'info'


class TestHandleIndividualBalanceConfirmation:
    """Test the handle_individual_balance_confirmation function"""

    def test_success_case_with_user_debt(self, debts_and_expenses, db_session):
        """Test successful individual balance confirmation for user with debt"""
        # Create our own test scenario with known balances
        from app.model.group import Group
        test_user1 = User.create("debt1", "debt1@example.com", "password")
        test_user2 = User.create("debt2", "debt2@example.com", "password") 
        test_user3 = User.create("debt3", "debt3@example.com", "password")
        test_group = Group.create("Debt Test Group", [test_user1, test_user2, test_user3])
        
        # Set up balances: user1 owes, user2 is owed
        GroupBalance.update_balance(test_user1.id, test_group.id, -30.0)
        GroupBalance.update_balance(test_user2.id, test_group.id, 30.0)
        db_session.commit()
        
        result = handle_individual_balance_confirmation(test_group, test_user1.id)
        
        assert result['success'] is True
        assert result['user'] == test_user1
        assert result['user_balance'] == -30.0
        assert len(result['settlement_transactions']) > 0

    def test_success_case_with_user_credit(self, debts_and_expenses, db_session):
        """Test successful individual balance confirmation for user who is owed money"""
        # Create test scenario
        from app.model.group import Group
        test_user1 = User.create("credit1", "credit1@example.com", "password")
        test_user2 = User.create("credit2", "credit2@example.com", "password") 
        test_user3 = User.create("credit3", "credit3@example.com", "password")
        test_group = Group.create("Credit Test Group", [test_user1, test_user2, test_user3])
        
        # Set up balances: user2 is owed, user1 owes
        GroupBalance.update_balance(test_user1.id, test_group.id, -20.0)
        GroupBalance.update_balance(test_user2.id, test_group.id, 20.0)
        db_session.commit()
        
        result = handle_individual_balance_confirmation(test_group, test_user2.id)
        
        assert result['success'] is True
        assert result['user'] == test_user2
        assert result['user_balance'] == 20.0
        assert len(result['settlement_transactions']) > 0

    def test_user_not_in_group(self, users_and_group, db_session):
        """Test when user is not in the group"""
        user1, user2, user3, group = users_and_group
        
        # Create a user not in the group
        outside_user = User.create("outsider", "outsider@test.com", "password")
        db_session.commit()
        
        result = handle_individual_balance_confirmation(group, outside_user.id)
        
        assert result['success'] is False
        assert result['message'] == "User not found or not in group."
        assert result['message_type'] == 'danger'

    def test_user_with_zero_balance(self, users_and_group, db_session):
        """Test when user has zero balance"""
        user1, user2, user3, group = users_and_group
        
        result = handle_individual_balance_confirmation(group, user1.id)
        
        assert result['success'] is False
        assert result['message'] == "No balance to settle for this user."
        assert result['message_type'] == 'info'


class TestHandleIndividualBalanceProcess:
    """Test the handle_individual_balance_process function"""

    def test_success_case_with_user_debt(self, debts_and_expenses, db_session):
        """Test successful individual balance processing for user with debt"""
        # Create test scenario
        from app.model.group import Group
        test_user1 = User.create("process1", "process1@example.com", "password")
        test_user2 = User.create("process2", "process2@example.com", "password") 
        test_user3 = User.create("process3", "process3@example.com", "password")
        test_group = Group.create("Process Test Group", [test_user1, test_user2, test_user3])
        
        # Set up balances: user1 owes, user2 is owed
        GroupBalance.update_balance(test_user1.id, test_group.id, -30.0)
        GroupBalance.update_balance(test_user2.id, test_group.id, 30.0)
        db_session.commit()
        
        result = handle_individual_balance_process(test_group, test_user1.id)
        
        assert result['success'] is True
        assert result['user'] == test_user1
        assert len(result['settlement_expenses']) > 0

    def test_user_not_in_group(self, users_and_group, db_session):
        """Test when user is not in the group"""
        user1, user2, user3, group = users_and_group
        
        # Create a user not in the group
        outside_user = User.create("outsider2", "outsider2@test.com", "password")
        db_session.commit()
        
        result = handle_individual_balance_process(group, outside_user.id)
        
        assert result['success'] is False
        assert result['message'] == "User not found or not in group."
        assert result['message_type'] == 'danger'

    def test_user_with_zero_balance(self, users_and_group, db_session):
        """Test when user has zero balance"""
        user1, user2, user3, group = users_and_group
        
        result = handle_individual_balance_process(group, user1.id)
        
        assert result['success'] is False
        assert result['message'] == "No balance to settle for this user."
        assert result['message_type'] == 'info'

    def test_settlement_creates_expenses(self, debts_and_expenses, db_session):
        """Test that settlement actually creates expense records"""
        # Create test scenario
        from app.model.group import Group
        from app.model.expense import Expense
        test_user1 = User.create("expense1", "expense1@example.com", "password")
        test_user2 = User.create("expense2", "expense2@example.com", "password") 
        test_user3 = User.create("expense3", "expense3@example.com", "password")
        test_group = Group.create("Expense Test Group", [test_user1, test_user2, test_user3])
        
        # Set up balances: user1 owes, user2 is owed
        GroupBalance.update_balance(test_user1.id, test_group.id, -30.0)
        GroupBalance.update_balance(test_user2.id, test_group.id, 30.0)
        db_session.commit()
        
        # Count existing expenses before settlement
        initial_expense_count = Expense.query.count()
        
        result = handle_individual_balance_process(test_group, test_user1.id)
        
        assert result['success'] is True
        
        # Check that new expenses were created
        final_expense_count = Expense.query.count()
        assert final_expense_count > initial_expense_count
        
        # Check that settlement expenses have correct category
        settlement_expenses = result['settlement_expenses']
        for expense in settlement_expenses:
            assert expense.category.name == 'SETTLEMENT'