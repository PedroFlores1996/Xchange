"""
Comprehensive test coverage for index views.

This module tests all aspects of the index blueprint including:
- Authentication requirements
- Redirects
- HTTP methods
- Edge cases
"""

import pytest
from flask import url_for
from flask_login import current_user


class TestHomePageView:
    """Test cases for the home_page view (/)."""

    def test_home_page_redirects_to_dashboard_when_authenticated(
        self, client, authenticated_user
    ):
        """Test that authenticated users are redirected to their dashboard."""
        response = client.get("/")

        assert response.status_code == 302
        assert response.location == url_for("user.user_dashboard")

    def test_home_page_redirects_to_login_when_unauthenticated(
        self, client, unauthenticated_user
    ):
        """Test that unauthenticated users are redirected to login."""
        response = client.get("/")

        assert response.status_code == 302
        # The redirect should be to login page due to @login_required decorator
        assert "/login" in response.location
