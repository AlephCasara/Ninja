from __future__ import annotations

import argparse
from pathlib import Path

from ninja_labs.pipeline import run_phase1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ninja-labs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    phase1 = subparsers.add_parser("phase1", help="Phase 1 historical substrate")
    phase1_sub = phase1.add_subparsers(dest="phase1_command", required=True)

    build = phase1_sub.add_parser("build", help="Build Bronze/Silver/Gold substrate")
    build.add_argument("--config", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "phase1" and args.phase1_command == "build":
        manifest = run_phase1(args.config)
        print(manifest)
        return 0
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
