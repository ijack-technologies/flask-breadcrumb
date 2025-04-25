"""
Performance test for Flask-Breadcrumb extension.

This script measures the time it takes to build the breadcrumb tree
for different numbers of routes and different depths of the current path.
"""

import statistics
import time

from flask import Flask

from flask_breadcrumb import Breadcrumb, get_breadcrumbs


def create_app_with_routes(num_routes, max_depth):
    """Create a Flask application with a specified number of routes.

    Args:
        num_routes: Number of routes to create
        max_depth: Maximum depth of routes

    Returns:
        Flask application
    """
    app = Flask(__name__)
    breadcrumb = Breadcrumb(app)

    # Create routes with different depths
    routes_created = 0

    # Add root route
    @app.route("/")
    @breadcrumb("Home", order=0)
    def index():
        return "Home"

    routes_created += 1

    # Add routes with different depths
    for i in range(min(num_routes - routes_created, 10)):
        route_path = f"/path{i}"
        endpoint = f"path_route_depth1_{i}"

        @app.route(route_path, endpoint=endpoint)
        @breadcrumb(f"Path {i}", order=i)
        def path_route_depth1():
            return f"Path {i}"

        routes_created += 1

        if routes_created >= num_routes or max_depth < 2:
            break

        # Add routes with depth 2
        for j in range(min(num_routes - routes_created, 5)):
            route_path = f"/path{i}/subpath{j}"
            endpoint = f"path_route_depth2_{i}_{j}"

            @app.route(route_path, endpoint=endpoint)
            @breadcrumb(f"Subpath {j}", order=j)
            def path_route_depth2():
                return f"Path {i} > Subpath {j}"

            routes_created += 1

            if routes_created >= num_routes or max_depth < 3:
                break

            # Add routes with depth 3
            for k in range(min(num_routes - routes_created, 3)):
                route_path = f"/path{i}/subpath{j}/item{k}"
                endpoint = f"path_route_depth3_{i}_{j}_{k}"

                @app.route(route_path, endpoint=endpoint)
                @breadcrumb(f"Item {k}", order=k)
                def path_route_depth3():
                    return f"Path {i} > Subpath {j} > Item {k}"

                routes_created += 1

                if routes_created >= num_routes:
                    break

    return app


def measure_performance(app, path, num_iterations=100):
    """Measure the time it takes to build the breadcrumb tree.

    Args:
        app: Flask application
        path: Path to build breadcrumbs for
        num_iterations: Number of iterations to run

    Returns:
        Tuple of (mean_time, median_time, min_time, max_time)
    """
    times = []

    with app.test_request_context(path):
        # Warm up
        get_breadcrumbs()

        # Measure
        for _ in range(num_iterations):
            start_time = time.time()
            get_breadcrumbs()
            end_time = time.time()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds

    return (statistics.mean(times), statistics.median(times), min(times), max(times))


def run_performance_tests():
    """Run performance tests for different numbers of routes and depths."""
    print("Running performance tests for Flask-Breadcrumb extension...")
    print()
    print("1. Testing with different numbers of routes")
    print("-------------------------------------------")
    print("Routes | Mean (ms) | Median (ms) | Min (ms) | Max (ms)")
    print("-------|-----------|-------------|----------|----------")

    for num_routes in [10, 50, 100, 200]:
        app = create_app_with_routes(num_routes, max_depth=3)
        mean, median, min_time, max_time = measure_performance(app, "/")
        print(
            f"{num_routes:6d} | {mean:9.3f} | {median:11.3f} | {min_time:8.3f} | {max_time:9.3f}"
        )

    print()
    print("2. Testing with different path depths")
    print("------------------------------------")
    print(
        "Depth | Path                  | Mean (ms) | Median (ms) | Min (ms) | Max (ms)"
    )
    print(
        "------|------------------------|-----------|-------------|----------|----------"
    )

    app = create_app_with_routes(100, max_depth=3)

    for depth, path in [
        (0, "/"),
        (1, "/path0"),
        (2, "/path0/subpath0"),
        (3, "/path0/subpath0/item0"),
    ]:
        mean, median, min_time, max_time = measure_performance(app, path)
        print(
            f"{depth:5d} | {path:22s} | {mean:9.3f} | {median:11.3f} | {min_time:8.3f} | {max_time:9.3f}"
        )


if __name__ == "__main__":
    run_performance_tests()
