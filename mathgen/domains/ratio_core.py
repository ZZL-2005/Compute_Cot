"""ratio_percent_proportion extras (design.md sec 10, parts not in arithmetic_core).

ratio simplification, direct and inverse proportion, and rate / unit conversion.
proportion_solve, percent_to_fraction_decimal and percent_change already live in
arithmetic_core. All answers exact and verified.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction


def gen_ratio_simplify(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base_a = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    base_b = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    g0 = math.gcd(base_a, base_b)
    ra, rb = base_a // g0, base_b // g0
    k = rng.randint(2, {Difficulty.EASY: 5, Difficulty.MEDIUM: 10, Difficulty.HARD: 20}[diff])
    a, b = ra * k, rb * k
    answer = f"{ra}:{rb}"
    trace = [
        TraceStep(op="find_gcd", text=f"Find the greatest common divisor of {a} and {b}: gcd = {k}."),
        TraceStep(op="divide", text=f"Divide both parts by {k}: {a}÷{k} = {ra} and {b}÷{k} = {rb}."),
        TraceStep(op="finish", text=f"So {a}:{b} simplifies to {answer}.", after=answer),
    ]
    return make_sample(
        "ratio_percent.ratio_simplify",
        f"Simplify the ratio {a}:{b}.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=(math.gcd(a, b) == k and ra == a // math.gcd(a, b)),
    )


def gen_direct_proportion(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = rng.randint(2, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff])
    x1 = rng.randint(2, 9)
    y1 = k * x1
    x2 = rng.randint(2, 12)
    y2 = k * x2
    trace = [
        TraceStep(op="find_constant", text=f"Direct proportion means y = kx. From x={x1}, y={y1}: k = {y1}/{x1} = {k}."),
        TraceStep(op="apply", text=f"For x={x2}: y = {k}×{x2} = {y2}."),
        TraceStep(op="finish", text=f"So y = {y2}.", after=str(y2)),
    ]
    return make_sample(
        "ratio_percent.direct_proportion",
        f"y is directly proportional to x. When x={x1}, y={y1}. Find y when x={x2}.",
        trace,
        str(y2),
        {"k": k, "x1": x1, "x2": x2, "difficulty": diff},
        verified=(y2 == k * x2 and y1 == k * x1),
    )


def gen_inverse_proportion(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 18}[diff]
    x1 = rng.randint(2, hi)
    y1 = rng.randint(2, hi)
    k = x1 * y1
    divisors = [d for d in range(1, k + 1) if k % d == 0]
    x2 = rng.choice(divisors)
    while x2 == x1:
        x2 = rng.choice(divisors)
    y2 = Fraction(k, x2)
    ans = fmt_fraction(y2)
    trace = [
        TraceStep(op="find_constant", text=f"Inverse proportion means xy = k. From x={x1}, y={y1}: k = {x1}×{y1} = {k}."),
        TraceStep(op="apply", text=f"For x={x2}: y = k/x = {k}/{x2} = {ans}."),
        TraceStep(op="finish", text=f"So y = {ans}.", after=ans),
    ]
    return make_sample(
        "ratio_percent.inverse_proportion",
        f"y is inversely proportional to x. When x={x1}, y={y1}. Find y when x={x2}.",
        trace,
        ans,
        {"k": k, "x1": x1, "x2": x2, "difficulty": diff},
        verified=(y2 == Fraction(k, x2) and x1 * y1 == k),
    )


_CONV = [
    ("kilometers", "meters", 1000),
    ("meters", "centimeters", 100),
    ("hours", "minutes", 60),
    ("minutes", "seconds", 60),
    ("kilograms", "grams", 1000),
    ("liters", "milliliters", 1000),
]


def gen_rate_unit_conversion(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    u1, u2, factor = rng.choice(_CONV)
    amount = rng.randint(2, {Difficulty.EASY: 12, Difficulty.MEDIUM: 50, Difficulty.HARD: 200}[diff])
    result = amount * factor
    trace = [
        TraceStep(op="state_factor", text=f"There are {factor} {u2} in 1 {u1}."),
        TraceStep(op="multiply", text=f"Multiply: {amount}×{factor} = {result}."),
        TraceStep(op="finish", text=f"So {amount} {u1} = {result} {u2}.", after=str(result)),
    ]
    return make_sample(
        "ratio_percent.rate_unit_conversion",
        f"Convert {amount} {u1} to {u2}.",
        trace,
        str(result),
        {"amount": amount, "u1": u1, "u2": u2, "factor": factor, "difficulty": diff},
        verified=(result == amount * factor),
    )


REGISTRY: Dict[str, Any] = {
    "ratio_percent.ratio_simplify": gen_ratio_simplify,
    "ratio_percent.direct_proportion": gen_direct_proportion,
    "ratio_percent.inverse_proportion": gen_inverse_proportion,
    "ratio_percent.rate_unit_conversion": gen_rate_unit_conversion,
}
