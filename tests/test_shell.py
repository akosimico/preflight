from gui.sidebar import NAVIGATION_ITEMS


def test_navigation_contains_required_views() -> None:
    assert NAVIGATION_ITEMS == (
        "Dashboard", "Projects", "Discovery", "Test Suite", "Scenarios", "Reports", "History", "Settings",
    )


def test_application_entry_point_is_importable() -> None:
    import app

    assert callable(app.main)
