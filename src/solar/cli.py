# Solar CLI - v1.0.3 (with smart update)
from __future__ import annotations

import argparse
import subprocess
import sys

from .engine import SOLAR_VERSION, run_file, compile_to_python


def _in_venv() -> bool:
    # Standard venv detection
    if hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix:
        return True
    # virtualenv compatibility
    if hasattr(sys, "real_prefix"):
        return True
    return False


def _is_windows() -> bool:
    return sys.platform.startswith("win")


def _is_linux_or_macos() -> bool:
    return sys.platform.startswith("linux") or sys.platform == "darwin"


def _run_update() -> int:
    """
    Update Solar via pip, using rules:
      - Windows: pip install -U solar-lang
      - Linux/macOS:
          - in venv: pip install -U solar-lang
          - not in venv: pip install -U solar-lang --break-system-packages
    Uses current Python executable so it updates the same environment
    where 'solar' is installed.
    """
    cmd = [sys.executable, "-m", "pip", "install", "-U", "solar-lang"]

    if _is_linux_or_macos() and not _in_venv():
        cmd.append("--break-system-packages")

    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("Error: pip not found for this Python environment.", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    ap = argparse.ArgumentParser(prog="solar", add_help=True)
    sub = ap.add_subparsers(dest="cmd", required=False)

    sub.add_parser("help", help="Show help")

    p_run = sub.add_parser("run", help="Run a .solar file")
    p_run.add_argument("file", help="Path to .solar file")

    sub.add_parser("version", help="Show Solar version")

    p_comp = sub.add_parser("compile", help="Compile a .solar file to Python and print it")
    p_comp.add_argument("file", help="Path to .solar file")

    sub.add_parser("update", help="Update Solar (pip install -U solar-lang)")

    args = ap.parse_args(argv)

    if args.cmd in (None, "help"):
        ap.print_help()
        return 0

    if args.cmd == "version":
        print(SOLAR_VERSION)
        return 0

    if args.cmd == "run":
        run_file(args.file)
        return 0

    if args.cmd == "compile":
        with open(args.file, "r", encoding="utf-8") as f:
            src = f.read()
        print(compile_to_python(src))
        return 0

    if args.cmd == "update":
        return _run_update()

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
