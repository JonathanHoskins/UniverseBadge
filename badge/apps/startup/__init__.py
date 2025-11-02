"""Startup animation app with timed hold and fade-out.

Plays a sequence of frames, holds on a specific frame, and then fades out when
the user presses a button after the animation completes.
"""

import sys
import os

sys.path.insert(0, "/system/apps/startup")
os.chdir("/system/apps/startup")

from badgeware import io, screen, run, brushes, shapes, display

# animation settings
animation_duration = 3
fade_duration = 0.75
frame_count = 159
hold_frame = 113

# render the specified frame from the animation
current_frame = None
current_frame_filename = None

ticks_start = None

CLEAR = shapes.rectangle(0, 0, screen.width, screen.height)


def show_frame(i: int, alpha: int = 255) -> None:
    """Load and draw a specific intro frame with a fade alpha overlay."""
    # check if this frame needs loading
    global current_frame_filename
    filename = f"frames/intro_{i:05d}.png"
    screen.load_into(filename)

    screen.brush = brushes.color(0, 0, 0, 255 - alpha)
    screen.draw(CLEAR)

    # render the frame
    current_frame_filename = filename


button_pressed_at = None


def update() -> bool | None:
    """Main update: compute frame/alpha, render, and exit when done.

    Returns False to indicate the app should exit back to the launcher.
    """
    global button_pressed_at, ticks_start

    _ensure_start_time()
    time = _elapsed_seconds()

    # phase handling and frame calculation
    _maybe_mark_button_pressed(time)
    result = _compute_frame_and_alpha(time)
    if result is False:
        return False
    frame, alpha = result

    show_frame(frame, int(alpha))  # type: ignore[arg-type]
    return None


# --- Helper functions ---
def _ensure_start_time() -> None:
    """Initialize the start tick counter exactly once."""
    global ticks_start
    if ticks_start is None:
        ticks_start = io.ticks

def _elapsed_seconds() -> float:
    """Return elapsed time in seconds since app start."""
    return (io.ticks - ticks_start) / 1000

def _maybe_mark_button_pressed(time: float) -> None:
    """Latch the first button press after the animation has finished."""
    global button_pressed_at
    if time >= animation_duration and io.pressed and not button_pressed_at:
        button_pressed_at = time

def _compute_frame_and_alpha(time: float) -> tuple[int, float] | bool:
    """Compute current frame and alpha, or False to indicate exit.

    Returns a (frame, alpha) tuple during playback, or False once the fade-out
    has completed and the app should exit.
    """
    frame, alpha = hold_frame, 255
    if time < animation_duration:
        frame = round((time / animation_duration) * hold_frame)
        return (frame, alpha)

    if button_pressed_at:
        time_since_pressed = time - button_pressed_at
        if time_since_pressed < fade_duration:
            frame = round((time_since_pressed / fade_duration) * (frame_count - hold_frame)) + hold_frame
            alpha = int(255 - ((time_since_pressed / fade_duration) * 255))  # type: ignore[assignment]
            return (frame, alpha)
        else:
            _clear_and_exit()
            return False
    return (frame, alpha)

def _clear_and_exit() -> None:
    """Clear the screen and flush the display for a clean exit."""
    screen.brush = brushes.color(0, 0, 0)
    screen.draw(CLEAR)
    display.update()


if __name__ == "__main__":
    run(update)
