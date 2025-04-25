# Flask-Breadcrumb

A Flask extension that provides hierarchical breadcrumb navigation for your Flask applications.

## Features

- Hierarchical breadcrumb structure with parent-child relationships
- Automatic parent-child relationship detection based on URL paths
- Support for custom ordering of breadcrumbs
- Support for dynamic breadcrumb text using functions
- Easy integration with Flask templates
- JSON output for easy integration with JavaScript frameworks

## Installation

```bash
pip install flask-breadcrumb
```

## Basic Usage

```python
from flask import Flask
from flask_breadcrumb import Breadcrumb

app = Flask(__name__)
breadcrumb = Breadcrumb(app)

# Or use the init_app pattern
# breadcrumb = Breadcrumb()
# breadcrumb.init_app(app)

@app.route('/')
@breadcrumb('Home', order=0)
def index():
    return 'Home'

@app.route('/path1')
@breadcrumb('Path 1', order=0)
def path1():
    return 'Path 1'

@app.route('/path1/subpath')
@breadcrumb('Subpath', order=0)
def subpath():
    return 'Subpath'
```

## How It Works

The Flask-Breadcrumb extension automatically:

1. Analyzes your Flask application's URL routes
2. Builds a breadcrumb path from the current page up to the root
3. Applies custom text and ordering from your `@breadcrumb` decorators
4. Makes the breadcrumb tree available in your templates and through API functions

Unlike other breadcrumb extensions, it doesn't rely on storing state in the application config, which can lead to issues with breadcrumbs being mixed together. Instead, it builds the breadcrumb tree on-demand by analyzing the URL structure.

The breadcrumb tree includes:

1. The current page and its ancestors (the path from the current page to the root)
2. Siblings at each level of the hierarchy
3. No children of the current page (only showing upward and lateral navigation)

This means:

- The home page will show "Home" with no children
- A page at "/path1" will show "Home > Path 1" with "Path 2" as a sibling of "Path 1", but no children of "Path 1"
- A page at "/path1/subpath" will show "Home > Path 1 > Subpath" with siblings at each level, but no children of "Subpath"

This approach allows users to navigate up the hierarchy and laterally to sibling pages, but doesn't clutter the breadcrumbs with child pages that would be better shown in a separate navigation menu.

## Accessing Breadcrumbs in Templates

The breadcrumb tree is available in templates through the `breadcrumb_tree()` function:

```html
<ul class="breadcrumb">
  {% set crumbs = breadcrumb_tree() %}
  <li><a href="{{ crumbs.url }}">{{ crumbs.text }}</a></li>
  {% for child in crumbs.children recursive %} {% if child.is_current_path %}
  <li class="current">{{ child.text }}</li>
  {% else %}
  <li><a href="{{ child.url }}">{{ child.text }}</a></li>
  {% endif %} {% if child.children %} {{ loop(child.children) }} {% endif %} {%
  endfor %}
</ul>
```

## Printing Breadcrumbs

You can print the breadcrumb tree for debugging or API responses:

```python
from flask_breadcrumb import get_breadcrumbs

@app.route('/path1/subpath')
@breadcrumb('Subpath', order=0)
def subpath():
    # Get breadcrumbs for the current route
    breadcrumbs = get_breadcrumbs()
    print(breadcrumbs)

    # Or get breadcrumbs for a specific route
    other_breadcrumbs = get_breadcrumbs('/path2')
    print(other_breadcrumbs)

    return 'Subpath'
```

## Breadcrumb Structure

The breadcrumb tree has the following structure:

```json
{
  "text": "Home",
  "url": "/",
  "order": 0,
  "is_current_path": true,
  "children": [
    {
      "text": "Path 1",
      "url": "/path1",
      "order": 0,
      "is_current_path": true,
      "children": [
        {
          "text": "Shared",
          "url": "/path1/shared",
          "order": 0,
          "is_current_path": true,
          "children": [
            {
              "text": "Item",
              "url": "/path1/shared/item",
              "order": 0,
              "is_current_path": true,
              "children": []
            }
          ]
        }
      ]
    },
    {
      "text": "Path 2",
      "url": "/path2",
      "order": 1,
      "is_current_path": false,
      "children": []
    }
  ]
}
```

## Dynamic Breadcrumb Text

You can use a function to generate dynamic breadcrumb text:

```python
from flask import request

@app.route('/user/<username>')
@breadcrumb(lambda: f'User: {request.view_args["username"]}')
def user_profile(username):
    return f'Profile for {username}'
```

## Advanced Options

### Custom Ordering

You can control the order of breadcrumbs:

```python
@app.route('/path1')
@breadcrumb('Path 1', order=1)
def path1():
    return 'Path 1'

@app.route('/path2')
@breadcrumb('Path 2', order=0)  # Will appear before Path 1
def path2():
    return 'Path 2'
```

### Default Text Generation

If you don't provide text for a breadcrumb, the extension will generate default text based on the URL:

- `/` becomes "Home"
- `/users` becomes "Users"
- `/users/profile` becomes "Profile"

## Example

See the `example.py` file for a complete working example.

## License

MIT
