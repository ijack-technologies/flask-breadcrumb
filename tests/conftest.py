"""Pytest configuration for Flask-Breadcrumb tests."""

import pytest
from flask import Flask, request


@pytest.fixture
def base_app():
    """Create a basic Flask application for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'
    
    # Add a request context for testing
    @app.before_request
    def set_request_globals():
        if not hasattr(request, 'endpoint'):
            request.endpoint = None
    
    return app