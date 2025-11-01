# This file is copied from /system/main.py to /main.py on first run

import sys
import os
from badgeware import run, io
import machine
import gc
import powman

SKIP_CINEMATIC = powman.get_wake_reason() == powman.WAKE_WATCHDOG

running_app = None


def quit_to_launcher(pin):
    global running_app
    getattr(running_app, "on_exit", lambda: None)()
    # If we reset while boot is low, bad times
    while not pin.value():
        pass
    machine.reset()


if not SKIP_CINEMATIC:
    startup = __import__("/system/apps/startup")

    run(startup.update)

    if sys.path[0].startswith("/system/apps"):
        sys.path.pop(0)

    del startup

    gc.collect()

# --- Screensaver/auto-dim helper ---
from badgeware import screen, brushes, shapes

INACTIVITY_TIMEOUT_MS = 60000  # 60 seconds
last_activity_time = [io.ticks]  # Use list to allow modification in nested function
screensaver_active = [False]

def create_screensaver_wrapper(update_fn, app_module=None):
    """Wraps an update function with screensaver logic"""
    def wrapped_update():
        # Check if app wants to disable screensaver
        disable_screensaver = getattr(app_module, 'disable_screensaver', False) if app_module else False
        
        # Update inactivity timer on any button press (check if sets are non-empty)
        if len(io.pressed) > 0 or len(io.held) > 0:
            last_activity_time[0] = io.ticks
            if screensaver_active[0]:
                screensaver_active[0] = False
        
        # Call the original update function
        result = update_fn()
        
        # Apply screensaver if inactive for too long and app allows it
        if not disable_screensaver:
            time_since_activity = io.ticks - last_activity_time[0]
            if time_since_activity > INACTIVITY_TIMEOUT_MS:
                if not screensaver_active[0]:
                    screensaver_active[0] = True
                # Draw dim overlay
                screen.brush = brushes.color(0, 0, 0, 180)
                screen.draw(shapes.rectangle(0, 0, 160, 120))
        
        return result
    return wrapped_update

menu = __import__("/system/apps/menu")

app = run(create_screensaver_wrapper(menu.update, menu))

if sys.path[0].startswith("/system/apps"):
    sys.path.pop(0)

del menu

# make sure these can be re-imported by the app
del sys.modules["ui"]
del sys.modules["icon"]

gc.collect()

# Don't pass the b press into the app
while io.held:
    io.poll()

machine.Pin.board.BUTTON_HOME.irq(
    trigger=machine.Pin.IRQ_FALLING, handler=quit_to_launcher
)

sys.path.insert(0, app)
os.chdir(app)

running_app = __import__(app)

getattr(running_app, "init", lambda: None)()

# Reset inactivity timer when launching a new app
last_activity_time[0] = io.ticks
screensaver_active[0] = False

# Use the same screensaver wrapper for the running app
run(create_screensaver_wrapper(running_app.update, running_app))

# Unreachable, in theory!
machine.reset()

