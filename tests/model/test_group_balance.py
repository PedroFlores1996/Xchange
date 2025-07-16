import pytest
from app.model.user import User
from app.model.group import Group
from app.model.group_balance import GroupBalance


def test_create_group_balance(db_session):
    """Test creating a group balance using set_balance."""
    user = User.create("user1", "email1", "password")
    group = Group.create("group1", [user])
    
    GroupBalance.set_balance(user.id, group.id, 100.0)
    db_session.flush()  # Use db_session to avoid warning
    
    assert GroupBalance.query.count() == 1
    balance = GroupBalance.find(user.id, group.id)
    assert balance.user == user
    assert balance.group == group
    assert balance.balance == 100.0


def test_find_group_balance(db_session):
    """Test finding a group balance."""
    user = User.create("user1", "email1", "password")
    group = Group.create("group1", [user])
    
    GroupBalance.set_balance(user.id, group.id, 100.0)
    db_session.flush()  # Use db_session to avoid warning
    
    found_balance = GroupBalance.find(user.id, group.id)
    assert found_balance is not None
    assert found_balance.balance == 100.0
    assert found_balance.user == user
    assert found_balance.group == group


def test_find_or_create_existing(db_session):
    """Test find_or_create with existing balance."""
    user = User.create("user1", "email1", "password")
    group = Group.create("group1", [user])
    
    # Create balance using set_balance
    GroupBalance.set_balance(user.id, group.id, 100.0)
    original_balance = GroupBalance.find(user.id, group.id)
    
    # find_or_create should return the existing balance
    found_balance = GroupBalance.find_or_create(user.id, group.id)
    db_session.flush()  # Use db_session to avoid warning
    assert found_balance == original_balance
    assert found_balance.balance == 100.0
    assert GroupBalance.query.count() == 1


def test_find_or_create_new(db_session):
    """Test find_or_create with non-existing balance."""
    user = User.create("user1", "email1", "password")
    group = Group.create("group1", [user])
    
    balance = GroupBalance.find_or_create(user.id, group.id)
    db_session.flush()  # Use db_session to avoid warning
    
    assert balance.user == user
    assert balance.group == group
    assert balance.balance == 0.0
    assert GroupBalance.query.count() == 1


def test_update_balance(db_session):
    """Test updating a group balance."""
    user = User.create("user1", "email1", "password")
    group = Group.create("group1", [user])
    
    # Create initial balance
    GroupBalance.update_balance(user.id, group.id, 100.0)
    db_session.flush()  # Use db_session to avoid warning
    
    balance = GroupBalance.find(user.id, group.id)
    assert balance.balance == 100.0
    
    # Update balance
    GroupBalance.update_balance(user.id, group.id, 50.0)
    
    balance = GroupBalance.find(user.id, group.id)
    assert balance.balance == 150.0
    assert GroupBalance.query.count() == 1


def test_set_balance(db_session):
    """Test setting a group balance."""
    user = User.create("user1", "email1", "password")
    group = Group.create("group1", [user])
    
    # Create initial balance
    GroupBalance.update_balance(user.id, group.id, 100.0)
    
    balance = GroupBalance.find(user.id, group.id)
    assert balance.balance == 100.0
    
    # Set balance to new value
    GroupBalance.set_balance(user.id, group.id, 75.0)
    db_session.flush()  # Use db_session to avoid warning
    
    balance = GroupBalance.find(user.id, group.id)
    assert balance.balance == 75.0
    assert GroupBalance.query.count() == 1


def test_clear_group_balances(db_session):
    """Test clearing all balances for a group."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")
    group = Group.create("group1", [user1, user2])
    
    # Create initial balances
    GroupBalance.update_balance(user1.id, group.id, 100.0)
    GroupBalance.update_balance(user2.id, group.id, -100.0)
    
    assert GroupBalance.query.count() == 2
    
    # Clear all balances for the group
    GroupBalance.clear_group_balances(group.id)
    db_session.flush()  # Use db_session to avoid warning
    
    balance1 = GroupBalance.find(user1.id, group.id)
    balance2 = GroupBalance.find(user2.id, group.id)
    assert balance1 is None
    assert balance2 is None
    assert GroupBalance.query.count() == 0


def test_multiple_users_same_group(db_session):
    """Test multiple users in the same group."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")
    group = Group.create("group1", [user1, user2])
    
    GroupBalance.update_balance(user1.id, group.id, 100.0)
    GroupBalance.update_balance(user2.id, group.id, -100.0)
    db_session.flush()  # Use db_session to avoid warning
    
    balance1 = GroupBalance.find(user1.id, group.id)
    balance2 = GroupBalance.find(user2.id, group.id)
    
    assert balance1.balance == 100.0
    assert balance2.balance == -100.0
    assert GroupBalance.query.count() == 2


def test_same_user_multiple_groups(db_session):
    """Test same user in multiple groups."""
    user = User.create("user1", "email1", "password")
    group1 = Group.create("group1", [user])
    group2 = Group.create("group2", [user])
    
    GroupBalance.update_balance(user.id, group1.id, 100.0)
    GroupBalance.update_balance(user.id, group2.id, -50.0)
    db_session.flush()  # Use db_session to avoid warning
    
    balance1 = GroupBalance.find(user.id, group1.id)
    balance2 = GroupBalance.find(user.id, group2.id)
    
    assert balance1.balance == 100.0
    assert balance2.balance == -50.0
    assert GroupBalance.query.count() == 2


def test_get_group_balances(db_session):
    """Test getting all balances for a group."""
    user1 = User.create("user1", "email1", "password")
    user2 = User.create("user2", "email2", "password")
    group = Group.create("group1", [user1, user2])
    
    GroupBalance.update_balance(user1.id, group.id, 100.0)
    GroupBalance.update_balance(user2.id, group.id, -50.0)
    db_session.flush()  # Use db_session to avoid warning
    
    balances = GroupBalance.get_group_balances(group.id)
    
    assert len(balances) == 2
    assert balances[user1.id] == 100.0
    assert balances[user2.id] == -50.0


def test_unique_constraint(db_session):
    """Test unique constraint on user_id and group_id."""
    from sqlalchemy.exc import IntegrityError
    
    user = User.create("user1", "email1", "password")
    group = Group.create("group1", [user])
    
    GroupBalance.set_balance(user.id, group.id, 100.0)
    
    with pytest.raises(IntegrityError):
        # Try to manually create a duplicate record
        duplicate = GroupBalance(user_id=user.id, group_id=group.id, balance=50.0)
        db_session.add(duplicate)
        db_session.commit()