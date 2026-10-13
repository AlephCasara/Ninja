from __future__ import annotations

import argparse
import json
from pathlib import Path

from ninja_labs.pipeline import run_phase1
from ninja_labs.validation.e1_attention import (
    run_e1_estimator_validation,
    write_e1_estimator_validation,
)
from ninja_labs.validation.harness import run_validation_selftest, write_validation_selftest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ninja-labs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    phase1 = subparsers.add_parser("phase1", help="Phase 1 historical substrate")
    phase1_sub = phase1.add_subparsers(dest="phase1_command", required=True)

    build = phase1_sub.add_parser("build", help="Build Bronze/Silver/Gold substrate")
    build.add_argument("--config", type=Path, required=True)

    validation = subparsers.add_parser(
        "validation", help="Scientific anti-confirmation and estimator validation"
    )
    validation_sub = validation.add_subparsers(dest="validation_command", required=True)

    selftest = validation_sub.add_parser(
        "selftest", help="Run deterministic generic anti-confirmation harness checks"
    )
    selftest.add_argument("--seed", type=int, default=1729)
    selftest.add_argument("--output", type=Path)

    e1 = validation_sub.add_parser(
        "e1-attention", help="Validate E1 attention estimators on controlled worlds"
    )
    e1.add_argument("--seed", type=int, default=20261013)
    e1.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "phase1" and args.phase1_command == "build":
        manifest = run_phase1(args.config)
        print(manifest)
        return 0
    if args.command == "validation" and args.validation_command == "selftest":
        if args.output:
            payload = write_validation_selftest(args.output, seed=args.seed)
            print(args.output)
        else:
            payload = run_validation_selftest(seed=args.seed)
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["passed"] else 1
    if args.command == "validation" and args.validation_command == "e1-attention":
        if args.output:
            payload = write_e1_estimator_validation(args.output, seed=args.seed)
            print(args.output)
        else:
            payload = run_e1_estimator_validation(seed=args.seed)
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["passed"] else 1
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
