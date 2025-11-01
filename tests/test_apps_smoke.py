import importlib
from pathlib import Path

from tests.conftest import prepare_app_import


def discover_apps():
    apps_dir = Path(__file__).resolve().parents[1] / "badge" / "apps"
    out = []
    for d in apps_dir.iterdir():
        if d.is_dir() and (d / "__init__.py").exists():
            out.append(d.name)
    return sorted(out)


def try_import_app(app: str):
    prepare_app_import(app)
    fqmn = f"badge.apps.{app}"
    return importlib.import_module(fqmn)


def test_each_app_runs_one_update():
    failures = []
    skip = {
        # Hardware/network dependent or complex runtime coupling
        "badge",   # requires network/machine/powman
        "quest",   # IR beacon and external libs
        "tv-remote",  # IR beacon and external libs
        "gallery", # file system expectations
        "monapet", # heavy sprite/UI coupling
        "sketch",  # UI module coupling
        # Intentionally include 'dvd' and 'menu' now that stubs + preload handle them
    }
    for app in discover_apps():
        if app in skip:
            continue
        try:
            module = try_import_app(app)
            # call update once if present
            if hasattr(module, "update") and callable(module.update):
                ret = module.update()
                # menu may return a string path to launch; others return None
                assert ret is None or isinstance(ret, (str, bytes))
        except Exception as e:
            failures.append((app, repr(e)))

    if failures:
        msgs = "\n".join([f"{a}: {m}" for a, m in failures])
        raise AssertionError(f"Some apps failed to import or update once:\n{msgs}")
