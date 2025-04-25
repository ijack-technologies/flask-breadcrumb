"""
Flask-Breadcrumb Example

This example demonstrates how to use the Flask-Breadcrumb extension
with the ability to print breadcrumbs.
"""

from flask import Flask, render_template_string

from flask_breadcrumb import Breadcrumb, get_breadcrumbs

# Create Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "example-secret-key"

# Initialize Breadcrumb
breadcrumb = Breadcrumb(app)

# Simple template that shows the breadcrumb structure
base_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask-Breadcrumb Example</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        .content {
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        nav ul {
            list-style: none;
            padding: 0;
            display: flex;
            background-color: #333;
            margin-bottom: 20px;
        }
        nav ul li {
            margin: 0;
            padding: 0;
        }
        nav ul li a {
            display: block;
            color: white;
            text-decoration: none;
            padding: 10px 15px;
        }
        nav ul li a:hover {
            background-color: #555;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .breadcrumb {
            display: flex;
            list-style: none;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 4px;
        }
        .breadcrumb li {
            margin-right: 10px;
        }
        .breadcrumb li:after {
            content: ">";
            margin-left: 10px;
        }
        .breadcrumb li:last-child:after {
            content: "";
        }
        .breadcrumb a {
            text-decoration: none;
            color: #0066cc;
        }
        .breadcrumb .current {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <nav>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/path1">Path 1</a></li>
            <li><a href="/path2">Path 2</a></li>
            <li><a href="/path1/shared">Path 1 > Shared</a></li>
            <li><a href="/path2/shared">Path 2 > Shared</a></li>
            <li><a href="/path1/shared/item">Path 1 > Shared > Item</a></li>
            <li><a href="/path2/shared/item">Path 2 > Shared > Item</a></li>
        </ul>
    </nav>

    <div class="content">
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>

        <!-- Display breadcrumbs -->
        <ul class="breadcrumb">
            {% set crumbs = breadcrumb_tree() %}
            <li><a href="{{ crumbs.url }}">{{ crumbs.text }}</a></li>
            {% for child in crumbs.children recursive %}
                {% if child.is_current_path %}
                    <li class="current">{{ child.text }}</li>
                {% else %}
                    <li><a href="{{ child.url }}">{{ child.text }}</a></li>
                {% endif %}
                {% if child.children %}
                    {{ loop(child.children) }}
                {% endif %}
            {% endfor %}
        </ul>
    </div>

    <div class="content">
        <h2>Breadcrumb JSON Structure</h2>
        <pre>{{ breadcrumb_json }}</pre>
    </div>
</body>
</html>
"""


# Home page
@app.route("/")
@breadcrumb("Home", order=0)
def index():
    """Home page with a simple breadcrumb."""
    title = "Home"
    description = "This example demonstrates how to use the Flask-Breadcrumb extension with the ability to print breadcrumbs."

    # Get the breadcrumb JSON for the current route
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print("\n=== Breadcrumbs for / ===")
    print(breadcrumb_json)
    print("========================\n")

    # Also print the breadcrumbs for other routes to show they're working correctly
    print("=== Breadcrumbs for /path1 (from home) ===")
    print(get_breadcrumbs("/path1"))
    print("================================\n")

    print("=== Breadcrumbs for /path2 (from home) ===")
    print(get_breadcrumbs("/path2"))
    print("================================\n")

    return render_template_string(
        base_template,
        title=title,
        description=description,
        breadcrumb_json=breadcrumb_json,
    )


# Path 1
@app.route("/path1")
@breadcrumb("Path 1", order=0)
def path1():
    """First path."""
    title = "Path 1"
    description = "This is the first path. Notice how the breadcrumb structure shows the hierarchical relationship."

    # Get the breadcrumb JSON for the current route
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print("\n=== Breadcrumbs for /path1 ===")
    print(breadcrumb_json)
    print("============================\n")

    return render_template_string(
        base_template,
        title=title,
        description=description,
        breadcrumb_json=breadcrumb_json,
    )


# Path 2
@app.route("/path2")
@breadcrumb("Path 2", order=1)
def path2():
    """Second path."""
    title = "Path 2"
    description = "This is the second path. Notice how the breadcrumb structure shows the hierarchical relationship."

    # Get the breadcrumb JSON for the current route
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print("\n=== Breadcrumbs for /path2 ===")
    print(breadcrumb_json)
    print("============================\n")

    return render_template_string(
        base_template,
        title=title,
        description=description,
        breadcrumb_json=breadcrumb_json,
    )


# Path 1 > Shared
@app.route("/path1/shared")
@breadcrumb("Shared", order=0)
def path1_shared():
    """Shared page under path 1."""
    title = "Shared (under Path 1)"
    description = "This is a shared page under Path 1. Notice how the breadcrumb structure shows the hierarchical relationship."

    # Get the breadcrumb JSON for the current route
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print("\n=== Breadcrumbs for /path1/shared ===")
    print(breadcrumb_json)
    print("==================================\n")

    return render_template_string(
        base_template,
        title=title,
        description=description,
        breadcrumb_json=breadcrumb_json,
    )


# Path 2 > Shared
@app.route("/path2/shared")
@breadcrumb("Shared", order=0)
def path2_shared():
    """Shared page under path 2."""
    title = "Shared (under Path 2)"
    description = "This is a shared page under Path 2. Notice how the breadcrumb structure shows the hierarchical relationship."

    # Get the breadcrumb JSON for the current route
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print("\n=== Breadcrumbs for /path2/shared ===")
    print(breadcrumb_json)
    print("==================================\n")

    return render_template_string(
        base_template,
        title=title,
        description=description,
        breadcrumb_json=breadcrumb_json,
    )


# Path 1 > Shared > Item
@app.route("/path1/shared/item")
@breadcrumb("Item", order=0)
def path1_shared_item():
    """Item page under path 1 > shared."""
    title = "Item (under Path 1 > Shared)"
    description = "This is an item page under Path 1 > Shared. Notice how the breadcrumb structure shows the hierarchical relationship."

    # Get the breadcrumb JSON for the current route
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print("\n=== Breadcrumbs for /path1/shared/item ===")
    print(breadcrumb_json)
    print("=======================================\n")

    # You can also get breadcrumbs for a different route
    other_breadcrumbs = get_breadcrumbs("/path2")
    print("\n=== Breadcrumbs for /path2 (from another route) ===")
    print(other_breadcrumbs)
    print("==============================================\n")

    return render_template_string(
        base_template,
        title=title,
        description=description,
        breadcrumb_json=breadcrumb_json,
    )


# Path 2 > Shared > Item
@app.route("/path2/shared/item")
@breadcrumb("Item", order=0)
def path2_shared_item():
    """Item page under path 2 > shared."""
    title = "Item (under Path 2 > Shared)"
    description = "This is an item page under Path 2 > Shared. Notice how the breadcrumb structure shows the hierarchical relationship."

    # Get the breadcrumb JSON for the current route
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print("\n=== Breadcrumbs for /path2/shared/item ===")
    print(breadcrumb_json)
    print("=======================================\n")

    return render_template_string(
        base_template,
        title=title,
        description=description,
        breadcrumb_json=breadcrumb_json,
    )


if __name__ == "__main__":
    # Run the application
    app.config["ENV"] = "development"
    app.run(debug=True, port=5000)
