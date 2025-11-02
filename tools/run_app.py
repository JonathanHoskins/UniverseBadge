"""
Desktop runner for badge apps using the test stubs, with a simple visual screen and interactive buttons.

- Uses tests/_stubs/badgeware to emulate the badgeware API
- Provides a Tkinter window to visualize drawing (text and simple shapes)
- Calls app.update() in a loop
- Maps keyboard keys to io.BUTTON_* (A/B/C and arrows)
- Adds clickable on-screen buttons for A, B, C, Up, Down
- Prints key UI state each second (status text, errors, connectivity)

Press ESC in the console to quit (or close the window).

Usage:
    python tools/run_app.py badge.apps.hc911
    python tools/run_app.py badge.apps.wifi
"""
from __future__ import annotations

import importlib
import sys
import time
from types import ModuleType

# Ensure repo root and test stubs are importable
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
STUBS = REPO / "tests" / "_stubs"
if str(STUBS) not in sys.path:
    sys.path.insert(0, str(STUBS))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Now we can import the stubbed badgeware (module object)
import badgeware as bw  # type: ignore
io = bw.io  # shorthand

# Default app
APP_MODULE = sys.argv[1] if len(sys.argv) > 1 else "badge.apps.hc911"


def _load_app(modname: str) -> ModuleType:
    mod = importlib.import_module(modname)
    if not hasattr(mod, "update"):
        raise RuntimeError(f"Module {modname} has no update()")
    return mod


# ---------------- Visual screen (Tkinter) -----------------

SCALE = 3  # scale drawing for visibility
WIDTH, HEIGHT = 160, 120
pressed_queue: set[int] = set()
held_keys: set[int] = set()


def _to_hex(color):
    # Accept (r,g,b[,a]) tuple from brushes.color
    if not isinstance(color, (tuple, list)):
        return "#ffffff"
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    return f"#{r:02x}{g:02x}{b:02x}"


try:
    import tkinter as tk  # type: ignore
