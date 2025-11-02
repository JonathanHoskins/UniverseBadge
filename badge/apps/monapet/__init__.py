import sys
import os

sys.path.insert(0, "/system/apps/monapet")
os.chdir("/system/apps/monapet")


import ui
from mona import Mona
from badgeware import io, run, State

mona = Mona(82)  # create mona!

# speed at which each statistic goes from 100% to 0%
happiness_duration = 1800
hunger_duration = 1200
cleanliness_duration = 2400


def game_update() -> None:
    global mona
    if not mona.is_dead():
        _update_stats()
        _handle_play()
        _handle_feed()
        _handle_clean()
        _maybe_move_to_random()
        _maybe_random_idle()
        _check_bad_state()
    else:
        _handle_dead_state()


# --- Helper Functions for game_update ---
def _update_stats() -> None:
    seconds = io.ticks_delta / 1000
    happy_delta = (seconds / happiness_duration) * 100
    mona.happy(-happy_delta)
    hunger_delta = (seconds / hunger_duration) * 100
    mona.hunger(-hunger_delta)
    clean_delta = (seconds / cleanliness_duration) * 100
    mona.clean(-clean_delta)

def _handle_play() -> None:
    if io.BUTTON_A in io.pressed:
        mona.happy(30)
        mona.do_action("heart")

def _handle_feed() -> None:
    if io.BUTTON_B in io.pressed:
        mona.hunger(30)
        mona.do_action("eating")

def _handle_clean() -> None:
    if io.BUTTON_C in io.pressed:
        mona.clean(30)
        mona.do_action("dance")

def _maybe_move_to_random() -> None:
    if mona.time_since_last_position_change() > 5:
        mona.move_to_random()

def _maybe_random_idle() -> None:
    if mona.time_since_last_mood_change() > 8:
        mona.random_idle()

def _check_bad_state() -> None:
    if min(mona.hunger(), mona.happy(), mona.clean()) < 30:
        mona.set_mood("notify")

def _handle_dead_state() -> None:
    global mona
    mona.set_mood("dead")
    mona.move_to_center()
    if io.BUTTON_B in io.pressed:
        mona = Mona(82)


    # --- Helper Functions for game_update ---
    def _update_stats():
        seconds = io.ticks_delta / 1000
        happy_delta = (seconds / happiness_duration) * 100
        mona.happy(-happy_delta)
        hunger_delta = (seconds / hunger_duration) * 100
        mona.hunger(-hunger_delta)
        clean_delta = (seconds / cleanliness_duration) * 100
        mona.clean(-clean_delta)

    def _handle_play():
        if io.BUTTON_A in io.pressed:
            mona.happy(30)
            mona.do_action("heart")

    def _handle_feed():
        if io.BUTTON_B in io.pressed:
            mona.hunger(30)
            mona.do_action("eating")

    def _handle_clean():
        if io.BUTTON_C in io.pressed:
            mona.clean(30)
            mona.do_action("dance")

    def _maybe_move_to_random():
        if mona.time_since_last_position_change() > 5:
            mona.move_to_random()

    def _maybe_random_idle():
        if mona.time_since_last_mood_change() > 8:
            mona.random_idle()

    def _check_bad_state():
        if min(mona.hunger(), mona.happy(), mona.clean()) < 30:
            mona.set_mood("notify")

    def _handle_dead_state():
        global mona
        mona.set_mood("dead")
        mona.move_to_center()
        if io.BUTTON_B in io.pressed:
            mona = Mona(82)


def update() -> None:
    game_update()
    mona.update()
    _draw_scene()
    _draw_mona()
    _draw_ui_elements()
    ui.draw_header()


# --- Helper Functions for update ---
def _draw_scene():
    ui.background(mona)

def _draw_mona():
    mona.draw()

def _draw_ui_elements():
    if not mona.is_dead():
        ui.draw_bar("happy",  2, 41, mona.happy())
        ui.draw_bar("hunger", 2, 58, mona.hunger())
        ui.draw_bar("clean",  2, 75, mona.clean())
        ui.draw_button(4, 100,  "play", mona.current_action() == "heart")
        ui.draw_button(55, 100,  "feed", mona.current_action() == "eating")
        ui.draw_button(106, 100, "clean", mona.current_action() == "dance")
    else:
        ui.draw_button(55, 100, "reset", True)


def init():
    state = {
        "happy": 100,
        "hunger": 100,
        "clean": 100,
    }
    if State.load("monapet", state):
        mona.load(state)

    del state


def on_exit():
    State.save("monapet", mona.save())


if __name__ == "__main__":
    run(update, init=init, on_exit=on_exit)
