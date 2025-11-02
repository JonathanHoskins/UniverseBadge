"""Flappy Mona game.

This app implements a side-scrolling game inspired by Flappy Bird using
badgeware primitives. The update loop is decomposed into small helpers for
intro, gameplay, and game-over states. Fonts are sourced from shared constants.
"""
import sys
import os

sys.path.insert(0, "/system/apps/flappy")
os.chdir("/system/apps/flappy")

from badgeware import screen, Image, PixelFont, SpriteSheet, io, brushes, shapes, run
from mona import Mona
from obstacle import Obstacle

background = Image.load("assets/background.png")
grass = Image.load("assets/grass.png")
cloud = Image.load("assets/cloud.png")
large_font = PixelFont.load("/system/assets/fonts/ziplock.ppf")
small_font = PixelFont.load("/system/assets/fonts/nope.ppf")
ghost = SpriteSheet("/system/assets/mona-sprites/mona-dead.png", 7, 1).animation()
mona = None


class GameState:
    INTRO = 1
    PLAYING = 2
    GAME_OVER = 3


state = GameState.INTRO


def update():
    """Main update loop that dispatches per-state handlers."""
    draw_background()

    if state == GameState.INTRO:
        intro()

    if state == GameState.PLAYING:
        play()

    if state == GameState.GAME_OVER:
        game_over()


# handle the intro screen of the game, shows the game title and a message to
# tell the player how to start the game


def intro():
    """Render intro UI and transition to PLAYING when A is pressed."""
    global state, mona
    _draw_intro_ui()
    if _should_start_game():
        state = GameState.PLAYING
        Obstacle.obstacles = []
        Obstacle.next_spawn_time = io.ticks + 500
        mona = Mona()

# handle the main game loop and user input. each tick we'll update the game
# state (read button input, move mona, create new obstacles, etc..) then
# draw the background and sprites


def play():
    """Advance gameplay: input, physics, spawning, draw; detect game over."""
    global state
    _handle_play_input()
    _update_player()
    _spawn_obstacles_if_needed()
    _update_and_draw_obstacles()
    _draw_player_and_score()
    if _is_game_over():
        state = GameState.GAME_OVER

# handle the GAME OVER screen. show the player what score they achieved and
# provide instructions for how to start again


def game_over():
    """Render game-over UI and return to intro when A is pressed."""
    global state
    _draw_game_over_ui()
    if _should_restart():
        state = GameState.INTRO


# draw the scrolling background with parallax layers
background_offset = 0


def draw_background():
    """Draw parallax sky, clouds, and grass with a scrolling offset."""
    global background_offset
    _clear_sky()
    _update_background_offset()
    _draw_parallax_layers()

# a couple of helper functions for formatting text


def shadow_text(text, x, y):
    """Draw text with a subtle drop shadow at the given coordinates."""
    screen.brush = brushes.color(20, 40, 60, 100)
    screen.text(text, x + 1, y + 1)
    screen.brush = brushes.color(255, 255, 255)
    screen.text(text, x, y)


def center_text(text, y):
    """Horizontally center text at the provided y position."""
    w, _ = screen.measure_text(text)
    shadow_text(text, 80 - (w / 2), y)


# --- Helper functions ---
def _draw_intro_ui():
    """Intro screen title and blinking prompt."""
    screen.font = large_font
    center_text("FLAPPY MONA", 38)
    if int(io.ticks / 500) % 2:
        screen.font = small_font
        center_text("Press A to start", 70)

def _should_start_game():
    """Return True if A was pressed to start the game."""
    return io.BUTTON_A in io.pressed

def _handle_play_input():
    """Handle in-game input (jump on A) while alive."""
    if mona and not mona.is_dead() and io.BUTTON_A in io.pressed:
        mona.jump()

def _update_player():
    """Advance player physics/animation one tick."""
    if mona:
        mona.update()

def _spawn_obstacles_if_needed():
    """Spawn obstacles on a schedule while player is alive."""
    if mona and not mona.is_dead() and Obstacle.next_spawn_time and io.ticks > Obstacle.next_spawn_time:
        Obstacle.spawn()

def _update_and_draw_obstacles():
    """Update active obstacles (if alive) and draw them."""
    for obstacle in Obstacle.obstacles:
        if mona and not mona.is_dead():
            obstacle.update()
        obstacle.draw()

def _draw_player_and_score():
    """Draw the player and current score in the HUD."""
    if mona:
        mona.draw()
        screen.font = small_font
        shadow_text(f"Score: {mona.score}", 3, 0)

def _is_game_over():
    """Return True when the player has finished the death animation."""
    if mona and mona.is_dead() and mona.is_done_dying():
        return True
    return False

def _draw_game_over_ui():
    """Game-over title, final score, and restart prompt."""
    screen.font = large_font
    center_text("GAME OVER!", 18)
    screen.font = small_font
    if mona:
        center_text(f"Final score: {mona.score}", 40)
    if int(io.ticks / 500) % 2:
        screen.brush = brushes.color(255, 255, 255)
        center_text("Press A to restart", 70)

def _should_restart():
    """Return True if A was pressed to restart from game-over."""
    return io.BUTTON_A in io.pressed

def _clear_sky():
    """Fill the background with sky color."""
    screen.brush = brushes.color(73, 219, 255)
    screen.draw(shapes.rectangle(0, 0, 160, 120))

def _update_background_offset():
    """Increment parallax offset while intro or player alive."""
    global background_offset
    if not mona or not mona.is_dead() or state == GameState.INTRO:
        background_offset += 1

def _draw_parallax_layers():
    """Render background, clouds, and grass with parallax scrolling."""
    for i in range(3):
        bo = ((-background_offset / 8) % background.width) - screen.width
        screen.blit(background, bo + (background.width * i), 120 - background.height)
        bo = ((-background_offset / 8) % (cloud.width * 2)) - screen.width
        screen.blit(cloud, bo + (cloud.width * 2 * i), 20)
    for i in range(3):
        bo = ((-background_offset / 4) % (grass.width)) - screen.width
        screen.blit(grass, bo + (grass.width * i), 120 - grass.height)


if __name__ == "__main__":
    run(update)
