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
    INTRO = 1
    PLAYING = 2


state = GameState.INTRO


def update():
    global state, logo

    # clear background
    screen.brush = brushes.color(0, 0, 0)
    screen.draw(shapes.rectangle(0, 0, 160, 120))

    if state == GameState.INTRO:
        screen.font = large_font
        w, _ = screen.measure_text("DVD BOUNCE")
        screen.brush = brushes.color(255, 255, 255)
        screen.text("DVD BOUNCE", 80 - (w / 2), 30)

        screen.font = small_font
        if int(io.ticks / 500) % 2:
            w, _ = screen.measure_text("Press A to start")
            screen.text("Press A to start", 80 - (w / 2), 80)

        if io.BUTTON_A in io.pressed:
            logo = DVDLogo()
            state = GameState.PLAYING

    elif state == GameState.PLAYING:
        # update and draw the bouncing logo
        logo.update()
        logo.draw()

        # show simple instructions to return to intro
        screen.font = small_font
        if int(io.ticks / 500) % 2:
            w, _ = screen.measure_text("Press B to return")
            screen.text("Press B to return", 80 - (w / 2), 108)

        if io.BUTTON_B in io.pressed:
            state = GameState.INTRO


if __name__ == "__main__":
    run(update)
