"""Flask-Breadcrumb extension for Flask applications."""

import json
import re
from functools import wraps
from typing import Any, Callable, Dict, Union
from urllib.parse import urlparse

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
        is_current_path: bool = False,
    ):
        """Initialize a breadcrumb item.

        Args:
            text: Text to display for the breadcrumb or a function that returns the text
            url: URL for the breadcrumb
            is_current_path: Whether this breadcrumb represents the current path
        """
        self.text = text
        self.url = url
        self.is_current_path = is_current_path
        self.children = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert the breadcrumb item to a dictionary."""
        return {
            "text": self.text() if callable(self.text) else self.text,
            "url": self.url,
            "is_current_path": self.is_current_path,
            "children": [child.to_dict() for child in self.children],
        }

    def add(self, breadcrumb: "BreadcrumbItem") -> None:
        """Check the breadcrumb and add it to the tree.

        Args:
            breadcrumb: Breadcrumb item to add
        """
        if self.is_child(breadcrumb):
            self.add_child(breadcrumb)
        elif self.is_parent(breadcrumb):
            return self.make_parent(breadcrumb)
        else:
            for child in self.children:
                child.add(breadcrumb)
        return self

    def is_child(self, breadcrumb: "BreadcrumbItem") -> bool:
        """Check if a breadcrumb is a child of this one.

        Args:
            breadcrumb: Breadcrumb item to check

        Returns:
            True if the breadcrumb is a child, False otherwise
        """
        return breadcrumb.url.startswith(self.url) and breadcrumb.url != self.url

    def is_parent(self, breadcrumb: "BreadcrumbItem") -> bool:
        """Check if a breadcrumb is a parent of this one.

        Args:
            breadcrumb: Breadcrumb item to check

        Returns:
            True if the breadcrumb is a parent, False otherwise
        """
        return self.url.startswith(breadcrumb.url) and breadcrumb.url != self.url

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
        # Sort children by url
        self.children.sort(key=lambda x: x.url)

    def make_parent(self, parent: "BreadcrumbItem") -> None:
        """Add a parent breadcrumb item.

        Args:
            parent: Parent breadcrumb item to add
        """
        parent.add_child(self)
        return parent


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

        app.extensions["breadcrumb"] = self

        return self

    def __call__(self, text, max_depth=None):
        """Decorator to register a view function as a breadcrumb.

        Args:
            text: Text to display for the breadcrumb or a function that returns the text
            max_depth: Maximum depth to traverse up the breadcrumb tree

        Returns:
            Decorator function
        """

        def decorator(f):
            # Store metadata about this route's breadcrumb
            endpoint = f.__name__
            self.breadcrumb_metadata[endpoint] = {
                "text": text
                if text is not None
                else endpoint.title().replace("_", " "),
            }

            @wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)

            return decorated_function

        return decorator

    def _get_parent_url(self, rule):
        url = str(rule)
        remaining, target = url.rsplit("/", 1)
        # if the target is like <.*>
        is_dynamic = re.match(r"^<.+>$", target) is not None
        if is_dynamic:
            return remaining
        else:
            return url

    def parse(self, max_depth=None, use_root=False):
        if "GET" not in request.method:
            return {}
        # filter out rules with GET not in methods
        routes = list(
            filter(
                lambda x: ("GET" in x.methods or str(x) == str(request.url_rule))
                and x.endpoint in self.breadcrumb_metadata,
                current_app.url_map.iter_rules(),
            )
        )
        crumbs = str(request.url_rule).split("/")
        if max_depth is None:
            max_depth = 0
        else:
            max_depth = len(crumbs) - max_depth - 1
        crumbs = crumbs[max_depth:]
        breadcrumbs = []
        for i, crumb in enumerate(crumbs):
            if not crumb and not use_root:
                continue
            crumbs[i] = "/" + crumb
            if use_root:
                start_url = 1
            else:
                start_url = 0
            search_url = "".join(crumbs[start_url : i + 1])

            def parse(route_path, args, base_url):
                startswith = str(route_path).startswith(base_url)
                if not startswith:
                    return False
                remaining = str(route_path)[len(base_url) :]
                if len(list(filter(None, remaining.split("/")))) > 1:
                    return False
                curr_args = request.url_rule.arguments
                if not args.issubset(curr_args):
                    return False
                return True

            if breadcrumbs == {}:
                breadcrumbs = []
            breadcrumbs = breadcrumbs + [
                BreadcrumbItem(
                    text=self.breadcrumb_metadata[x.endpoint]["text"],
                    url=urlparse(x.build(request.view_args)[-1]).path,
                    is_current_path=urlparse(x.build(request.view_args)[-1]).path
                    in request.path,
                )
                for x in list(
                    filter(
                        lambda x: parse(x, x.arguments, search_url),
                        routes,
                    )
                )
            ]
        route_map = {}
        breadcrumbs.reverse()
        for b in breadcrumbs:
            if route_map == {}:
                route_map = b
                continue
            else:
                route_map = route_map.add(b)

        return route_map.to_dict() if isinstance(route_map, BreadcrumbItem) else {}


def get_breadcrumbs(url=None, max_depth=None, use_root=False):
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
        tree = extension.parse(max_depth, use_root)
    else:
        # Create a test request context with the provided URL
        with current_app.test_request_context(url):
            tree = extension.parse()

    # Return the tree as a JSON string
    return json.dumps(tree, indent=2)
