"""Tests for get_user_balances function"""

import pytest
from flask_login import login_user, logout_user
from app.user import get_user_balances
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt
from app.model.group_balance import GroupBalance
from app.model.constants import NO_GROUP
from decimal import Decimal


class TestGetUserBalances:
    """Tests for get_user_balances function"""

    def test_get_user_balances_with_debts(self, db_session, request_context):
        """Test getting user balances with various debts and group balances"""
        # Create users and groups
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password") 
        user3 = User.create("user3", "user3@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2])
        group2 = Group.create("group2", [user1, user3])
        
        # Log in user1 to set current_user
        login_user(user1)
        
        try:
            # Create group balances directly
            GroupBalance.update_balance(user1.id, group1.id, float(Decimal("30.00")))  # user1 is owed 30 in group1
            GroupBalance.update_balance(user1.id, group2.id, float(Decimal("30.00")))  # user1 is owed 30 in group2
            
            # Create individual debt where user1 is lender
            Debt.update(user3.id, user1.id, float(Decimal("15.00")))
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # Check structure
            assert isinstance(group_balances, dict)
            assert isinstance(overall_balance, (int, float))
            
            # Check group balances
            assert group1.id in group_balances
            assert group2.id in group_balances
            assert NO_GROUP in group_balances
            
            # user1 is owed 30 in group1
            assert group_balances[group1.id] == 30.0
            
            # user1 is owed 30 in group2
            assert group_balances[group2.id] == 30.0
            
            # user1 lent 15 to user3 individually (no group)
            assert group_balances[NO_GROUP] == 15.0
            
            # Overall balance: 30 + 30 + 15 = 75
            assert overall_balance == 75.0
            
        finally:
            logout_user()

    def test_get_user_balances_no_debts(self, db_session, request_context):
        """Test getting user balances with no debts"""
        # Create user and groups
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2])
        
        # Log in user1
        login_user(user1)
        
        try:
            group_balances, overall_balance = get_user_balances(user1)
            
            # Check structure
            assert isinstance(group_balances, dict)
            assert isinstance(overall_balance, (int, float))
            
            # All balances should be zero
            assert group_balances[group1.id] == 0.0
            assert group_balances[NO_GROUP] == 0.0
            assert overall_balance == 0.0
            
        finally:
            logout_user()

    def test_get_user_balances_only_lender(self, db_session, request_context):
        """Test getting balances when user is only a lender"""
        # Create users and group
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password")
        user3 = User.create("user3", "user3@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2, user3])
        
        # Log in user1
        login_user(user1)
        
        try:
            # Create group balance where user1 is owed money
            GroupBalance.update_balance(user1.id, group1.id, float(Decimal("40.00")))
            
            # Create individual debt where user1 is lender
            Debt.update(user3.id, user1.id, float(Decimal("25.00")))
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # user1 is owed 40 in group1
            assert group_balances[group1.id] == 40.0
            
            # user1 lent 25 individually (no group)
            assert group_balances[NO_GROUP] == 25.0
            
            # Overall positive balance
            assert overall_balance == 65.0
            
        finally:
            logout_user()

    def test_get_user_balances_only_borrower(self, db_session, request_context):
        """Test getting balances when user is only a borrower"""
        # Create users and group
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password")
        user3 = User.create("user3", "user3@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2, user3])
        
        # Log in user1
        login_user(user1)
        
        try:
            # Create group balance where user1 owes money
            GroupBalance.update_balance(user1.id, group1.id, float(Decimal("-35.00")))
            
            # Create individual debt where user1 is borrower
            Debt.update(user1.id, user3.id, float(Decimal("20.00")))
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # user1 owes 35 in group1
            assert group_balances[group1.id] == -35.0
            
            # user1 owes 20 individually (no group)
            assert group_balances[NO_GROUP] == -20.0
            
            # Overall negative balance
            assert overall_balance == -55.0
            
        finally:
            logout_user()

    def test_get_user_balances_multiple_groups(self, db_session, request_context):
        """Test getting balances across multiple groups"""
        # Create users and groups
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password")
        user3 = User.create("user3", "user3@test.com", "password")
        user4 = User.create("user4", "user4@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2])
        group2 = Group.create("group2", [user1, user3])
        group3 = Group.create("group3", [user1, user4])
        
        # Log in user1
        login_user(user1)
        
        try:
            # Create group balances across different groups
            GroupBalance.update_balance(user1.id, group1.id, float(Decimal("100.00")))  # user1 is owed in group1
            GroupBalance.update_balance(user1.id, group2.id, float(Decimal("-60.00")))  # user1 owes in group2
            GroupBalance.update_balance(user1.id, group3.id, float(Decimal("30.00")))   # user1 is owed in group3
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # Check individual group balances
            assert group_balances[group1.id] == 100.0   # positive (owed)
            assert group_balances[group2.id] == -60.0   # negative (owes)  
            assert group_balances[group3.id] == 30.0    # positive (owed)
            assert group_balances[NO_GROUP] == 0.0      # no individual debts
            
            # Overall balance: 100 - 60 + 30 = 70
            assert overall_balance == 70.0
            
        finally:
            logout_user()

    def test_get_user_balances_zero_group_balance(self, db_session, request_context):
        """Test getting balances when group balance is zero"""
        # Create users and group
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2])
        
        # Log in user1
        login_user(user1)
        
        try:
            # Create zero group balance (or no balance record, which defaults to 0)
            # No GroupBalance record created, so it will default to 0.0
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # Group balance should be zero (default)
            assert group_balances[group1.id] == 0.0
            
            # Overall balance should be zero
            assert overall_balance == 0.0
            
        finally:
            logout_user()