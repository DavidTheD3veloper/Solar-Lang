# Solar CLI - v1.0.3
from __future__ import annotations

import argparse
import sys
from .engine import SOLAR_VERSION, run_file, compile_to_python

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

    ap.print_help()
    return 2
