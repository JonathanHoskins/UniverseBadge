"""
Desktop runner for badge apps using the test stubs.

- Uses tests/_stubs/badgeware to emulate the badgeware API
- Calls app.update() in a loop
- Maps keyboard keys to io.BUTTON_* (A/B/C and arrows)
- Prints key UI state each second (status text, errors, connectivity)

Windows-only interactive keys use msvcrt.getch(). Press ESC to quit.

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

# Now we can import the stubbed badgeware
from badgeware import io  # type: ignore

# Default app
APP_MODULE = sys.argv[1] if len(sys.argv) > 1 else "badge.apps.hc911"


def _load_app(modname: str) -> ModuleType:
    mod = importlib.import_module(modname)
    if not hasattr(mod, "update"):
        raise RuntimeError(f"Module {modname} has no update()")
    return mod


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
            # left/right are currently unused by most apps
    return True


def _print_state(mod: ModuleType):
    # Try to print common fields if present
    fields = []
    for name in ("status_text", "error_msg", "wifi_enabled", "fetching", "active_incidents", "daily_total", "yearly_total"):
        if hasattr(mod, name):
            fields.append(f"{name}={getattr(mod, name)!r}")
    if fields:
        print("[state] ", ", ".join(fields))


def main():
    mod = _load_app(APP_MODULE)

    print(f"Running {APP_MODULE}. Press ESC to quit. Keys: A/B/C, arrows.")
    last_print = 0.0
    try:
        while True:
            # Update ticks
            io.ticks += 33

            # Handle keys
            if not _windows_key_input():
                break

            # Run one update frame
            mod.update()

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
