import importlib
from conftest import prepare_app_import


def test_menu_pagination_bounds():
    prepare_app_import("menu")
    menu = importlib.import_module("badge.apps.menu")

    # Simulate some discovered apps
    menu.apps = [(f"app{i}", f"app{i}") for i in range(10)]  # 10 apps
    menu.current_page = 5  # Out of range

    menu._recalculate_total_pages()
    assert menu.total_pages >= 1

    # Ensure current page is clamped and icons reloaded safely
    menu._ensure_current_page_in_bounds()
    assert 0 <= menu.current_page < menu.total_pages


def test_menu_handle_app_launch_noop_when_no_press():
    prepare_app_import("menu")
    menu = importlib.import_module("badge.apps.menu")
    menu.apps = [("app0", "app0")]
    menu.current_page = 0
    menu.active = 0

    # No button pressed -> should return None
    # Ensure pressed set is empty
    from badgeware import io
    io.pressed.clear()
    assert menu._handle_app_launch() is None
