#!/usr/bin/env python3
"""Generate Out-of-Distribution (OOD) test data for MathGen.

Two modes:
  extrap  — digits/ranges beyond training distribution
  template — question phrasing not seen during training
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import List

from mathgen.config import GenConfig, Difficulty
from mathgen.core import Sample, json_default
from mathgen.registry import GENERATORS, generate_samples
from mathgen.validate import validate_sample

# These templates are RESERVED for OOD testing — never used in training.
OOD_TEMPLATES = {
    "generic": [
        "Work out {q}.",
        "How much is {q}?",
        "Can you figure out {q}?",
        "Please calculate {q}.",
        "I need the answer to: {q}.",
        "Solve the following: {q}.",
        "{q} — what do you get?",
        "Tell me the result of {q}.",
        "Obtain the value of {q}.",
    ],
}

# Extrapolation: sources where we push digit ranges beyond training.
# Each entry: (source_name, harder_params_override)
# Training max digits: addition=4, subtraction=4, multiplication=4, division=4
# OOD: push to 5-6 digits
EXTRAP_SOURCES = [
    "arithmetic.integer_addition_carry",
    "arithmetic.integer_subtraction_borrow",
    "arithmetic.long_multiplication",
    "arithmetic.long_division_exact",
    "arithmetic.long_division_remainder",
    "arithmetic.long_division_zero_in_quotient",
    "arithmetic.decimal_multiplication",
    "arithmetic.decimal_division_by_decimal",
    "arithmetic.order_of_operations_nested",
]


def generate_extrap(n: int, seed: int, out: Path) -> None:
    """Generate extrapolation OOD: larger digit ranges than training."""
    rng = random.Random(seed)
    collected: List[Sample] = []
    sources = EXTRAP_SOURCES
    attempts = 0
    cap = max(1000, n * 50)

    while len(collected) < n and attempts < cap:
        attempts += 1
        src = rng.choice(sources)
        # Use HARD difficulty for maximum digit ranges
        sample = GENERATORS[src](rng, GenConfig(difficulty=Difficulty.HARD))
        ok, _ = validate_sample(sample)
        if ok:
            collected.append(sample)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for s in collected:
            f.write(json.dumps(s.to_json_obj(), ensure_ascii=False, default=json_default) + "\n")
    print(f"Wrote {len(collected)} extrapolation OOD samples to {out}")


def generate_template_ood(n: int, seed: int, out: Path) -> None:
    """Generate template OOD: unseen question phrasings."""
    rng = random.Random(seed)
    sources = list(GENERATORS.keys())
    templates = OOD_TEMPLATES["generic"]
    collected: List[Sample] = []
    attempts = 0
    cap = max(1000, n * 50)

    while len(collected) < n and attempts < cap:
        attempts += 1
        src = rng.choice(sources)
        sample = GENERATORS[src](rng, GenConfig())
        ok, _ = validate_sample(sample)
        if not ok:
            continue
        # Rewrite the question with an OOD template.
        original_q = sample.messages[0]["content"]
        template = rng.choice(templates)
        new_q = template.format(q=_strip_period(original_q))
        sample.messages[0]["content"] = new_q
        collected.append(sample)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for s in collected:
            f.write(json.dumps(s.to_json_obj(), ensure_ascii=False, default=json_default) + "\n")
    print(f"Wrote {len(collected)} template OOD samples to {out}")


def _strip_period(q: str) -> str:
    """Remove trailing period so template can add its own punctuation."""
    q = q.strip()
    if q.endswith("."):
        return q[:-1].strip()
    return q


def main():
    parser = argparse.ArgumentParser(description="Generate OOD test data for MathGen")
    parser.add_argument("--n", type=int, required=True, help="Number of samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, required=True, help="Output JSONL path")
    parser.add_argument("--mode", choices=["extrap", "template"], required=True)
    args = parser.parse_args()

    if args.mode == "extrap":
        generate_extrap(args.n, args.seed, Path(args.out))
    else:
        generate_template_ood(args.n, args.seed, Path(args.out))


if __name__ == "__main__":
    main()
