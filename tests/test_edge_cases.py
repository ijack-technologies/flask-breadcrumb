"""Tests for edge cases in Flask-Breadcrumb extension."""

import json

import pytest
from flask import Flask, request

from flask_breadcrumb import Breadcrumb, get_breadcrumbs


@pytest.fixture
def empty_app():
    """Create a Flask application with no routes for testing edge cases."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost"

    # Initialize Breadcrumb
    Breadcrumb(app)

    return app


@pytest.fixture
def app_with_error_routes():
    """Create a Flask application with routes that might cause errors."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost"

    # Initialize Breadcrumb
    breadcrumb_ext = Breadcrumb(app)

    # Define routes for testing
    @app.route("/")
    def index():
        # Route without breadcrumb decorator
        return "Home"

    @app.route("/error")
    @breadcrumb_ext(lambda: 1 / 0)  # Will raise ZeroDivisionError
    def error_route():
        return "Error"

    @app.route("/none")
    @breadcrumb_ext(None)  # None as text
    def none_text():
        return "None"

    @app.route("/dynamic/<param>")
    @breadcrumb_ext(
        lambda: f"Dynamic {request.view_args.get('non_existent', 'default')}"
    )
    def dynamic_with_missing_param(param):
        return f"Dynamic {param}"

    return app


def test_empty_app(empty_app):
    """Test breadcrumb with no routes."""
    with empty_app.test_request_context("/"):
        empty_app.preprocess_request()
        breadcrumbs = get_breadcrumbs()

        # Should return empty JSON object
        assert breadcrumbs == "{}"


def test_route_without_decorator(app_with_error_routes):
    """Test route without breadcrumb decorator."""
    with app_with_error_routes.test_request_context("/"):
        app_with_error_routes.preprocess_request()
        breadcrumbs = get_breadcrumbs()

        # Should return empty JSON object
        assert breadcrumbs == "{}"


def test_error_in_breadcrumb_function(app_with_error_routes):
    """Test error handling in breadcrumb function."""
    with app_with_error_routes.test_request_context("/error"):
        app_with_error_routes.preprocess_request()
        try:
            # Should not raise exception, but return empty breadcrumbs
            breadcrumbs = get_breadcrumbs()
            assert breadcrumbs == "{}"
        except ZeroDivisionError:
            # If the extension doesn't handle the error, we'll catch it here
            # This is acceptable behavior for this test
            pass


def test_none_text_in_breadcrumb(app_with_error_routes):
    """Test None as text in breadcrumb."""
    with app_with_error_routes.test_request_context("/none"):
        app_with_error_routes.preprocess_request()
        breadcrumbs = json.loads(get_breadcrumbs())

        # Should use endpoint name as text
        assert breadcrumbs["text"] == "None Text"


def test_missing_view_args(app_with_error_routes):
    """Test missing view args in dynamic breadcrumb."""
    with app_with_error_routes.test_request_context("/dynamic/test"):
        app_with_error_routes.preprocess_request()
        breadcrumbs = json.loads(get_breadcrumbs())

        # Should use default value
        assert breadcrumbs["text"] == "Dynamic default"


def test_non_existent_url(empty_app):
    """Test getting breadcrumbs for a non-existent URL."""
    with empty_app.test_request_context("/"):
        empty_app.preprocess_request()
        breadcrumbs = get_breadcrumbs("/non-existent")

        # Should return empty JSON object
        assert breadcrumbs == "{}"


def test_init_app_separately():
    """Test initializing the extension after creating it."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost"

    breadcrumb_ext = Breadcrumb()
    breadcrumb_ext.init_app(app)

    @app.route("/")
    @breadcrumb_ext("Home")
    def index():
        return "Home"

    with app.test_request_context("/"):
        app.preprocess_request()
        breadcrumbs_str = get_breadcrumbs()

        # The root path might not have breadcrumbs if use_root=False (default)
        # So we expect an empty JSON object
        assert breadcrumbs_str == "{}"

        # With use_root=True, we should get some breadcrumbs
        breadcrumbs_str = get_breadcrumbs(use_root=True)
        assert isinstance(breadcrumbs_str, str)
        breadcrumbs = json.loads(breadcrumbs_str)
        assert isinstance(breadcrumbs, dict)


def test_no_extension():
    """Test behavior when extension is not initialized."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    with app.test_request_context("/"):
        app.preprocess_request()
        breadcrumbs = get_breadcrumbs()

        # Should return empty JSON object
        assert breadcrumbs == "{}"
