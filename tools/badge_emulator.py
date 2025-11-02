"""
Full UniverseBadge Desktop Emulator

Emulates the complete badge experience with:
- App menu system (mimics badge/main.py)
- Visual 160x120 screen with Tkinter
- Interactive buttons (A/B/C, Up/Down, Left/Right)
- App switching and navigation
- Persistent state across app switches

Usage:
    python tools/badge_emulator.py
"""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path
from types import ModuleType

# Ensure repo root and test stubs are importable
REPO = Path(__file__).resolve().parents[1]
STUBS = REPO / "tests" / "_stubs"
if str(STUBS) not in sys.path:
    sys.path.insert(0, str(STUBS))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Import the stubbed badgeware
import badgeware as bw  # type: ignore
io = bw.io

# Display constants
SCALE = 4  # scale drawing for better visibility
WIDTH, HEIGHT = 160, 120
pressed_queue: set[int] = set()
held_keys: set[int] = set()

# Available apps (mimics menu structure)
APPS = [
    ("badge", "Badge Info"),
    ("hello", "Hello World"),
    ("life", "Game of Life"),
    ("snake", "Snake"),
    ("flappy", "Flappy Mona"),
    ("monapet", "Mona Pet"),
    ("sketch", "Sketch Pad"),
    ("quest", "Quest Game"),
    ("commits", "GitHub Commits"),
    ("gallery", "Image Gallery"),
    ("wifi", "WiFi Diagnostics"),
    ("hc911", "HC 911 Incidents"),
]

# State
current_app_index = 0
current_app_module = None
in_menu = True


def _to_hex(color):
    """Convert RGB tuple to hex color string."""
    if not isinstance(color, (tuple, list)):
        return "#ffffff"
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    return f"#{r:02x}{g:02x}{b:02x}"


try:
    import tkinter as tk  # type: ignore
except Exception:
    tk = None


class _VisualShape:
    def __init__(self, kind: str, *args):
        self.kind = kind
        self.args = args


class VisualShapes:
    def circle(self, x: int, y: int, r: int):
        return _VisualShape("circle", x, y, r)

    def rectangle(self, x: int, y: int, w: int, h: int):
        return _VisualShape("rectangle", x, y, w, h)

    def rounded_rectangle(self, x: int, y: int, w: int, h: int, r: int = 5):
        return _VisualShape("rounded_rectangle", x, y, w, h, r)


class VisualScreen:
    def __init__(self, canvas, x=0, y=0, w=WIDTH, h=HEIGHT, scale=SCALE):
        self.width = w
        self.height = h
        self._canvas = canvas
        self._origin_x = x
        self._origin_y = y
        self._scale = scale
        self.brush = bw.brushes.color(255, 255, 255)
        self.font = None

    def _sx(self, x):
        return (self._origin_x + x) * self._scale

    def _sy(self, y):
        return (self._origin_y + y) * self._scale

    def draw(self, shape: _VisualShape):
        if tk is None or not isinstance(shape, _VisualShape):
            return None
        color = _to_hex(self.brush)
        if shape.kind == "circle":
            x, y, r = shape.args
            x0, y0 = self._sx(x - r), self._sy(y - r)
            x1, y1 = self._sx(x + r), self._sy(y + r)
            self._canvas.create_oval(x0, y0, x1, y1, outline=color, fill=color)
        elif shape.kind == "rectangle":
            x, y, w, h = shape.args
            self._canvas.create_rectangle(self._sx(x), self._sy(y), self._sx(x + w), self._sy(y + h), outline=color, fill=color)
        elif shape.kind == "rounded_rectangle":
            x, y, w, h, r = shape.args
            # Simple approximation with rectangles
            self._canvas.create_rectangle(self._sx(x), self._sy(y), self._sx(x + w), self._sy(y + h), outline=color, fill=color)
        return None

    def clear(self):
        if tk is None:
            return None
        self._canvas.delete("all")
        self._canvas.create_rectangle(0, 0, self._sx(self.width), self._sy(self.height), outline=_to_hex(self.brush), fill=_to_hex(self.brush))
        return None

    def text(self, text: str, x: int, y: int):
        if tk is None:
            return None
        self._canvas.create_text(self._sx(x), self._sy(y), anchor="nw", text=str(text), fill=_to_hex(self.brush), font=("TkFixedFont", 10))
        return None

    def measure_text(self, text: str):
        return (max(0, len(text)) * 6, 10)

    def blit(self, _img, x: int, y: int):
        self._canvas.create_rectangle(self._sx(x), self._sy(y), self._sx(x + 16), self._sy(y + 16), outline=_to_hex(self.brush))
        return None

    def scale_blit(self, _img, x: int, y: int, w: int, h: int):
        self._canvas.create_rectangle(self._sx(x), self._sy(y), self._sx(x + w), self._sy(y + h), outline=_to_hex(self.brush))
        return None

    def window(self, x, y, w, h):
        return VisualScreen(self._canvas, self._origin_x + x, self._origin_y + y, w, h, self._scale)

    def load_into(self, _filename: str):
        return None


