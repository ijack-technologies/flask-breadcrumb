"""Flask-Breadcrumb extension for Flask applications."""

import json
import re
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from flask import current_app, request

__all__ = [
    "Breadcrumb",
    "breadcrumb",
    "breadcrumb_tree",
    "get_breadcrumbs",
]


class BreadcrumbItem:
    """Class representing a breadcrumb item."""

    def __init__(
        self,
        text: Union[str, Callable],
        url: str,
        order: Optional[int] = None,
        is_current_path: bool = False,
    ):
        """Initialize a breadcrumb item.

        Args:
            text: Text to display for the breadcrumb or a function that returns the text
            url: URL for the breadcrumb
            order: Order of the breadcrumb (used for sorting)
            is_current_path: Whether this breadcrumb represents the current path
        """
        self.text = text
        self.url = url
        self.order = order if order is not None else 0
        self.is_current_path = is_current_path
        self.children = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert the breadcrumb item to a dictionary."""
        return {
            "text": self.text() if callable(self.text) else self.text,
            "url": self.url,
            "order": self.order,
            "is_current_path": self.is_current_path,
            "children": [child.to_dict() for child in self.children],
        }

    def add_child(self, child: "BreadcrumbItem") -> None:
        """Add a child breadcrumb item.

        Args:
            child: Child breadcrumb item to add
        """
        # Check if child is already in children
        for existing_child in self.children:
            if existing_child.url == child.url:
                return
        self.children.append(child)
        # Sort children by order
        self.children.sort(key=lambda x: (x.order, x.url))


class Breadcrumb:
    """Breadcrumb organizer for a Flask application."""

    def __init__(self, app=None):
        """Initialize Breadcrumb extension.

        Args:
            app: Flask application object
        """
        # Dictionary to store breadcrumb metadata for routes
        self.breadcrumb_metadata = {}

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Configure an application. This registers a context_processor.

        Args:
            app: The flask.Flask object to configure.
        """
        if not hasattr(app, "extensions"):
            app.extensions = {}

        # Register context processor to make breadcrumbs available in templates
        app.context_processor(lambda: {"breadcrumb_tree": self.get_breadcrumb_tree})

        app.extensions["breadcrumb"] = self

        return self

    def __call__(self, text, order=None, max_depth=None):
        """Decorator to register a view function as a breadcrumb.

        Args:
            text: Text to display for the breadcrumb or a function that returns the text
            order: Order of the breadcrumb (used for sorting)
            max_depth: Maximum depth to traverse up the breadcrumb tree

        Returns:
            Decorator function
        """

        def decorator(f):
            # Store metadata about this route's breadcrumb
            endpoint = f.__name__
            self.breadcrumb_metadata[endpoint] = {
                "text": text,
                "order": order,
                "max_depth": max_depth,
            }

            @wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)

            return decorated_function

        return decorator

    def get_breadcrumb_tree(self):
        """Build a hierarchical breadcrumb tree based on the current request path.

        Returns:
            Dictionary representing the breadcrumb tree
        """
        if not current_app:
            return {}

        # Get the current URL path
        current_path = request.path.rstrip("/")
        if not current_path:
            current_path = "/"

        # Build the breadcrumb tree
        return self._build_breadcrumb_tree(current_path)

    def _build_breadcrumb_tree(self, current_path):
        """Build a breadcrumb tree for a specific path.

        Args:
            current_path: Path to build breadcrumbs for

        Returns:
            Dictionary representing the breadcrumb tree
        """
        # Get all routes from the application
        routes = self._get_routes()

        # Create a dictionary to store breadcrumb items by URL
        breadcrumb_items = {}

        # Precompute is_current_path for each URL
        is_current_path_map = {}

        # First, create breadcrumb items for all routes
        for url, endpoint, methods in routes:
            # Skip static files and other non-GET routes
            if "GET" not in methods or endpoint.startswith("static"):
                continue

            # Get metadata for this endpoint
            metadata = self.breadcrumb_metadata.get(endpoint, {})
            text = metadata.get("text", self._generate_default_text(url))
            order = metadata.get("order", 0)

            # Create a breadcrumb item
            is_current = url == current_path
            is_current_path_map[url] = is_current
            breadcrumb_items[url] = BreadcrumbItem(
                text=text, url=url, order=order, is_current_path=is_current
            )

        # If we don't have any breadcrumb items, return an empty dict
        if not breadcrumb_items:
            return {}

        # Make sure we have a root item
        if "/" not in breadcrumb_items:
            is_current = current_path == "/"
            is_current_path_map["/"] = is_current
            breadcrumb_items["/"] = BreadcrumbItem(
                text="Home", url="/", order=0, is_current_path=is_current
            )

        # Special case for root path
        if current_path == "/":
            root_item = breadcrumb_items["/"]
            return {
                "text": root_item.text()
                if callable(root_item.text)
                else root_item.text,
                "url": "/",
                "order": root_item.order,
                "is_current_path": True,
                "children": [],
            }

        # Build the path from current page to root
        path_to_root = []
        path = current_path

        # Precompute parent URLs for all paths
        parent_url_map = {}
        for url in breadcrumb_items:
            parent_url_map[url] = self._get_parent_url(url)

        # Traverse up the path until we reach the root
        while path != "/":
            if path in breadcrumb_items:
                path_to_root.append(path)
            parent_path = parent_url_map.get(path, self._get_parent_url(path))
            if parent_path == path:  # Avoid infinite loop
                break
            path = parent_path

        # Add the root
        if "/" in breadcrumb_items:
            path_to_root.append("/")

        # If we couldn't find a path to root, return just the current page
        if not path_to_root:
            if current_path in breadcrumb_items:
                item = breadcrumb_items[current_path]
                return {
                    "text": item.text() if callable(item.text) else item.text,
                    "url": item.url,
                    "order": item.order,
                    "is_current_path": True,
                    "children": [],
                }
            return {}

        # Build a dictionary to store parent-child relationships
        parent_to_children = {}

        # Precompute child relationships
        is_child_map = {}
        for url in breadcrumb_items:
            if url != "/" and url != current_path:
                is_child_map[(url, current_path)] = self._is_child_of(url, current_path)

        # Group items by their parent URL, but only include siblings of items in our path
        # and don't include children of the current path
        for url, item in breadcrumb_items.items():
            if url == "/":
                continue

            parent_url = parent_url_map.get(url, self._get_parent_url(url))

            # Only include items that are siblings of items in our path or the path itself
            # Skip items that are children of the current path
            if is_child_map.get((url, current_path), False):
                continue

            children = parent_to_children.get(parent_url, [])
            children.append(
                {
                    "text": item.text() if callable(item.text) else item.text,
                    "url": url,
                    "order": item.order,
                    "is_current_path": is_current_path_map.get(url, False),
                    "children": [],
                }
            )
            parent_to_children[parent_url] = children

        # Sort children by order
        for parent_url, children in parent_to_children.items():
            children.sort(key=lambda x: (x["order"], x["url"]))

        # Start with the root
        root_item = breadcrumb_items["/"]
        result = {
            "text": root_item.text() if callable(root_item.text) else root_item.text,
            "url": "/",
            "order": root_item.order,
            "is_current_path": is_current_path_map.get("/", False),
            "children": [],
        }
        current_level = result

        # Add root's children (top-level items)
        if "/" in parent_to_children:
            current_level["children"] = parent_to_children["/"]

        # Now traverse the path from root to the current page
        for i, path in enumerate(reversed(path_to_root)):
            if i == 0:  # Skip root, we already added it
                continue

            # Find the current path in the children
            for child in current_level["children"]:
                if child["url"] == path:
                    # This is the next level in our path
                    if path in parent_to_children and path != current_path:
                        # Add its children, but only if this isn't the current path
                        # (we don't want to show children of the current path)
                        child["children"] = parent_to_children[path]

                    # Move to the next level
                    current_level = child
                    break

        return result

    def _is_child_of(self, child_url, parent_url):
        """Check if a URL is a child of another URL.

        Args:
            child_url: The potential child URL
            parent_url: The potential parent URL

        Returns:
            True if child_url is a child of parent_url, False otherwise
        """
        # If either URL is the root, handle specially
        if parent_url == "/":
            return child_url != "/"

        # A URL is a child of another URL if it starts with the parent URL
        # and has additional path components
        # This is more efficient than using startswith() alone
        parent_len = len(parent_url)
        return (
            len(child_url) > parent_len + 1
            and child_url[:parent_len] == parent_url
            and child_url[parent_len] == "/"
        )

    def _get_routes(self):
        """Get all routes from the Flask application.

        Returns:
            List of tuples (url, endpoint, methods)
        """
        # Check if we have a cached version
        if hasattr(self, "_routes_cache"):
            return self._routes_cache

        routes = []
        for rule in current_app.url_map.iter_rules():
            # Convert the URL pattern to a concrete URL
            url = str(rule)

            # Remove variable parts (e.g., /<id>/ becomes /)
            url = re.sub(r"<[^>]+>", "", url)

            # Remove duplicate slashes
            url = re.sub(r"//+", "/", url)

            # Remove trailing slash except for root
            if url != "/" and url.endswith("/"):
                url = url[:-1]

            routes.append((url, rule.endpoint, rule.methods))

        # Cache the routes
        self._routes_cache = routes
        return routes

    def _get_parent_url(self, url):
        """Get the parent URL for a given URL.

        Args:
            url: URL to get the parent for

        Returns:
            Parent URL
        """
        # Remove trailing slash if present
        url = url.rstrip("/")

        # If we're at the root, there's no parent
        if url == "":
            return "/"

        # Split the URL into parts
        parts = url.split("/")

        # If there's only one part (e.g., '/home'), the parent is the root
        if len(parts) <= 2:
            return "/"

        # Otherwise, remove the last part to get the parent
        return "/".join(parts[:-1])

    def _generate_default_text(self, url):
        """Generate default text for a URL if none is provided.

        Args:
            url: URL to generate text for

        Returns:
            Default text for the URL
        """
        # Remove trailing slash if present
        url = url.rstrip("/")

        # If it's the root, return 'Home'
        if url == "":
            return "Home"

        # Otherwise, use the last part of the URL
        parts = url.split("/")
        last_part = parts[-1]

        # Convert to title case and replace hyphens/underscores with spaces
        last_part = last_part.replace("-", " ").replace("_", " ").title()

        return last_part or "Home"


