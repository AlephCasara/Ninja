#!/usr/bin/env python3
"""Fail if Markdown contains patterns that GitHub will not render as intended."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def add(path: Path, line: int, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}:{line}: {message}")


for path in sorted(ROOT.rglob("*.md")):
    if ".git" in path.parts:
        continue

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    backtick = chr(96)

    forbidden = {
        r"\[": r"unsupported display-math delimiter \[; use double-dollar or a math fence",
        r"\]": r"unsupported display-math delimiter \]; use double-dollar or a math fence",
        r"\(": r"unsupported inline-math delimiter \(; use dollar delimiters",
        r"\)": r"unsupported inline-math delimiter \); use dollar delimiters",
        "\\" + backtick: "escaped backtick found; use literal Markdown backticks",
    }

    for number, line in enumerate(lines, 1):
        for needle, message in forbidden.items():
            if needle in line:
                add(path, number, message)

        if line.strip() == "$":
            add(path, number, "single-dollar display delimiter; use $$ or a math fence")

        for ch in line:
            code = ord(ch)
            if code < 32 and ch not in {"\t"}:
                add(path, number, f"unexpected control character U+{code:04X}")

    tick_fences = sum(1 for line in lines if line.lstrip().startswith(backtick * 3))
    tilde_fences = sum(1 for line in lines if line.lstrip().startswith("~~~"))

    if tick_fences % 2:
        errors.append(f"{path.relative_to(ROOT)}: unbalanced backtick fences ({tick_fences} delimiter lines)")

    if tilde_fences % 2:
        errors.append(f"{path.relative_to(ROOT)}: unbalanced tilde fences ({tilde_fences} delimiter lines)")

    if text.count("$$") % 2:
        errors.append(f"{path.relative_to(ROOT)}: unbalanced $$ math delimiters ({text.count('$$')} occurrences)")


if errors:
    print("Markdown rendering lint failed:\n", file=sys.stderr)
    for error in errors:
        print(f" - {error}", file=sys.stderr)
    sys.exit(1)

print("Markdown rendering lint passed.")
