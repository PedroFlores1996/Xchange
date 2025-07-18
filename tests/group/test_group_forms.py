"""
Minimal test coverage for GroupForm.validate_name method.

This module provides the minimum tests required to achieve 100% coverage
of the validate_name method in GroupForm.
"""

import pytest
from wtforms import ValidationError
from app.group.forms import GroupForm


class TestGroupFormValidateName:
    """Test cases for GroupForm.validate_name method."""

    def test_validate_name_valid_short_name(self, request_context):
        """Test that names within 72 characters are valid."""
        form = GroupForm()
        form.name.data = "Valid Group Name"
        
        # Should not raise any exception
        form.validate_name(form.name)

    def test_validate_name_valid_exactly_72_characters(self, request_context):
        """Test that exactly 72 characters is valid (boundary test)."""
        form = GroupForm()
        # Create a string with exactly 72 characters
        form.name.data = "A" * 72
        
        # Should not raise any exception
        form.validate_name(form.name)

    def test_validate_name_invalid_exceeds_72_characters(self, request_context):
        """Test that names exceeding 72 characters raise ValidationError."""
        form = GroupForm()
        # Create a string with 73 characters (one over the limit)
        form.name.data = "A" * 73
        
        with pytest.raises(ValidationError) as exc_info:
            form.validate_name(form.name)
        
        assert str(exc_info.value) == "Group name must not exceed 72 characters."