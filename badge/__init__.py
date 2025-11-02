"""UniverseBadge package.

Provides app modules under `badge.apps` and shared constants in `badge.common`.
This file exists to ensure reliable package imports in all environments
(including CI), even when implicit namespace packages might not be recognized.
"""

__all__ = ["apps", "common"]
