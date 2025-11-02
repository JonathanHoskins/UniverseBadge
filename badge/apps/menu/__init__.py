"""Badge app launcher menu.

Auto-discovers installed apps under /system/apps, paginates their icons, and
launches the selected app. The update flow is decomposed into helper functions
for pagination, input handling, and drawing.
"""
import os
os.chdir("/system/apps/menu")
import math
from badgeware import screen, PixelFont, Image, SpriteSheet, is_dir, file_exists, shapes, brushes, io, run
from icon import Icon
import ui

mona = SpriteSheet("/system/assets/mona-sprites/mona-default.png", 11, 1)
screen.font = PixelFont.load("/system/assets/fonts/ark.ppf")
# screen.antialias = Image.X2

# Auto-discover apps with __init__.py
apps = []
try:
    for entry in os.listdir("/system/apps"):
        app_path = f"/system/apps/{entry}"
        if is_dir(app_path):
            has_init = file_exists(f"{app_path}/__init__.py")
            if has_init:
                # Skip menu and startup apps
                if entry not in ("menu", "startup"):
                    # Use directory name as display name
                    apps.append((entry, entry))
except Exception as e:
    print(f"Error discovering apps: {e}")

# Pagination constants
APPS_PER_PAGE = 6
current_page = 0
# total_pages will be recalculated dynamically in update() to handle apps
total_pages = 1

# find installed apps and create icons for current page
def load_page_icons(page: int):
    icons = []
    start_idx = page * APPS_PER_PAGE
    end_idx = min(start_idx + APPS_PER_PAGE, len(apps))
    
    for i in range(start_idx, end_idx):
        app = apps[i]
        name, path = app[0], app[1]
        
        if is_dir(f"/system/apps/{path}"):
            icon_idx = i - start_idx
            x = icon_idx % 3
            y = math.floor(icon_idx / 3)
            pos = (x * 48 + 33, y * 48 + 42)
            try:
                # Try to load app-specific icon, fall back to default
                icon_path = f"/system/apps/{path}/icon.png"
                if not file_exists(icon_path):
                    icon_path = "/system/apps/menu/default_icon.png"
                sprite = Image.load(icon_path)
                icons.append(Icon(pos, name, icon_idx % APPS_PER_PAGE, sprite))
            except Exception as e:
                print(f"Error loading icon for {path}: {e}")
    return icons

icons = load_page_icons(current_page)

active = 0

MAX_ALPHA = 255
alpha = 30


def update() -> str | None:

    global active, icons, alpha, current_page, total_pages

    _recalculate_total_pages()
    _ensure_current_page_in_bounds()
    _handle_input()
    _handle_wrapping_and_pagination()
    app_path = _handle_app_launch()
    if app_path:
        return app_path

    _draw_menu_ui()
    _draw_icons_and_labels()
    _draw_page_indicator()
    _draw_fade_in()

    return None


# --- Helper Functions ---
def _recalculate_total_pages() -> None:
    global total_pages
    total_pages = max(1, math.ceil(len(apps) / APPS_PER_PAGE))

def _ensure_current_page_in_bounds() -> None:
    global current_page, total_pages, icons
    if current_page >= total_pages:
        current_page = total_pages - 1
        icons = load_page_icons(current_page)

def _handle_input() -> None:
    global active
    if io.BUTTON_C in io.pressed:
        active += 1
    if io.BUTTON_A in io.pressed:
        active -= 1
    if io.BUTTON_UP in io.pressed:
        active -= 3
    if io.BUTTON_DOWN in io.pressed:
        active += 3

def _handle_wrapping_and_pagination() -> None:
    global active, current_page, total_pages, icons
    if active >= len(icons):
        if current_page < total_pages - 1:
            current_page += 1
            icons = load_page_icons(current_page)
            active = 0
        else:
            active = 0
    elif active < 0:
        if current_page > 0:
            current_page -= 1
            icons = load_page_icons(current_page)
            active = len(icons) - 1
        else:
            active = len(icons) - 1

def _handle_app_launch() -> str | None:
    if io.BUTTON_B in io.pressed:
        app_idx = current_page * APPS_PER_PAGE + active
        if app_idx < len(apps):
            app_path = f"/system/apps/{apps[app_idx][1]}"
            try:
                if is_dir(app_path) and file_exists(f"{app_path}/__init__.py"):
                    return app_path
                else:
                    print(f"Error: App {apps[app_idx][1]} not found or missing __init__.py")
            except Exception as e:
                print(f"Error launching app {apps[app_idx][1]}: {e}")
    return None

def _draw_menu_ui() -> None:
    ui.draw_background()
    ui.draw_header()

def _draw_icons_and_labels() -> None:
    for i in range(len(icons)):
        icons[i].activate(active == i)
        icons[i].draw()
    if Icon.active_icon:
        label = f"{Icon.active_icon.name}"
        w, _ = screen.measure_text(label)
        screen.brush = brushes.color(211, 250, 55)
        screen.draw(shapes.rounded_rectangle(80 - (w / 2) - 4, 100, w + 8, 15, 4))
        screen.brush = brushes.color(0, 0, 0, 150)
        screen.text(label, 80 - (w / 2), 101)

def _draw_page_indicator() -> None:
    if total_pages > 1:
        page_label = f"{current_page + 1}/{total_pages}"
        w, _ = screen.measure_text(page_label)
        screen.brush = brushes.color(211, 250, 55, 150)
        screen.text(page_label, 160 - w - 5, 112)

def _draw_fade_in() -> None:
    global alpha
    if alpha <= MAX_ALPHA:
        screen.brush = brushes.color(0, 0, 0, 255 - alpha)
        screen.clear()
        alpha += 30

if __name__ == "__main__":
    run(update)