def _load_app(app_name: str) -> ModuleType | None:
    """Load an app module by name."""
    try:
        mod = importlib.import_module(f"badge.apps.{app_name}")
        if not hasattr(mod, "update"):
            return None
        return mod
    except Exception as e:
        print(f"Failed to load app {app_name}: {e}")
        return None


def _draw_menu():
    """Draw the app selection menu."""
    bw.screen.brush = bw.brushes.color(13, 17, 23)
    bw.screen.clear()
    
    bw.screen.brush = bw.brushes.color(201, 209, 217)
    bw.screen.text("UniverseBadge Menu", 5, 5)
    
    # Draw app list
    y = 25
    for i, (app_name, app_title) in enumerate(APPS):
        if i == current_app_index:
            # Highlight selected
            bw.screen.brush = bw.brushes.color(46, 160, 67)
            bw.screen.text(f"> {app_title}", 5, y)
        else:
            bw.screen.brush = bw.brushes.color(88, 96, 105)
            bw.screen.text(f"  {app_title}", 5, y)
        y += 10
        if y > 105:
            break
    
    # Instructions
    bw.screen.brush = bw.brushes.color(255, 191, 0)
    bw.screen.text("UP/DOWN:Select A:Launch", 5, 108)


def _tk_bind_keys(root):
    """Bind keyboard keys to button inputs."""
    if tk is None:
        return

    def _press(btn):
        pressed_queue.add(btn)

    def _hold(btn):
        held_keys.add(btn)

    def _release(btn):
        held_keys.discard(btn)

    # Key bindings for A/B/C (press only)
    root.bind("<KeyPress-a>", lambda e: _press(io.BUTTON_A))
    root.bind("<KeyPress-A>", lambda e: _press(io.BUTTON_A))
    root.bind("<KeyPress-b>", lambda e: _press(io.BUTTON_B))
    root.bind("<KeyPress-B>", lambda e: _press(io.BUTTON_B))
    root.bind("<KeyPress-c>", lambda e: _press(io.BUTTON_C))
    root.bind("<KeyPress-C>", lambda e: _press(io.BUTTON_C))

    # Arrow keys (hold + repeat)
    root.bind("<KeyPress-Up>", lambda e: _hold(io.BUTTON_UP))
    root.bind("<KeyRelease-Up>", lambda e: _release(io.BUTTON_UP))
    root.bind("<KeyPress-Down>", lambda e: _hold(io.BUTTON_DOWN))
    root.bind("<KeyRelease-Down>", lambda e: _release(io.BUTTON_DOWN))
    root.bind("<KeyPress-Left>", lambda e: _hold(getattr(io, 'BUTTON_LEFT', io.BUTTON_UP)))
    root.bind("<KeyRelease-Left>", lambda e: _release(getattr(io, 'BUTTON_LEFT', io.BUTTON_UP)))
    root.bind("<KeyPress-Right>", lambda e: _hold(getattr(io, 'BUTTON_RIGHT', io.BUTTON_DOWN)))
    root.bind("<KeyRelease-Right>", lambda e: _release(getattr(io, 'BUTTON_RIGHT', io.BUTTON_DOWN)))

    # Escape to return to menu
    root.bind("<Escape>", lambda e: _press(io.BUTTON_B))


def _tk_controls(root):
    """Create on-screen control buttons."""
    if tk is None:
        return None, None, None, None

    frm = tk.Frame(root, bg="#0d1117")
    frm.pack(fill="x", pady=8)

    def press(btn):
        pressed_queue.add(btn)

    # Hold toggles
    hold_up_var = tk.BooleanVar(value=False)
    hold_down_var = tk.BooleanVar(value=False)

    # Info label
    info_label = tk.Label(frm, text="Badge Menu", font=("Arial", 12, "bold"), bg="#0d1117", fg="#c9d1d9")
    info_label.pack(pady=4)

    # Control buttons frame
    btn_frm = tk.Frame(frm, bg="#0d1117")
    btn_frm.pack()

    # Layout: [Left] [Up] [Down] [Right]   [A] [B] [C]
    tk.Button(btn_frm, text="←", width=4, height=2, bg="#30363d", fg="#c9d1d9", command=lambda: press(getattr(io, 'BUTTON_LEFT', io.BUTTON_UP))).pack(side="left", padx=2)
    tk.Button(btn_frm, text="↑", width=4, height=2, bg="#30363d", fg="#c9d1d9", command=lambda: press(io.BUTTON_UP)).pack(side="left", padx=2)
    tk.Button(btn_frm, text="↓", width=4, height=2, bg="#30363d", fg="#c9d1d9", command=lambda: press(io.BUTTON_DOWN)).pack(side="left", padx=2)
    tk.Button(btn_frm, text="→", width=4, height=2, bg="#30363d", fg="#c9d1d9", command=lambda: press(getattr(io, 'BUTTON_RIGHT', io.BUTTON_DOWN))).pack(side="left", padx=2)

    tk.Label(btn_frm, text="  ", bg="#0d1117").pack(side="left")  # Spacer

    tk.Button(btn_frm, text="A", width=4, height=2, bg="#2ea043", fg="white", font=("Arial", 12, "bold"), command=lambda: press(io.BUTTON_A)).pack(side="left", padx=2)
    tk.Button(btn_frm, text="B", width=4, height=2, bg="#f85149", fg="white", font=("Arial", 12, "bold"), command=lambda: press(io.BUTTON_B)).pack(side="left", padx=2)
    tk.Button(btn_frm, text="C", width=4, height=2, bg="#ffbf00", fg="white", font=("Arial", 12, "bold"), command=lambda: press(io.BUTTON_C)).pack(side="left", padx=2)

    # Hold toggles
    check_frm = tk.Frame(frm, bg="#0d1117")
    check_frm.pack(pady=4)
    tk.Checkbutton(check_frm, text="Hold Up", variable=hold_up_var, bg="#0d1117", fg="#c9d1d9", selectcolor="#30363d").pack(side="left", padx=8)
    tk.Checkbutton(check_frm, text="Hold Down", variable=hold_down_var, bg="#0d1117", fg="#c9d1d9", selectcolor="#30363d").pack(side="left", padx=8)

    return info_label, hold_up_var, hold_down_var


