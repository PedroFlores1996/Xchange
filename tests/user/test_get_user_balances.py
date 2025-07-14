"""Tests for get_user_balances function"""

import pytest
from flask_login import login_user, logout_user
from app.user import get_user_balances
from app.model.user import User
from app.model.group import Group
from app.model.debt import Debt
from app.model.constants import NO_GROUP
from decimal import Decimal


class TestGetUserBalances:
    """Tests for get_user_balances function"""

    def test_get_user_balances_with_debts(self, db_session, request_context):
        """Test getting user balances with various debts"""
        # Create users and groups
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password") 
        user3 = User.create("user3", "user3@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2])
        group2 = Group.create("group2", [user1, user3])
        
        # Log in user1 to set current_user
        login_user(user1)
        
        try:
            # Create debts where user1 is lender
            Debt.update(user2.id, user1.id, float(Decimal("50.00")), group1.id)
            Debt.update(user3.id, user1.id, float(Decimal("30.00")), group2.id)
            
            # Create debt where user1 is borrower
            Debt.update(user1.id, user2.id, float(Decimal("20.00")), group1.id)
            
            # Create no-group debt where user1 is lender
            Debt.update(user3.id, user1.id, float(Decimal("15.00")), NO_GROUP)
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # Check structure
            assert isinstance(group_balances, dict)
            assert isinstance(overall_balance, (int, float))
            
            # Check group balances
            assert group1.id in group_balances
            assert group2.id in group_balances
            assert NO_GROUP in group_balances
            
            # user1 lent 50 to user2 in group1, borrowed 20 from user2 in group1
            # Net in group1: 50 - 20 = 30
            assert group_balances[group1.id] == 30.0
            
            # user1 lent 30 to user3 in group2
            assert group_balances[group2.id] == 30.0
            
            # user1 lent 15 to user3 with no group
            assert group_balances[NO_GROUP] == 15.0
            
            # Overall balance: 50 - 20 + 30 + 15 = 75
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
            assert group_balances[NO_GROUP] == 0
            assert overall_balance == 0
            
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
            # Create debts where user1 is only lender
            Debt.update(user2.id, user1.id, float(Decimal("40.00")), group1.id)
            Debt.update(user3.id, user1.id, float(Decimal("25.00")), NO_GROUP)
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # user1 lent 40 in group1
            assert group_balances[group1.id] == 40.0
            
            # user1 lent 25 with no group
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
            # Create debts where user1 is only borrower
            Debt.update(user1.id, user2.id, float(Decimal("35.00")), group1.id)
            Debt.update(user1.id, user3.id, float(Decimal("20.00")), NO_GROUP)
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # user1 owes 35 in group1
            assert group_balances[group1.id] == -35.0
            
            # user1 owes 20 with no group
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
            # Create debts in different groups
            Debt.update(user2.id, user1.id, float(Decimal("100.00")), group1.id)  # user1 lends in group1
            Debt.update(user1.id, user3.id, float(Decimal("60.00")), group2.id)   # user1 borrows in group2
            Debt.update(user4.id, user1.id, float(Decimal("30.00")), group3.id)   # user1 lends in group3
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # Check individual group balances
            assert group_balances[group1.id] == 100.0   # positive (lender)
            assert group_balances[group2.id] == -60.0   # negative (borrower)  
            assert group_balances[group3.id] == 30.0    # positive (lender)
            assert group_balances[NO_GROUP] == 0        # no no-group debts
            
            # Overall balance: 100 - 60 + 30 = 70
            assert overall_balance == 70.0
            
        finally:
            logout_user()

    def test_get_user_balances_zero_group_balance(self, db_session, request_context):
        """Test getting balances when group balance nets to zero"""
        # Create users and group
        user1 = User.create("user1", "user1@test.com", "password")
        user2 = User.create("user2", "user2@test.com", "password")
        
        group1 = Group.create("group1", [user1, user2])
        
        # Log in user1
        login_user(user1)
        
        try:
            # Create equal debts in both directions
            Debt.update(user2.id, user1.id, float(Decimal("50.00")), group1.id)  # user1 lends 50
            Debt.update(user1.id, user2.id, float(Decimal("50.00")), group1.id)  # user1 borrows 50
            
            db_session.commit()
            
            group_balances, overall_balance = get_user_balances(user1)
            
            # Group balance should be zero (50 - 50 = 0)
            assert group_balances[group1.id] == 0.0
            
            # Overall balance should be zero
            assert overall_balance == 0.0
            
        finally:
            logout_user()