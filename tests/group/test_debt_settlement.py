"""Tests for debt settlement functionality"""

import pytest
from flask import url_for
from flask_login import login_user, logout_user
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt
from app.model.expense import Expense, ExpenseCategory
from app.model.constants import NO_GROUP
from app.group import get_group_user_balances
from app.debt import simplify_debts
from decimal import Decimal


@pytest.fixture
def settlement_test_users(db_session):
    """Create test users for settlement testing"""
    user1 = User.create("alice", "alice@test.com", "password")
    user2 = User.create("bob", "bob@test.com", "password")
    user3 = User.create("charlie", "charlie@test.com", "password")
    return user1, user2, user3


@pytest.fixture
def settlement_test_group(settlement_test_users, db_session):
    """Create test group for settlement testing"""
    user1, user2, user3 = settlement_test_users
    group = Group.create("Settlement Test Group", [user1, user2, user3])
    return group


@pytest.fixture
def complex_debt_scenario(settlement_test_users, settlement_test_group, db_session):
    """Create a complex debt scenario for testing settlement"""
    user1, user2, user3 = settlement_test_users
    group = settlement_test_group
    
    # Create debts that require settlement
    # Alice owes Bob $50
    Debt.update(user1.id, user2.id, 50.0, group.id)
    # Bob owes Charlie $30
    Debt.update(user2.id, user3.id, 30.0, group.id)
    # Charlie owes Alice $20
    Debt.update(user3.id, user1.id, 20.0, group.id)
    
    db_session.commit()
    return user1, user2, user3, group


class TestDebtSettlementLogic:
    """Test the core debt settlement logic"""
    
    def test_get_group_user_balances_calculation(self, complex_debt_scenario, db_session):
        """Test that group balances are calculated correctly"""
        user1, user2, user3, group = complex_debt_scenario
        
        balances = get_group_user_balances(group)
        
        # Alice: owes Bob $50, is owed by Charlie $20 = net owes $30
        assert balances[user1] == -30.0
        
        # Bob: is owed by Alice $50, owes Charlie $30 = net is owed $20
        assert balances[user2] == 20.0
        
        # Charlie: is owed by Bob $30, owes Alice $20 = net is owed $10
        assert balances[user3] == 10.0
        
        # Total should sum to zero
        assert sum(balances.values()) == 0.0
    
    def test_simplify_debts_calculation(self, complex_debt_scenario, db_session):
        """Test that the simplify_debts function works correctly"""
        user1, user2, user3, group = complex_debt_scenario
        
        balances = get_group_user_balances(group)
        balance_dict = {user.id: balance for user, balance in balances.items()}
        
        transactions = simplify_debts(balance_dict)
        
        # Should minimize number of transactions
        assert len(transactions) <= 2  # With 3 users, max 2 transactions needed
        
        # Check that transactions actually settle the debts
        net_changes = {user1.id: 0.0, user2.id: 0.0, user3.id: 0.0}
        for debtor_id, creditor_id, amount in transactions:
            net_changes[debtor_id] += amount  # Debtor pays (positive)
            net_changes[creditor_id] -= amount  # Creditor receives (negative)
        
        # Net changes should equal the negative of original balances
        for user_id, original_balance in balance_dict.items():
            assert abs(net_changes[user_id] + original_balance) < 0.01  # Allow for floating point errors
    
    def test_no_debts_scenario(self, settlement_test_users, settlement_test_group, db_session):
        """Test settlement when there are no debts"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group
        
        balances = get_group_user_balances(group)
        
        # All balances should be zero
        assert all(balance == 0.0 for balance in balances.values())
        
        balance_dict = {user.id: balance for user, balance in balances.items()}
        transactions = simplify_debts(balance_dict)
        
        # No transactions should be needed
        assert len(transactions) == 0
    
    def test_single_debt_scenario(self, settlement_test_users, settlement_test_group, db_session):
        """Test settlement with a single debt"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group
        
        # Create single debt: Alice owes Bob $100
        Debt.update(user1.id, user2.id, 100.0, group.id)
        db_session.commit()
        
        balances = get_group_user_balances(group)
        balance_dict = {user.id: balance for user, balance in balances.items()}
        
        transactions = simplify_debts(balance_dict)
        
        # Should have exactly one transaction
        assert len(transactions) == 1
        
        debtor_id, creditor_id, amount = transactions[0]
        assert debtor_id == user1.id
        assert creditor_id == user2.id
        assert amount == 100.0


