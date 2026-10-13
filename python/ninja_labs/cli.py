from __future__ import annotations

import argparse
import json
from pathlib import Path

from ninja_labs.adapters.arctic_shift_stream import download_subreddit_posts_jsonl
from ninja_labs.pipeline import run_phase1
from ninja_labs.preregistration import create_e1_preregistration_seal
from ninja_labs.sealed_e1 import run_sealed_e1_train_validation
from ninja_labs.util import parse_utc
from ninja_labs.validation.e1_attention import (
    run_e1_estimator_validation,
    write_e1_estimator_validation,
)
from ninja_labs.validation.e1_monte_carlo import (
    run_e1_monte_carlo_validation,
    write_e1_monte_carlo_validation,
)
from ninja_labs.validation.harness import run_validation_selftest, write_validation_selftest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ninja-labs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    phase1 = subparsers.add_parser("phase1", help="Phase 1 historical substrate")
    phase1_sub = phase1.add_subparsers(dest="phase1_command", required=True)

    build = phase1_sub.add_parser("build", help="Build Bronze/Silver/Gold substrate")
    build.add_argument("--config", type=Path, required=True)

    acquire = phase1_sub.add_parser(
        "acquire-reddit", help="Stream canonical Arctic Shift subreddit post JSONL"
    )
    acquire.add_argument("--subreddit", action="append", required=True)
    acquire.add_argument("--after", required=True, help="UTC/ISO timestamp or date")
    acquire.add_argument("--before", required=True, help="exclusive UTC/ISO timestamp or date")
    acquire.add_argument(
        "--out-dir", type=Path, default=Path(".ninja-inputs/arctic-shift")
    )
    acquire.add_argument("--no-resume", action="store_true")

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

    e1_mc = validation_sub.add_parser(
        "e1-monte-carlo",
        help="Stress E1 seasonal attention normalization across randomized worlds",
    )
    e1_mc.add_argument("--seed", type=int, default=20261013)
    e1_mc.add_argument("--worlds", type=int, default=64)
    e1_mc.add_argument("--output", type=Path)

    experiment = subparsers.add_parser("experiment", help="Run preregistered experiments")
    experiment_sub = experiment.add_subparsers(dest="experiment_command", required=True)

    prereg = experiment_sub.add_parser(
        "e1-preregister",
        help="Seal E1 before train/validation without opening untouched_test",
    )
    prereg.add_argument("--manifest", type=Path, required=True)
    prereg.add_argument("--config", type=Path, required=True)
    prereg.add_argument("--estimator-validation", type=Path, required=True)
    prereg.add_argument("--monte-carlo-validation", type=Path, required=True)
    prereg.add_argument("--output", type=Path, required=True)

    e1_tv = experiment_sub.add_parser(
        "e1-train-validation",
        help="Evaluate E1 on train+validation under a preregistration seal",
    )
    e1_tv.add_argument("--manifest", type=Path, required=True)
    e1_tv.add_argument("--config", type=Path, required=True)
    e1_tv.add_argument("--seal", type=Path, required=True)
    e1_tv.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "phase1" and args.phase1_command == "build":
        manifest = run_phase1(args.config)
        print(manifest)
        return 0
    if args.command == "phase1" and args.phase1_command == "acquire-reddit":
        after = parse_utc(args.after)
        before = parse_utc(args.before)
        reports = []
        for subreddit in args.subreddit:
            report = download_subreddit_posts_jsonl(
                subreddit=subreddit,
                after=after,
                before=before,
                output_path=args.out_dir / f"r_{subreddit}_posts.jsonl",
                resume=not args.no_resume,
            )
            reports.append(report)
        print(json.dumps(reports, indent=2, sort_keys=True))
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
    if args.command == "validation" and args.validation_command == "e1-monte-carlo":
        if args.output:
            payload = write_e1_monte_carlo_validation(
                args.output, seed=args.seed, worlds=args.worlds
            )
            print(args.output)
        else:
            payload = run_e1_monte_carlo_validation(
                seed=args.seed, worlds=args.worlds
            )
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["passed"] else 1
    if args.command == "experiment" and args.experiment_command == "e1-preregister":
        payload = create_e1_preregistration_seal(
            manifest_path=args.manifest,
            config_path=args.config,
            estimator_validation_path=args.estimator_validation,
            monte_carlo_validation_path=args.monte_carlo_validation,
            output_path=args.output,
        )
        print(args.output)
        print(payload["seal_sha256"])
        return 0
    if args.command == "experiment" and args.experiment_command == "e1-train-validation":
        payload = run_sealed_e1_train_validation(
            manifest_path=args.manifest,
            config_path=args.config,
            seal_path=args.seal,
            output_path=args.output,
        )
        print(args.output)
        print(json.dumps(payload["status_counts"], sort_keys=True))
        print(json.dumps(payload["primary_confirmatory_result"], sort_keys=True))
        return 0
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