def main():
    global current_app_index, current_app_module, in_menu

    # Set up Tk window
    root = None
    canvas = None
    info_label = None
    hold_up_var = None
    hold_down_var = None

    if tk is not None:
        root = tk.Tk()
        root.title("UniverseBadge Desktop Emulator")
        root.configure(bg="#0d1117")
        canvas = tk.Canvas(root, width=WIDTH * SCALE, height=HEIGHT * SCALE, bg="#0d1117", highlightthickness=0)
        canvas.pack(pady=8)
        _tk_bind_keys(root)
        info_label, hold_up_var, hold_down_var = _tk_controls(root)

    # Patch badgeware screen & shapes
    if canvas is not None:
        bw.screen = VisualScreen(canvas)
        bw.shapes = VisualShapes()

    print("UniverseBadge Desktop Emulator")
    print("Press ESC or B to return to menu from any app")
    print("Close window or Ctrl+C to quit")

    last_print = 0.0

    try:
        while True:
            # Update ticks
            io.ticks += 33

            # Handle input
            io.pressed.clear()
            if root is not None:
                # Update held from toggles
                try:
                    if hold_up_var and hold_up_var.get():
                        held_keys.add(io.BUTTON_UP)
                    else:
                        held_keys.discard(io.BUTTON_UP)
                    if hold_down_var and hold_down_var.get():
                        held_keys.add(io.BUTTON_DOWN)
                    else:
                        held_keys.discard(io.BUTTON_DOWN)
                except Exception:
                    pass

                # Transfer queued button presses
                if pressed_queue:
                    io.pressed.update(pressed_queue)
                    pressed_queue.clear()

                # Apply held keys
                if held_keys:
                    io.held = set(held_keys)
                    io.pressed.update(held_keys)
                else:
                    io.held = set()

            # Menu or app logic
            if in_menu:
                # Handle menu navigation
                if io.BUTTON_UP in io.pressed:
                    current_app_index = (current_app_index - 1) % len(APPS)
                if io.BUTTON_DOWN in io.pressed:
                    current_app_index = (current_app_index + 1) % len(APPS)
                if io.BUTTON_A in io.pressed:
                    # Launch app
                    app_name, app_title = APPS[current_app_index]
                    current_app_module = _load_app(app_name)
                    if current_app_module:
                        in_menu = False
                        if info_label:
                            info_label.config(text=f"App: {app_title} (B:Menu)")
                        print(f"Launched: {app_title}")
                    else:
                        print(f"Failed to load: {app_title}")
                
                # Draw menu
                _draw_menu()
            else:
                # Run current app
                if io.BUTTON_B in io.pressed:
                    # Return to menu
                    in_menu = True
                    current_app_module = None
                    if info_label:
                        info_label.config(text="Badge Menu")
                    print("Returned to menu")
                elif current_app_module:
                    try:
                        result = current_app_module.update()
                        # If app returns non-None, it might signal exit
                        if result is not None and hasattr(result, '__iter__'):
                            # Some apps return (next_app, params) - just go to menu
                            in_menu = True
                            current_app_module = None
                            if info_label:
                                info_label.config(text="Badge Menu")
                    except Exception as e:
                        print(f"App error: {e}")
                        # Don't crash, just show error
                        bw.screen.brush = bw.brushes.color(248, 81, 73)
                        bw.screen.text(f"Error: {str(e)[:30]}", 5, 50)

            # Update window
            if root is not None:
                root.update_idletasks()
                root.update()

            # Print state occasionally
            now = time.time()
            if now - last_print > 5.0:
                last_print = now
                if in_menu:
                    print(f"[menu] Selected: {APPS[current_app_index][1]}")
                else:
                    print(f"[app] Running: {APPS[current_app_index][1]}")

            # Frame delay ~30 FPS
            time.sleep(0.033)

    except KeyboardInterrupt:
        print("\nExiting...")
    except tk.TclError:
        print("\nWindow closed")


if __name__ == "__main__":
    main()
