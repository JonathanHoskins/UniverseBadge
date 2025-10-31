import importlib
import os as _real_os
import sys
from types import ModuleType
from pathlib import Path


def _install_badgeware_stub():
    # Ensure tests/_stubs is on sys.path so `import badgeware` resolves to our stub
    stubs_dir = Path(__file__).parent / "_stubs"
    if str(stubs_dir) not in sys.path:
        sys.path.insert(0, str(stubs_dir))


def _install_os_chdir_noop():
    # Create a proxy module for os that no-ops chdir to avoid FileNotFoundError
    if getattr(sys, "_badge_tests_os_stub", None):
        return
    proxy = ModuleType("os")
    # Copy attributes from real os
    for name in dir(_real_os):
        setattr(proxy, name, getattr(_real_os, name))
    # Override chdir to noop
    def _noop_chdir(_path):
        return None
    proxy.chdir = _noop_chdir  # type: ignore[attr-defined]
    sys.modules["os"] = proxy
    sys._badge_tests_os_stub = True  # type: ignore[attr-defined]


def _preload_sibling_modules(app_name: str):
    """
    Some apps import siblings with bare imports (e.g., `from mona import Mona`).
    Preload those siblings using their fully qualified path and register short
    names in sys.modules so the app import can resolve them.
    """
    app_dir = Path(__file__).resolve().parents[1] / "badge" / "apps" / app_name
    if not app_dir.is_dir():
        return
    for py in app_dir.glob("*.py"):
        if py.name == "__init__.py":
            continue
        mod_name = f"badge.apps.{app_name}.{py.stem}"
        try:
            mod = importlib.import_module(mod_name)
            # register short name (e.g., 'mona') for bare imports
            sys.modules.setdefault(py.stem, mod)
        except Exception:
            # If a sibling fails to import it's fine; the top-level import may not need it
            pass


def pytest_sessionstart(session):  # noqa: D401
    """Session start hook to install stubs before any tests import the apps."""
    _install_badgeware_stub()
    _install_os_chdir_noop()


def prepare_app_import(app_name: str):
    """Utility for tests to ready the environment before importing an app."""
    _install_badgeware_stub()
    _install_os_chdir_noop()
    _preload_sibling_modules(app_name)
