"""DVD logo bounce app with simple intro and play states.

Press A to start the logo bouncing, and B to return to the intro.
"""

import sys
import os

# ensure imports and working directory match how apps run on the badge
sys.path.insert(0, "/system/apps/dvd")
os.chdir("/system/apps/dvd")

from badgeware import screen, PixelFont, brushes, shapes, run, io
from dvd import DVDLogo

small_font = PixelFont.load("/system/assets/fonts/nope.ppf")
large_font = PixelFont.load("/system/assets/fonts/ziplock.ppf")

logo = None


class GameState:
    """Constants for app state."""
    INTRO = 1
    PLAYING = 2


state = GameState.INTRO


def update() -> None:
    """Main update loop: handle intro vs playing state and draw UI."""
    global state, logo
    _clear_background()
    if state == GameState.INTRO:
        _draw_intro()
        _handle_intro_input()
    elif state == GameState.PLAYING:
        _update_and_draw_playing()
        _draw_playing_hint()
        _handle_playing_input()


# --- Helper functions ---
def _clear_background() -> None:
    """Fill the screen with black."""
    screen.brush = brushes.color(0, 0, 0)
    screen.draw(shapes.rectangle(0, 0, 160, 120))

def _draw_intro() -> None:
    """Draw title and blinking start prompt."""
    screen.font = large_font
    w, _ = screen.measure_text("DVD BOUNCE")
    screen.brush = brushes.color(255, 255, 255)
    screen.text("DVD BOUNCE", 80 - (w / 2), 30)
    screen.font = small_font
    if int(io.ticks / 500) % 2:
        w, _ = screen.measure_text("Press A to start")
        screen.text("Press A to start", 80 - (w / 2), 80)

def _handle_intro_input() -> None:
    """Start the logo animation when A is pressed."""
    global state, logo
    if io.BUTTON_A in io.pressed:
        logo = DVDLogo()
        state = GameState.PLAYING

def _update_and_draw_playing() -> None:
    """Advance the logo animation and draw it."""
    logo.update()
    logo.draw()

def _draw_playing_hint() -> None:
    """Blink a hint to return to intro."""
    screen.font = small_font
    if int(io.ticks / 500) % 2:
        w, _ = screen.measure_text("Press B to return")
        screen.brush = brushes.color(255, 255, 255)
        screen.text("Press B to return", 80 - (w / 2), 108)

def _handle_playing_input() -> None:
    """Return to intro when B is pressed."""
    global state
    if io.BUTTON_B in io.pressed:
        state = GameState.INTRO


if __name__ == "__main__":
    run(update)
