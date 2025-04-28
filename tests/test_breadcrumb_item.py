"""Tests for BreadcrumbItem class in Flask-Breadcrumb extension."""

from flask_breadcrumb import BreadcrumbItem


def test_breadcrumb_item_init():
    """Test BreadcrumbItem initialization."""
    item = BreadcrumbItem(text="Home", url="/", is_current_path=True)

    assert item.text == "Home"
    assert item.url == "/"
    assert item.is_current_path is True
    assert item.children == []


def test_breadcrumb_item_to_dict():
    """Test BreadcrumbItem to_dict method."""
    item = BreadcrumbItem(text="Home", url="/", is_current_path=True)
    item_dict = item.to_dict()

    assert item_dict["text"] == "Home"
    assert item_dict["url"] == "/"
    assert item_dict["is_current_path"] is True
    assert item_dict["children"] == []


def test_breadcrumb_item_callable_text():
    """Test BreadcrumbItem with callable text."""
    item = BreadcrumbItem(text=lambda: "Dynamic Text", url="/", is_current_path=True)
    item_dict = item.to_dict()

    assert item_dict["text"] == "Dynamic Text"


def test_breadcrumb_item_add_child():
    """Test adding a child to a BreadcrumbItem."""
    parent = BreadcrumbItem(text="Parent", url="/parent", is_current_path=False)
    child = BreadcrumbItem(text="Child", url="/parent/child", is_current_path=True)

    parent.add(child)

    assert len(parent.children) == 1
    assert parent.children[0].text == "Child"
    assert parent.children[0].url == "/parent/child"
    assert parent.children[0].is_current_path is True


def test_breadcrumb_item_is_child():
    """Test is_child method."""
    parent = BreadcrumbItem(text="Parent", url="/parent", is_current_path=False)
    child = BreadcrumbItem(text="Child", url="/parent/child", is_current_path=True)
    not_child = BreadcrumbItem(text="Not Child", url="/other", is_current_path=False)

    assert parent.is_child(child) is True
    assert parent.is_child(not_child) is False
    assert child.is_child(parent) is False


def test_breadcrumb_item_is_parent():
    """Test is_parent method."""
    parent = BreadcrumbItem(text="Parent", url="/parent", is_current_path=False)
    child = BreadcrumbItem(text="Child", url="/parent/child", is_current_path=True)
    not_parent = BreadcrumbItem(text="Not Parent", url="/other", is_current_path=False)

    assert child.is_parent(parent) is True
    assert parent.is_parent(child) is False
    assert child.is_parent(not_parent) is False


def test_breadcrumb_item_make_parent():
    """Test make_parent method."""
    parent = BreadcrumbItem(text="Parent", url="/parent", is_current_path=False)
    child = BreadcrumbItem(text="Child", url="/parent/child", is_current_path=True)

    result = child.make_parent(parent)

    assert result == parent
    assert len(parent.children) == 1
    assert parent.children[0] == child


def test_breadcrumb_item_complex_hierarchy():
    """Test building a complex hierarchy of breadcrumb items."""
    root = BreadcrumbItem(text="Root", url="/", is_current_path=False)
    level1_a = BreadcrumbItem(text="Level 1A", url="/level1a", is_current_path=False)
    level1_b = BreadcrumbItem(text="Level 1B", url="/level1b", is_current_path=False)
    level2_a = BreadcrumbItem(
        text="Level 2A", url="/level1a/level2a", is_current_path=False
    )
    level2_b = BreadcrumbItem(
        text="Level 2B", url="/level1b/level2b", is_current_path=True
    )

    # Build hierarchy - need to add children to their parents, not all to root
    root.add(level1_a)
    root.add(level1_b)
    level1_a.add(level2_a)
    level1_b.add(level2_b)

    # Check structure
    assert len(root.children) == 2

    # Find level1_a
    level1_a_found = False
    for child in root.children:
        if child.url == "/level1a":
            level1_a_found = True
            assert child.text == "Level 1A"
            assert len(child.children) == 1
            assert child.children[0].text == "Level 2A"
            assert child.children[0].url == "/level1a/level2a"

    assert level1_a_found, "Level 1A not found in root's children"

    # Find level1_b
    level1_b_found = False
    for child in root.children:
        if child.url == "/level1b":
            level1_b_found = True
            assert child.text == "Level 1B"
            assert len(child.children) == 1
            assert child.children[0].text == "Level 2B"
            assert child.children[0].url == "/level1b/level2b"
            assert child.children[0].is_current_path is True

    assert level1_b_found, "Level 1B not found in root's children"
