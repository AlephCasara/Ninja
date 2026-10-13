from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ninja_labs.e1 import run_e1_train_validation
from ninja_labs.preregistration import verify_e1_preregistration_seal
from ninja_labs.util import sha256_json


def run_sealed_e1_train_validation(
    *,
    manifest_path: Path,
    config_path: Path,
    seal_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Run E1 train/validation only after verifying its preregistration seal."""

    seal = verify_e1_preregistration_seal(
        seal_path=seal_path,
        manifest_path=manifest_path,
        config_path=config_path,
    )
    payload = run_e1_train_validation(
        manifest_path=manifest_path,
        config_path=config_path,
        output_path=output_path,
    )

    confirmatory = seal["confirmatory"]
    primary: dict[str, Any] | None = None
    for record in payload.get("comparisons", []):
        is_primary = (
            record.get("target") == confirmatory["primary_target"]
            and int(record.get("horizon_bins", -1)) == int(confirmatory["primary_horizon_bins"])
            and record.get("candidate") == confirmatory["primary_candidate"]
        )
        record["role"] = "PRIMARY_CONFIRMATORY" if is_primary else "SECONDARY_OR_EXPLORATORY"
        if is_primary:
            if primary is not None:
                raise ValueError("multiple records matched the preregistered primary comparison")
            primary = record

    if primary is None:
        primary_summary: dict[str, Any] = {
            "status": "INVALID",
            "reason": "preregistered primary comparison was not estimable",
            **confirmatory,
        }
    else:
        primary_summary = {
            "status": primary["status"],
            "target": primary["target"],
            "horizon_bins": primary["horizon_bins"],
            "candidate": primary["candidate"],
            "relative_loss_improvement": primary.get("relative_loss_improvement"),
            "ci95_low": primary.get("ci95_low"),
            "ci95_high": primary.get("ci95_high"),
            "p_value": primary.get("p_value"),
            "q_value": primary.get("q_value"),
            "n_train": primary.get("n_train"),
            "n_validation": primary.get("n_validation"),
            "effective_n": primary.get("effective_n"),
        }

    payload["preregistration"] = {
        "seal_path": str(seal_path),
        "seal_sha256": seal["seal_sha256"],
        "verified": True,
        "created_before_train_validation": True,
    }
    payload["primary_confirmatory_result"] = primary_summary
    payload["scientific_boundary"] = (
        "Train/validation result under a preregistered seal. The untouched test artifact was not opened. "
        "Secondary/exploratory results cannot replace the preregistered primary comparison."
    )
    payload.pop("result_sha256", None)
    payload["result_sha256"] = sha256_json(payload)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
