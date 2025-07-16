"""Tests for debt settlement functionality"""

import pytest
from flask import url_for
from flask_login import login_user, logout_user
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt
from app.model.group_balance import GroupBalance
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

    # Create group balances that require settlement
    # Alice owes Bob $50, is owed by Charlie $20 = net owes $30
    GroupBalance.update_balance(user1.id, group.id, -30.0)
    # Bob is owed by Alice $50, owes Charlie $30 = net is owed $20
    GroupBalance.update_balance(user2.id, group.id, 20.0)
    # Charlie is owed by Bob $30, owes Alice $20 = net is owed $10
    GroupBalance.update_balance(user3.id, group.id, 10.0)

    db_session.commit()
    return user1, user2, user3, group


class TestDebtSettlementLogic:
    """Test the core debt settlement logic"""

    def test_get_group_user_balances_calculation(
        self, complex_debt_scenario, db_session
    ):
        """Test that group balances are calculated correctly"""
        user1, user2, user3, group = complex_debt_scenario

        balances = get_group_user_balances(group)

        # Check that all users are in the result
        assert user1 in balances
        assert user2 in balances
        assert user3 in balances

        # Alice: net owes $30
        assert balances[user1] == -30.0

        # Bob: net is owed $20
        assert balances[user2] == 20.0

        # Charlie: net is owed $10
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
            assert (
                abs(net_changes[user_id] + original_balance) < 0.01
            )  # Allow for floating point errors

    def test_no_debts_scenario(
        self, settlement_test_users, settlement_test_group, db_session
    ):
        """Test settlement when there are no debts"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group

        balances = get_group_user_balances(group)

        # Should have all users with zero balances
        assert len(balances) == 3
        assert all(balance == 0.0 for balance in balances.values())

        balance_dict = {user.id: balance for user, balance in balances.items()}
        transactions = simplify_debts(balance_dict)

        # No transactions should be needed
        assert len(transactions) == 0

    def test_single_debt_scenario(
        self, settlement_test_users, settlement_test_group, db_session
    ):
        """Test settlement with a single debt"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group

        # Create single balance: Alice owes Bob $100
        GroupBalance.update_balance(user1.id, group.id, -100.0)
        GroupBalance.update_balance(user2.id, group.id, 100.0)
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


class TestDebtSettlementEdgeCases:
    """Test edge cases for debt settlement"""

    def test_settlement_with_zero_net_balances_but_individual_debts(
        self, settlement_test_users, settlement_test_group, db_session
    ):
        """Test settlement when net balances are zero but individual debts exist"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group

        # Create group balances that net to zero
        # Alice and Bob have equal and opposite balances
        GroupBalance.update_balance(user1.id, group.id, 50.0)
        GroupBalance.update_balance(user2.id, group.id, -50.0)
        # Then cancel them out
        GroupBalance.update_balance(user1.id, group.id, -50.0)
        GroupBalance.update_balance(user2.id, group.id, 50.0)
        db_session.commit()

        balances = get_group_user_balances(group)

        # Net balances should be zero
        assert all(abs(balance) < 0.01 for balance in balances.values())

        # Group balances should be zero after cancellation
        group_balances = GroupBalance.query.filter_by(group_id=group.id).all()
        for balance in group_balances:
            assert abs(balance.balance) < 0.01

    def test_settlement_with_floating_point_precision(
        self, settlement_test_users, settlement_test_group, db_session
    ):
        """Test settlement with amounts that might cause floating point issues"""
        user1, user2, user3 = settlement_test_users
        group = settlement_test_group

        # Create group balances with amounts that might cause precision issues
        # Alice net: owes 33.33 to Bob, is owed 33.33 by Charlie = 0
        GroupBalance.update_balance(user1.id, group.id, 0.0)
        # Bob net: is owed 33.33 by Alice, owes 33.34 to Charlie = -0.01
        GroupBalance.update_balance(user2.id, group.id, -0.01)
        # Charlie net: is owed 33.34 by Bob, owes 33.33 to Alice = 0.01
        GroupBalance.update_balance(user3.id, group.id, 0.01)
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
