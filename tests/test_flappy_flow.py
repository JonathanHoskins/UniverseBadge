import importlib

from conftest import prepare_app_import


def _import_flappy():
    prepare_app_import("flappy")
    return importlib.import_module("badge.apps.flappy")


def test_flappy_start_transitions_to_playing():
    flappy = _import_flappy()

    # Reset state to intro
    flappy.state = flappy.GameState.INTRO
    flappy.mona = None

    # Press A
    flappy.io.pressed = {flappy.io.BUTTON_A}

    # One update should move to PLAYING and construct mona
    flappy.update()

    assert flappy.state == flappy.GameState.PLAYING
    assert flappy.mona is not None


def test_flappy_game_over_restart_to_intro():
    flappy = _import_flappy()

    # Ensure we're on the game over screen with a dummy mona for score rendering
    flappy.state = flappy.GameState.GAME_OVER

    class DummyMona:
        score = 0

        def is_dead(self):
            return True

        def is_done_dying(self):
            return True

        def update(self):
            pass

        def draw(self):
            pass

    flappy.mona = DummyMona()

    # Press A to restart
    flappy.io.pressed = {flappy.io.BUTTON_A}

    flappy.update()

    assert flappy.state == flappy.GameState.INTRO
