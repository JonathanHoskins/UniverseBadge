import importlib
from types import SimpleNamespace

from conftest import prepare_app_import


def test_life_injects_pattern_when_stagnant(monkeypatch):
    """If the board is stagnant for multiple generations, a pattern is injected."""
    prepare_app_import("life")
    life = importlib.import_module("badge.apps.life")

    # Force stagnation detection and set the counter just below the threshold
    life.game.stagnant_count = 4  # one less than threshold so next update triggers inject
    monkeypatch.setattr(life.game, "is_stagnant", lambda: True)

    called = {"pattern": None, "count": 0}

    def fake_inject(pattern_name):
        called["pattern"] = pattern_name
        called["count"] += 1
        # do not actually mutate grid for this test
        return None

    # Make random.choice deterministic so assertion is stable
    monkeypatch.setattr(life, "random", SimpleNamespace(choice=lambda seq: seq[0]))
    monkeypatch.setattr(life.game, "inject_pattern", fake_inject)

    # Advance time enough to trigger update interval
    life.io.ticks = life.game.last_update + life.game.update_interval + 1

    life.update()

    assert called["count"] == 1, "Expected inject_pattern to be called once when stagnant"
    assert called["pattern"] in {
        "glider",
        "lwss",
        "blinker",
        "toad",
        "beacon",
        "pulsar",
        "r_pentomino",
        "acorn",
    }
