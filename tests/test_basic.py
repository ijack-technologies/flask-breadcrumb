"""Basic tests for Flask-Breadcrumb."""

import json

from flask_breadcrumb import Breadcrumb, get_breadcrumbs


def test_basic_breadcrumb(base_app):
    """Test basic breadcrumb functionality."""
    # Initialize Breadcrumb with the app
    breadcrumb = Breadcrumb(base_app)

    # Create a simple route with a breadcrumb
    @base_app.route("/categories")
    @breadcrumb("Categories")
    def index():
        return "Home"

    # Make a request to the route
    with base_app.test_request_context("/categories"):
        # Get the breadcrumbs
        breadcrumbs = get_breadcrumbs()
        breadcrumb_data = json.loads(breadcrumbs)

        # Verify the breadcrumb data
        assert breadcrumb_data["text"] == "Categories"
        assert breadcrumb_data["url"] == "/categories"
        assert breadcrumb_data["is_current_path"] is True
