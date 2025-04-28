# Flask-Breadcrumb

[![build](https://github.com/username/flask-breadcrumb/actions/workflows/build.yml/badge.svg)](https://github.com/username/flask-breadcrumb/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/username/flask-breadcrumb/badge.svg?branch=main)](https://coveralls.io/github/username/flask-breadcrumb?branch=main)
[![PyPI version](https://badge.fury.io/py/flask-breadcrumb.svg)](https://badge.fury.io/py/flask-breadcrumb)
[![Python Versions](https://img.shields.io/pypi/pyversions/flask-breadcrumb.svg)](https://pypi.org/project/flask-breadcrumb/)

A Flask extension that provides automatic breadcrumb generation for your Flask applications. It intelligently builds hierarchical breadcrumb navigation based on your URL structure.

## Features

- Automatic breadcrumb generation based on URL structure
- Support for dynamic route parameters
- Customizable breadcrumb text
- Hierarchical breadcrumb structure with parent-child relationships
- JSON output for easy integration with frontend frameworks
- Support for dynamic text generation using route parameters

## Installation

```bash
pip install flask-breadcrumb
```

Or with uv:

```bash
uv pip install flask-breadcrumb
```

## Quick Start

```python
from flask import Flask, render_template_string, request
from flask_breadcrumb import Breadcrumb, get_breadcrumbs

app = Flask(__name__)
breadcrumb = Breadcrumb(app)

@app.route('/')
@breadcrumb("Home")
def index():
    return 'Home'

@app.route('/categories')
@breadcrumb("Categories")
def categories():
    # Get breadcrumbs as JSON
    breadcrumb_json = get_breadcrumbs()
    return render_template_string(
        '<pre>{{ breadcrumb_json }}</pre>',
        breadcrumb_json=breadcrumb_json
    )

@app.route('/categories/<category>')
@breadcrumb(lambda: f"Category: {request.view_args['category']}")
def category_page(category):
    breadcrumb_json = get_breadcrumbs()
    return render_template_string(
        '<pre>{{ breadcrumb_json }}</pre>',
        breadcrumb_json=breadcrumb_json
    )

if __name__ == '__main__':
    app.run(debug=True)
```

## Usage

### Basic Usage

Decorate your route functions with the `@breadcrumb` decorator to add them to the breadcrumb hierarchy:

```python
@app.route('/path1')
@breadcrumb("Path 1")
def path1():
    return 'Path 1'

@app.route('/path1/subpath')
@breadcrumb("Subpath")
def subpath():
    return 'Subpath'
```

### Dynamic Breadcrumb Text

You can use a function to generate dynamic breadcrumb text based on route parameters:

```python
@app.route('/user/<username>')
@breadcrumb(lambda: f"User: {request.view_args['username']}")
def user_profile(username):
    return f'Profile for {username}'
```

### Getting Breadcrumbs

To get the breadcrumb tree for the current request:

```python
breadcrumb_json = get_breadcrumbs()
```

You can also get breadcrumbs for a specific URL:

```python
other_breadcrumbs = get_breadcrumbs('/path2')
```

### Advanced Options

#### Max Depth

You can limit the depth of the breadcrumb tree:

```python
breadcrumb_json = get_breadcrumbs(max_depth=1)
```

#### Include Root

By default, the root path ('/') is not included in the breadcrumb tree. You can include it by setting `use_root=True`:

```python
breadcrumb_json = get_breadcrumbs(use_root=True)
```

## Breadcrumb Structure

The breadcrumb tree is returned as a JSON string with the following structure:

```json
{
  "text": "Home",
  "url": "/",
  "is_current_path": false,
  "children": [
    {
      "text": "Categories",
      "url": "/categories",
      "is_current_path": false,
      "children": [
        {
          "text": "Category: test",
          "url": "/categories/test",
          "is_current_path": true,
          "children": []
        }
      ]
    }
  ]
}
```

## Template Integration

Here's an example of how to render breadcrumbs in a Jinja2 template:

```html
{% set crumbs = breadcrumb_tree() %}
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item">
      <a href="{{ crumbs.url }}">{{ crumbs.text }}</a>
    </li>
    {% for child in crumbs.children recursive %} {% if child.is_current_path %}
    <li class="breadcrumb-item active" aria-current="page">{{ child.text }}</li>
    {% else %}
    <li class="breadcrumb-item">
      <a href="{{ child.url }}">{{ child.text }}</a>
    </li>
    {% endif %} {% if child.children %} {{ loop(child.children) }} {% endif %}
    {% endfor %}
  </ol>
</nav>
```

## API Reference

### `Breadcrumb(app=None)`

The main extension class.

- `app`: Flask application instance (optional). If not provided, you must call `init_app` later.

### `Breadcrumb.init_app(app)`

Initialize the extension with a Flask application.

- `app`: Flask application instance.

### `@breadcrumb(text)`

Decorator to register a view function as a breadcrumb.

- `text`: Text to display for the breadcrumb or a function that returns the text.

### `get_breadcrumbs(url=None, max_depth=None, use_root=False)`

Get the breadcrumb tree for a specific URL.

- `url`: URL to get breadcrumbs for. If None, uses the current request path.
- `max_depth`: Maximum depth to traverse up the breadcrumb tree.
- `use_root`: Whether to include the root path ('/') in the breadcrumb tree.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
