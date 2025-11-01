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

menu = __import__("/system/apps/menu")

app = run(menu.update)

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

# --- Screensaver/auto-dim wrapper ---
from badgeware import screen, brushes, shapes

INACTIVITY_TIMEOUT_MS = 60000  # 60 seconds
last_activity_time = io.ticks
screensaver_active = False

def wrapped_update():
    global last_activity_time, screensaver_active
    
    # Check if app wants to disable screensaver
    disable_screensaver = getattr(running_app, 'disable_screensaver', False)
    
    # Update inactivity timer on any button press
    if io.pressed or io.held:
        last_activity_time = io.ticks
        if screensaver_active:
            screensaver_active = False
    
    # Call the app's update function
    result = running_app.update()
    
    # Apply screensaver if inactive for too long and app allows it
    if not disable_screensaver:
        time_since_activity = io.ticks - last_activity_time
        if time_since_activity > INACTIVITY_TIMEOUT_MS:
            if not screensaver_active:
                screensaver_active = True
            # Draw dim overlay
            screen.brush = brushes.color(0, 0, 0, 180)
            screen.draw(shapes.rectangle(0, 0, 160, 120))
    
    return result

run(wrapped_update)

# Unreachable, in theory!
machine.reset()