def breadcrumb(text, order=None, max_depth=None):
    """Decorator to register a view function as a breadcrumb.

    Args:
        text: Text to display for the breadcrumb or a function that returns the text
        order: Order of the breadcrumb (used for sorting)
        max_depth: Maximum depth to traverse up the breadcrumb tree

    Returns:
        Decorator function
    """
    if (
        not hasattr(current_app, "extensions")
        or "breadcrumb" not in current_app.extensions
    ):
        # If the extension isn't initialized yet, create a dummy decorator
        def dummy_decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)

            return decorated_function

        return dummy_decorator

    # Get the breadcrumb extension
    extension = current_app.extensions["breadcrumb"]

    # Use the extension's decorator
    return extension(text, order, max_depth)


def breadcrumb_tree():
    """Get the breadcrumb tree for the current request.

    Returns:
        Dictionary representing the breadcrumb tree
    """
    if (
        not hasattr(current_app, "extensions")
        or "breadcrumb" not in current_app.extensions
    ):
        return {}

    # Get the breadcrumb extension
    extension = current_app.extensions["breadcrumb"]

    # Use the extension's method
    return extension.get_breadcrumb_tree()


def get_breadcrumbs(url=None):
    """Get the breadcrumb tree for a specific URL.

    Args:
        url: URL to get breadcrumbs for. If None, uses the current request path.

    Returns:
        JSON string representation of the breadcrumb tree
    """
    if (
        not hasattr(current_app, "extensions")
        or "breadcrumb" not in current_app.extensions
    ):
        return "{}"

    # Get the breadcrumb extension
    extension = current_app.extensions["breadcrumb"]

    # If no URL is provided, use the current request path
    if url is None:
        tree = extension.get_breadcrumb_tree()
    else:
        # Create a test request context with the provided URL
        with current_app.test_request_context(url):
            tree = extension.get_breadcrumb_tree()

    # Return the tree as a JSON string
    return json.dumps(tree, indent=2)