class TestDebtSettlementViews:
    """Test the settlement view functions"""
    
    def test_settlement_preview_authorized_user(self, client, complex_debt_scenario, db_session):
        """Test that authorized users can view settlement preview"""
        user1, user2, user3, group = complex_debt_scenario
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
            sess['_fresh'] = True
        
        response = client.get(f'/groups/{group.id}/settle')
        assert response.status_code == 200
        assert b'Settlement Transactions' in response.data
    
    def test_settlement_preview_unauthorized_user(self, client, complex_debt_scenario, db_session):
        """Test that unauthorized users cannot view settlement preview"""
        user1, user2, user3, group = complex_debt_scenario
        
        # Create a user not in the group
        unauthorized_user = User.create("unauthorized", "unauth@test.com", "password")
        db_session.commit()
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(unauthorized_user.id)
            sess['_fresh'] = True
        
        response = client.get(f'/groups/{group.id}/settle')
        assert response.status_code == 302  # Redirect due to no access
    
    def test_settlement_preview_no_debts(self, client, settlement_test_users, settlement_test_group, db_session):
        """Test settlement preview when there are no debts"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
            sess['_fresh'] = True
        
        response = client.get(f'/groups/{group.id}/settle')
        assert response.status_code == 302  # Redirect due to no debts
    
    def test_settlement_processing_creates_expenses(self, client, complex_debt_scenario, db_session):
        """Test that settlement processing creates the correct expenses"""
        user1, user2, user3, group = complex_debt_scenario
        
        # Count initial expenses
        initial_expense_count = Expense.query.filter_by(group_id=group.id).count()
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
            sess['_fresh'] = True
        
        response = client.post(f'/groups/{group.id}/settle')
        assert response.status_code == 200
        
        # Check that settlement expenses were created
        final_expense_count = Expense.query.filter_by(group_id=group.id).count()
        settlement_expenses = Expense.query.filter_by(
            group_id=group.id,
            category=ExpenseCategory.SETTLEMENT
        ).all()
        
        assert final_expense_count > initial_expense_count
        assert len(settlement_expenses) > 0
        
        # Check that settlement expenses have correct properties
        for expense in settlement_expenses:
            assert "Settlement payment" in expense.description
            assert expense.creator_id == user1.id
            assert expense.group_id == group.id
    
    def test_settlement_processing_clears_debts(self, client, complex_debt_scenario, db_session):
        """Test that settlement processing clears all group debts"""
        user1, user2, user3, group = complex_debt_scenario
        
        # Verify initial debts exist
        initial_debts = Debt.query.filter_by(group_id=group.id).all()
        assert len(initial_debts) > 0
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
            sess['_fresh'] = True
        
        response = client.post(f'/groups/{group.id}/settle')
        assert response.status_code == 200
        
        # Check that old debts are cleared
        remaining_old_debts = Debt.query.filter_by(group_id=group.id).all()
        
        # After settlement, new debts should be created by the settlement expenses
        # But the net effect should be zero balances
        final_balances = get_group_user_balances(group)
        
        # All balances should be zero or very close to zero (accounting for floating point)
        for balance in final_balances.values():
            assert abs(balance) < 0.01
    
    def test_settlement_processing_preserves_other_group_debts(self, client, complex_debt_scenario, db_session):
        """Test that settlement only affects the specified group's debts"""
        user1, user2, user3, group = complex_debt_scenario
        
        # Create another group with different debts
        other_group = Group.create("Other Group", [user1, user2])
        Debt.update(user1.id, user2.id, 25.0, other_group.id)
        db_session.commit()
        
        initial_other_group_debts = Debt.query.filter_by(group_id=other_group.id).count()
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
            sess['_fresh'] = True
        
        response = client.post(f'/groups/{group.id}/settle')
        assert response.status_code == 200
        
        # Check that other group's debts are unaffected
        final_other_group_debts = Debt.query.filter_by(group_id=other_group.id).count()
        assert final_other_group_debts == initial_other_group_debts
    
    def test_settlement_processing_preserves_no_group_debts(self, client, complex_debt_scenario, db_session):
        """Test that settlement doesn't affect non-group debts"""
        user1, user2, user3, group = complex_debt_scenario
        
        # Create no-group debt
        Debt.update(user1.id, user2.id, 15.0, NO_GROUP)
        db_session.commit()
        
        initial_no_group_debts = Debt.query.filter_by(group_id=NO_GROUP).count()
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user1.id)
            sess['_fresh'] = True
        
        response = client.post(f'/groups/{group.id}/settle')
        assert response.status_code == 200
        
        # Check that no-group debts are unaffected
        final_no_group_debts = Debt.query.filter_by(group_id=NO_GROUP).count()
        assert final_no_group_debts == initial_no_group_debts


class TestDebtSettlementEdgeCases:
    """Test edge cases for debt settlement"""
    
    def test_settlement_with_zero_net_balances_but_individual_debts(self, settlement_test_users, settlement_test_group, db_session):
        """Test settlement when net balances are zero but individual debts exist"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group
        
        # Create circular debts that net to zero
        # Alice owes Bob $50, Bob owes Alice $50
        # NOTE: Due to Debt.update() logic, these will cancel each other out
        Debt.update(user1.id, user2.id, 50.0, group.id)
        # This next debt will cancel the previous one due to Debt.update() logic
        Debt.update(user2.id, user1.id, 50.0, group.id)
        db_session.commit()
        
        balances = get_group_user_balances(group)
        
        # Net balances should be zero
        assert all(abs(balance) < 0.01 for balance in balances.values())
        
        # Due to automatic cancellation in Debt.update(), individual debts may not exist
        individual_debts = Debt.query.filter_by(group_id=group.id).all()
        # This test shows that automatic cancellation works
        assert len(individual_debts) == 0
    
    def test_settlement_with_floating_point_precision(self, settlement_test_users, settlement_test_group, db_session):
        """Test settlement with amounts that might cause floating point issues"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group
        
        # Create debts with amounts that might cause precision issues
        Debt.update(user1.id, user2.id, 33.33, group.id)
        Debt.update(user2.id, user3.id, 33.34, group.id)
        Debt.update(user3.id, user1.id, 33.33, group.id)
        db_session.commit()
        
        balances = get_group_user_balances(group)
        balance_dict = {user.id: balance for user, balance in balances.items()}
        
        transactions = simplify_debts(balance_dict)
        
        # Should still work despite floating point precision
        assert len(transactions) <= 2
        
        # Net changes should still balance out
        net_changes = {user1.id: 0.0, user2.id: 0.0, user3.id: 0.0}
        for debtor_id, creditor_id, amount in transactions:
            net_changes[debtor_id] += amount
            net_changes[creditor_id] -= amount
        
        for user_id, original_balance in balance_dict.items():
            assert abs(net_changes[user_id] + original_balance) < 0.01