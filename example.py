"""
Flask-Breadcrumb Example

This example demonstrates how to use the Flask-Breadcrumb extension
with the ability to print breadcrumbs.
"""

from flask import Flask, render_template_string, request

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
</head>
<body>
    <nav>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/categories">Categories</a></li>
            <li><a href="/categories/test">Categories > Test</a></li>
            <li><a href="/categories/test/products">Categories > Test > Products</a></li>
            <li><a href="/categories/test/products/other">Categories > Test > Products > Other</a></li>
        </ul>
    </nav>
    <div class="content">
        <h2>Breadcrumb JSON Structure</h2>
        <pre>{{ breadcrumb_json }}</pre>
    </div>
</body>
</html>
"""


# Home page
@app.route("/")
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


@app.route("/categories/<category>/products")
@breadcrumb("Categories")
def products(category):
    breadcrumb_json = get_breadcrumbs(use_root=True)

    # Print the breadcrumbs to the console
    print(f"\n=== Breadcrumbs for {request.path} ===")
    print(breadcrumb_json)
    print("=======================================\n")

    return render_template_string(
        base_template,
        breadcrumb_json=breadcrumb_json,
    )


@app.route("/categories/<category>/sales")
@breadcrumb("Categories")
def sales(category):
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print(f"\n=== Breadcrumbs for {request.path} ===")
    print(breadcrumb_json)
    print("=======================================\n")

    return render_template_string(
        base_template,
        breadcrumb_json=breadcrumb_json,
    )


@app.route("/categories/<category>/products/<product>")
@breadcrumb("Categories")
def product(category, product):
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print(f"\n=== Breadcrumbs for {request.path} ===")
    print(breadcrumb_json)
    print("=======================================\n")

    return render_template_string(
        base_template,
        breadcrumb_json=breadcrumb_json,
    )


@app.route("/categories/<category>")
@breadcrumb("Categories")
def category(category):
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print(f"\n=== Breadcrumbs for {request.path} ===")
    print(breadcrumb_json)
    print("=======================================\n")

    return render_template_string(
        base_template,
        breadcrumb_json=breadcrumb_json,
    )


@app.route("/categories")
@breadcrumb("Categories")
def categories():
    breadcrumb_json = get_breadcrumbs()

    # Print the breadcrumbs to the console
    print(f"\n=== Breadcrumbs for {request.path} ===")
    print(breadcrumb_json)
    print("=======================================\n")

    return render_template_string(
        base_template,
        breadcrumb_json=breadcrumb_json,
    )


if __name__ == "__main__":
    # Run the application
    app.config["ENV"] = "development"
    app.run(debug=True, port=5000)
