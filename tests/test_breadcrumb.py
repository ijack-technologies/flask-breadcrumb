"""Tests for Flask-Breadcrumb extension."""

import pytest
from flask import Flask, render_template_string, request

from flask_breadcrumb import Breadcrumb


@pytest.fixture
def app():
    """Create a Flask application for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'
    
    # Create a simple template for testing
    @app.route('/template')
    def test_template():
        return render_template_string("""
        {% set crumbs = breadcrumb_tree() %}
        <ul class="breadcrumb">
            <li>
                <a href="{{ crumbs.url }}">{{ crumbs.text }}</a>
                {% if crumbs.children %}
                <ul>
                    {% for child in crumbs.children %}
                    <li>
                        <a href="{{ child.url }}">{{ child.text }}</a>
                    </li>
                    {% endfor %}
                </ul>
                {% endif %}
            </li>
        </ul>
        """)
    
    return app


@pytest.fixture
def breadcrumb_extension(app):
    """Create a Breadcrumb extension instance."""
    return Breadcrumb(app)


def test_breadcrumb_init(app):
    """Test initializing the Breadcrumb extension."""
    breadcrumb = Breadcrumb()
    assert breadcrumb.app is None
    
    breadcrumb.init_app(app)
    assert app.extensions['breadcrumb'] == breadcrumb


def test_breadcrumb_decorator(app, breadcrumb_extension):
    """Test the breadcrumb decorator."""
    @app.route('/')
    @breadcrumb_extension('Home', order=0)
    def index():
        return 'Home'
    
    @app.route('/path1')
    @breadcrumb_extension('Path 1', order=0)
    def path1():
        return 'Path 1'
    
    @app.route('/path1/shared')
    @breadcrumb_extension('Shared', order=0)
    def shared1():
        return 'Shared 1'
    
    @app.route('/path1/shared/item')
    @breadcrumb_extension('Item', order=0)
    def item1():
        return 'Item 1'
    
    @app.route('/path2')
    @breadcrumb_extension('Path 2', order=1)
    def path2():
        return 'Path 2'
    
    # Test that breadcrumbs are registered
    with app.test_request_context('/'):
        app.preprocess_request()
        assert '/' in app.config['BREADCRUMB_ITEMS']
        assert app.config['BREADCRUMB_ITEMS']['/'].text == 'Home'
    
    with app.test_request_context('/path1'):
        app.preprocess_request()
        assert '/path1' in app.config['BREADCRUMB_ITEMS']
        assert app.config['BREADCRUMB_ITEMS']['/path1'].text == 'Path 1'
        assert app.config['BREADCRUMB_ITEMS']['/path1'].parent_url == '/'
    
    with app.test_request_context('/path1/shared'):
        app.preprocess_request()
        assert '/path1/shared' in app.config['BREADCRUMB_ITEMS']
        assert app.config['BREADCRUMB_ITEMS']['/path1/shared'].text == 'Shared'
        assert app.config['BREADCRUMB_ITEMS']['/path1/shared'].parent_url == '/path1'


def test_breadcrumb_tree(app, breadcrumb_extension):
    """Test the breadcrumb_tree function."""
    @app.route('/')
    @breadcrumb_extension('Home', order=0)
    def index():
        return 'Home'
    
    @app.route('/path1')
    @breadcrumb_extension('Path 1', order=0)
    def path1():
        return 'Path 1'
    
    @app.route('/path1/shared')
    @breadcrumb_extension('Shared', order=0)
    def shared1():
        return 'Shared 1'
    
    @app.route('/path1/shared/item')
    @breadcrumb_extension('Item', order=0)
    def item1():
        return 'Item 1'
    
    @app.route('/path2')
    @breadcrumb_extension('Path 2', order=1)
    def path2():
        return 'Path 2'
    
    # Test the breadcrumb tree at different paths
    with app.test_request_context('/'):
        app.preprocess_request()
        tree = breadcrumb_extension.app.extensions['breadcrumb'].app.context_processor(
            lambda: {}
        )['breadcrumb_tree']()
        assert tree['text'] == 'Home'
        assert len(tree['children']) == 2
        assert tree['children'][0]['text'] == 'Path 1'
        assert tree['children'][1]['text'] == 'Path 2'
    
    with app.test_request_context('/path1/shared/item'):
        app.preprocess_request()
        tree = breadcrumb_extension.app.extensions['breadcrumb'].app.context_processor(
            lambda: {}
        )['breadcrumb_tree']()
        assert tree['text'] == 'Home'
        assert tree['children'][0]['text'] == 'Path 1'
        assert tree['children'][0]['children'][0]['text'] == 'Shared'
        assert tree['children'][0]['children'][0]['children'][0]['text'] == 'Item'
        assert tree['children'][0]['children'][0]['children'][0]['is_current_path'] == True


def test_dynamic_text(app, breadcrumb_extension):
    """Test using a function for breadcrumb text."""
    @app.route('/dynamic/<name>')
    @breadcrumb_extension(lambda: f'Dynamic {request.view_args["name"]}')
    def dynamic(name):
        return f'Dynamic {name}'
    
    with app.test_request_context('/dynamic/test'):
        app.preprocess_request()
        assert '/dynamic/test' in app.config['BREADCRUMB_ITEMS']
        item = app.config['BREADCRUMB_ITEMS']['/dynamic/test']
        assert callable(item.text)
        assert item.to_dict()['text'] == 'Dynamic test'
