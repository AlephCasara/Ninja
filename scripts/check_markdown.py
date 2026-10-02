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

    if text.count("$") % 2:
        errors.append(f"{path.relative_to(ROOT)}: unbalanced $ math delimiters ({text.count('$')} occurrences)")

    # Validate brace balance inside GitHub math fences. This does not replace
    # MathJax parsing, but it catches the most common malformed-LaTeX failure.
    in_math = False
    math_start = 0
    math_lines: list[str] = []

    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not in_math and stripped == (backtick * 3 + "math"):
            in_math = True
            math_start = number
            math_lines = []
            continue

        if in_math and stripped == backtick * 3:
            math = "\n".join(math_lines)
            depth = 0
            for ch in math:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth < 0:
                        add(path, math_start, "math block has an extra closing brace")
                        break

            if depth > 0:
                add(path, math_start, f"math block has {depth} unclosed brace(s)")

            in_math = False
            continue

        if in_math:
            math_lines.append(line)


if errors:
    print("Markdown rendering lint failed:\n", file=sys.stderr)
    for error in errors:
        print(f" - {error}", file=sys.stderr)
    sys.exit(1)

print("Markdown rendering lint passed.")
