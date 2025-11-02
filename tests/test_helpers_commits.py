import importlib
from conftest import prepare_app_import


def test_commits_update_score_counts_destroyed_bricks():
    prepare_app_import("commits")
    commits = importlib.import_module("badge.apps.commits")

    # Build a small custom bricks list
    commits.bricks = [
        commits.Brick(0, 0, commits.COMMIT_COLORS[0]),
        commits.Brick(10, 0, commits.COMMIT_COLORS[1]),
        commits.Brick(20, 0, commits.COMMIT_COLORS[2]),
    ]
    # Mark two bricks as destroyed
    commits.bricks[0].alive = False
    commits.bricks[2].alive = False

    # Reset score and update
    commits.score = 0
    commits._update_score()
    assert commits.score == 2
