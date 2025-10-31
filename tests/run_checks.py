#!/usr/bin/env python3
"""Run basic repository checks:
- Syntax check (compileall)
- Run pytest if tests are present

Exit code: 0 on success, non-zero on failure.
"""
from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path


def run_syntax_check(root: Path) -> int:
    print("Running syntax check (compileall)...")
    ok = compileall.compile_dir(str(root), force=False, quiet=1)
    if ok:
        print("Syntax check passed.")
        return 0
    else:
        print("Syntax check failed: some files failed to compile.")
        return 2


def find_tests(root: Path) -> bool:
    # Look for a tests/ directory or any test_*.py files
    tests_dir = root / "tests"
    if tests_dir.exists() and any(tests_dir.rglob("test_*.py")):
        return True
    # search for test files anywhere
    if any(root.rglob("test_*.py")):
        return True
    return False


def run_pytest(root: Path) -> int:
    print("Running pytest (if present)...")
    try:
        res = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=str(root))
        return res.returncode
    except FileNotFoundError:
        print("pytest not found. Ensure pytest is installed in the environment.")
        return 3


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    print(f"Repository root: {repo_root}")

    rc = run_syntax_check(repo_root)
    if rc != 0:
        return rc

    if find_tests(repo_root):
        rc = run_pytest(repo_root)
        if rc != 0:
            print(f"pytest failed with exit code {rc}")
            return rc
        print("pytest passed.")
    else:
        print("No tests found; skipping pytest.")

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
