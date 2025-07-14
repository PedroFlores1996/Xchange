"""Tests for get_authorized_group function"""

import pytest
from app.group import get_authorized_group
from app.model.user import User
from app.model.group import Group


def test_get_authorized_group(request_context, logged_in_user):
    """Test getting an authorized group for current user"""
    group = Group.create("group_name", [logged_in_user])
    
    assert get_authorized_group(group.id) == group


def test_get_authorized_group_not_found(request_context, logged_in_user):
    """Test getting a group the current user is not a member of"""
    other_user = User.create("user2", "email2", "password")
    group = Group.create("group_name", [other_user])
    
    assert get_authorized_group(group.id) is None