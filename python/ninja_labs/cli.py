from __future__ import annotations

import argparse
import json
from pathlib import Path

from ninja_labs.adapters.arctic_shift_stream import download_subreddit_posts_jsonl
from ninja_labs.dataset_quality import evaluate_e1_dataset_quality
from ninja_labs.e1_final import create_e1_final_test_seal, run_e1_final_test
from ninja_labs.e1_robustness import run_e1_robustness
from ninja_labs.pipeline import run_phase1
from ninja_labs.preregistration import create_e1_preregistration_seal
from ninja_labs.sealed_e1 import run_sealed_e1_train_validation
from ninja_labs.util import git_is_dirty, parse_utc


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
    acquire.add_argument("--after", required=True)
    acquire.add_argument("--before", required=True)
    acquire.add_argument("--out-dir", type=Path, default=Path(".ninja-inputs/arctic-shift"))
    acquire.add_argument("--no-resume", action="store_true")

    validation = subparsers.add_parser("validation", help="Dataset and experiment checks")
    validation_sub = validation.add_subparsers(dest="validation_command", required=True)
    dataset_gate = validation_sub.add_parser("e1-dataset")
    dataset_gate.add_argument("--manifest", type=Path, required=True)
    dataset_gate.add_argument("--config", type=Path, required=True)
    dataset_gate.add_argument("--output", type=Path, required=True)

    experiment = subparsers.add_parser("experiment", help="Run experiment executors (E1 commands are legacy v1)")
    experiment_sub = experiment.add_subparsers(dest="experiment_command", required=True)
    prereg = experiment_sub.add_parser("e1-preregister", help="Legacy E1 v1 frozen protocol")
    prereg.add_argument("--manifest", type=Path, required=True)
    prereg.add_argument("--config", type=Path, required=True)
    prereg.add_argument("--dataset-quality", type=Path, required=True)
    prereg.add_argument("--output", type=Path, required=True)

    e1_tv = experiment_sub.add_parser("e1-train-validation", help="Legacy E1 v1 frozen protocol")
    e1_tv.add_argument("--manifest", type=Path, required=True)
    e1_tv.add_argument("--config", type=Path, required=True)
    e1_tv.add_argument("--seal", type=Path, required=True)
    e1_tv.add_argument("--output", type=Path, required=True)

    robust = experiment_sub.add_parser("e1-robustness", help="Legacy E1 v1 frozen protocol")
    robust.add_argument("--manifest", type=Path, required=True)
    robust.add_argument("--config", type=Path, required=True)
    robust.add_argument("--preregistration-seal", type=Path, required=True)
    robust.add_argument("--train-validation-result", type=Path, required=True)
    robust.add_argument("--output", type=Path, required=True)

    final_seal = experiment_sub.add_parser("e1-final-seal", help="Legacy E1 v1 frozen protocol")
    final_seal.add_argument("--manifest", type=Path, required=True)
    final_seal.add_argument("--config", type=Path, required=True)
    final_seal.add_argument("--preregistration-seal", type=Path, required=True)
    final_seal.add_argument("--train-validation-result", type=Path, required=True)
    final_seal.add_argument("--robustness-result", type=Path, required=True)
    final_seal.add_argument("--output", type=Path, required=True)

    final_test = experiment_sub.add_parser("e1-final-test", help="Legacy E1 v1 frozen protocol")
    final_test.add_argument("--manifest", type=Path, required=True)
    final_test.add_argument("--config", type=Path, required=True)
    final_test.add_argument("--preregistration-seal", type=Path, required=True)
    final_test.add_argument("--train-validation-result", type=Path, required=True)
    final_test.add_argument("--robustness-result", type=Path, required=True)
    final_test.add_argument("--final-test-seal", type=Path, required=True)
    final_test.add_argument("--access-ledger", type=Path, required=True)
    final_test.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "phase1" and args.phase1_command == "build":
        print(run_phase1(args.config))
        return 0
    if args.command == "phase1" and args.phase1_command == "acquire-reddit":
        reports = []
        for subreddit in args.subreddit:
            reports.append(
                download_subreddit_posts_jsonl(
                    subreddit=subreddit,
                    after=parse_utc(args.after),
                    before=parse_utc(args.before),
                    output_path=args.out_dir / f"r_{subreddit}_posts.jsonl",
                    resume=not args.no_resume,
                )
            )
        print(json.dumps(reports, indent=2, sort_keys=True))
        return 0
    if args.command == "validation" and args.validation_command == "e1-dataset":
        payload = evaluate_e1_dataset_quality(manifest_path=args.manifest, config_path=args.config, output_path=args.output)
        print(json.dumps(payload["checks"], sort_keys=True))
        return 0 if payload["passed"] else 1
    if args.command == "experiment" and args.experiment_command == "e1-preregister":
        if git_is_dirty():
            raise RuntimeError("E1 preregistration requires a clean Git worktree")
        payload = create_e1_preregistration_seal(
            manifest_path=args.manifest,
            config_path=args.config,
            dataset_quality_path=args.dataset_quality,
            output_path=args.output,
        )
        print(payload["seal_sha256"])
        return 0
    if args.command == "experiment" and args.experiment_command == "e1-train-validation":
        payload = run_sealed_e1_train_validation(manifest_path=args.manifest, config_path=args.config, seal_path=args.seal, output_path=args.output)
        print(json.dumps(payload["primary_confirmatory_result"], sort_keys=True))
        return 0
    if args.command == "experiment" and args.experiment_command == "e1-robustness":
        payload = run_e1_robustness(
            manifest_path=args.manifest,
            config_path=args.config,
            preregistration_seal_path=args.preregistration_seal,
            train_validation_result_path=args.train_validation_result,
            output_path=args.output,
        )
        print(json.dumps({"status": payload["status"], "checks": payload["checks"]}, sort_keys=True))
        return 0 if payload["passed"] else 1
    if args.command == "experiment" and args.experiment_command == "e1-final-seal":
        payload = create_e1_final_test_seal(
            manifest_path=args.manifest,
            config_path=args.config,
            preregistration_seal_path=args.preregistration_seal,
            train_validation_result_path=args.train_validation_result,
            robustness_result_path=args.robustness_result,
            output_path=args.output,
        )
        print(payload["seal_sha256"])
        return 0
    if args.command == "experiment" and args.experiment_command == "e1-final-test":
        payload = run_e1_final_test(
            manifest_path=args.manifest,
            config_path=args.config,
            preregistration_seal_path=args.preregistration_seal,
            train_validation_result_path=args.train_validation_result,
            robustness_result_path=args.robustness_result,
            final_test_seal_path=args.final_test_seal,
            access_ledger_path=args.access_ledger,
            output_path=args.output,
        )
        print(json.dumps({"status": payload["status"], "primary": payload["primary"]}, sort_keys=True))
        return 0
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
