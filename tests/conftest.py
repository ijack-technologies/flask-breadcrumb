"""Pytest configuration for Flask-Breadcrumb tests."""

import pytest
from flask import Flask


@pytest.fixture
def base_app():
    """Create a basic Flask application for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    return app
