import importlib
import os as _real_os
import sys
from types import ModuleType
import importlib.util
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
    # Two-pass approach: create module objects first, then execute them
    # so cross-imports can resolve
    siblings = sorted([py for py in app_dir.glob("*.py") if py.name != "__init__.py"])
    # For flappy: obstacle.py must be executed before mona.py (mona imports obstacle)
    # Heuristic: execute in alphabetical order (icon, mona, obstacle, ui) but reverse
    # if we see 'obstacle' before 'mona' so obstacle loads first
    if app_name == "flappy":
        # Ensure obstacle comes before mona
        siblings = sorted(siblings, key=lambda p: (p.stem != "obstacle", p.stem))
    
    modules_to_exec = []
    
    for py in siblings:
        mod_name = f"badge.apps.{app_name}.{py.stem}"
        if mod_name not in sys.modules:
            try:
                spec = importlib.util.spec_from_file_location(mod_name, str(py))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = mod
                    # also register short name (e.g., 'icon', 'dvd', 'mona', 'obstacle')
                    sys.modules.setdefault(py.stem, mod)
                    modules_to_exec.append((spec, mod))
            except Exception as ex:
                print(f"Warning: Failed to create module spec for {mod_name}: {ex}")
    
    # Now execute all the modules in a second pass
    for spec, mod in modules_to_exec:
        try:
            if spec.loader:
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        except Exception as ex:
            print(f"Warning: Failed to execute module {spec.name}: {ex}")
            # If a sibling fails to import it's fine; the top-level import may not need it


def pytest_sessionstart(session):  # noqa: D401
    """Session start hook to install stubs before any tests import the apps."""
    _install_badgeware_stub()
    _install_os_chdir_noop()


def prepare_app_import(app_name: str):
    """Utility for tests to ready the environment before importing an app."""
    _install_badgeware_stub()
    _install_os_chdir_noop()
    _preload_sibling_modules(app_name)
    # Provide minimal UI shims for apps that expect a local 'ui' module (e.g., menu)
    if app_name == "menu":
        ui = sys.modules.get("ui")
        if ui is None:
            ui = ModuleType("ui")
            sys.modules["ui"] = ui
        if not hasattr(ui, "draw_background"):
            def _bg():
                return None
            ui.draw_background = _bg  # type: ignore[attr-defined]
        if not hasattr(ui, "draw_header"):
            def _hdr():
                return None
            ui.draw_header = _hdr  # type: ignore[attr-defined]