except Exception:  # pragma: no cover - optional
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
        return None

    def clear(self):
        if tk is None:
            return None
        # fill with current brush color
        self._canvas.delete("all")
        self._canvas.create_rectangle(0, 0, self._sx(self.width), self._sy(self.height), outline=_to_hex(self.brush), fill=_to_hex(self.brush))
        return None

    def text(self, text: str, x: int, y: int):
        if tk is None:
            return None
        self._canvas.create_text(self._sx(x), self._sy(y), anchor="nw", text=str(text), fill=_to_hex(self.brush), font=("TkFixedFont", 8 * self._scale // 2))
        return None

    def measure_text(self, text: str):
        # simple fixed-size metrics (unscaled units)
        return (max(0, len(text)) * 6, 10)

    def blit(self, _img, x: int, y: int):
        # draw a placeholder rectangle for images
        self._canvas.create_rectangle(self._sx(x), self._sy(y), self._sx(x + 16), self._sy(y + 16), outline=_to_hex(self.brush))
        return None

    def scale_blit(self, _img, x: int, y: int, w: int, h: int):
        self._canvas.create_rectangle(self._sx(x), self._sy(y), self._sx(x + w), self._sy(y + h), outline=_to_hex(self.brush))
        return None

    def window(self, x, y, w, h):
        # Return a view into the same canvas with offset
        return VisualScreen(self._canvas, self._origin_x + x, self._origin_y + y, w, h, self._scale)

    def load_into(self, _filename: str):
        return None


def _windows_key_input():
    """Non-blocking key reader for Windows using msvcrt.

    Maps keys:
      - a => BUTTON_A, b => BUTTON_B, c => BUTTON_C
      - arrows => BUTTON_UP/DOWN/LEFT/RIGHT
      - esc => quit
    """
    try:
        import msvcrt  # type: ignore
    except Exception:
        return True  # keep running, no key support

    # Clear previous pressed set each frame; keep held if needed
    io.pressed.clear()

    while msvcrt.kbhit():
        ch = msvcrt.getch()
        if ch in (b"\x1b",):  # ESC
            return False
        if ch in (b"a", b"A"):
            io.pressed.add(io.BUTTON_A)
        elif ch in (b"b", b"B"):
            io.pressed.add(io.BUTTON_B)
        elif ch in (b"c", b"C"):
            io.pressed.add(io.BUTTON_C)
        elif ch == b"\xe0":  # special key prefix
            ch2 = msvcrt.getch()
            if ch2 == b"H":  # up
                io.pressed.add(io.BUTTON_UP)
            elif ch2 == b"P":  # down
                io.pressed.add(io.BUTTON_DOWN)
            elif ch2 == b"K":  # left
                io.pressed.add(getattr(io, "BUTTON_LEFT", io.BUTTON_UP))
            elif ch2 == b"M":  # right
                io.pressed.add(getattr(io, "BUTTON_RIGHT", io.BUTTON_DOWN))
    return True


def _tk_bind_keys(root):
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


def _tk_controls(root):
    if tk is None:
        return None

    frm = tk.Frame(root)
    frm.pack(fill="x", pady=4)

    def press(btn):
        pressed_queue.add(btn)

    # Hold toggles
    hold_up_var = tk.BooleanVar(value=False)
    hold_down_var = tk.BooleanVar(value=False)

    # Layout: [Left] [Up] [Down] [Right]   [A] [B] [C]   [Hold Up] [Hold Down]
    tk.Button(frm, text="Left", width=6, command=lambda: press(getattr(io, 'BUTTON_LEFT', io.BUTTON_UP))).pack(side="left", padx=4)
    tk.Button(frm, text="Up", width=6, command=lambda: press(io.BUTTON_UP)).pack(side="left", padx=4)
    tk.Button(frm, text="Down", width=6, command=lambda: press(io.BUTTON_DOWN)).pack(side="left", padx=4)
    tk.Button(frm, text="Right", width=6, command=lambda: press(getattr(io, 'BUTTON_RIGHT', io.BUTTON_DOWN))).pack(side="left", padx=4)

    tk.Button(frm, text="A", width=6, command=lambda: press(io.BUTTON_A)).pack(side="left", padx=12)
    tk.Button(frm, text="B", width=6, command=lambda: press(io.BUTTON_B)).pack(side="left", padx=4)
    tk.Button(frm, text="C", width=6, command=lambda: press(io.BUTTON_C)).pack(side="left", padx=4)

    tk.Checkbutton(frm, text="Hold Up", variable=hold_up_var).pack(side="left", padx=12)
    tk.Checkbutton(frm, text="Hold Down", variable=hold_down_var).pack(side="left", padx=4)

    return frm, hold_up_var, hold_down_var


def _print_state(mod: ModuleType):
    # Try to print common fields if present
    fields = []
    for name in ("status_text", "error_msg", "wifi_enabled", "fetching", "active_incidents", "daily_total", "yearly_total"):
        if hasattr(mod, name):
            fields.append(f"{name}={getattr(mod, name)!r}")
    if fields:
        print("[state] ", ", ".join(fields))


def main():
    # Set up Tk window if available
    root = None
    canvas = None
    if tk is not None:
        root = tk.Tk()
        root.title(f"UniverseBadge Emulator - {APP_MODULE}")
        canvas = tk.Canvas(root, width=WIDTH * SCALE, height=HEIGHT * SCALE, bg="#0d1117")
        canvas.pack()
        _tk_bind_keys(root)
        frm, hold_up_var, hold_down_var = _tk_controls(root)

    # Patch badgeware screen & shapes with visual versions if we have a canvas
    if canvas is not None:
        bw.screen = VisualScreen(canvas)
        bw.shapes = VisualShapes()

    mod = _load_app(APP_MODULE)

    print(f"Running {APP_MODULE}. Press ESC to quit. Keys: A/B/C, arrows.")
    last_print = 0.0
    try:
        while True:
            # Update ticks
            io.ticks += 33

            # Handle keys
            io.pressed.clear()
            # Prefer Tk bindings if available; otherwise use console keys
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
                # Transfer queued button presses for this frame
                if pressed_queue:
                    io.pressed.update(pressed_queue)
                    pressed_queue.clear()
                # Apply held keys as repeated presses
                if held_keys:
                    io.held = set(held_keys)
                    io.pressed.update(held_keys)
                else:
                    io.held = set()
            else:
                if not _windows_key_input():
                    break

            # Run one update frame
            mod.update()

            # Update the window
            if root is not None:
                root.update_idletasks()
                root.update()

            # Print state once per second
            now = time.time()
            if now - last_print > 1.0:
                last_print = now
                _print_state(mod)

            # Frame delay ~30 FPS
            time.sleep(0.033)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
