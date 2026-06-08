"""absolute_value_schema domain (design.md sec 27)."""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_interval, fmt_union
from mathgen.verify import interval_set, sets_equal


def gen_absolute_value_equation_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    c = rng.randint(-hi, hi)
    d = rng.randint(1, hi)
    lo, high = c - d, c + d
    answer = f"x={lo} or x={high}"
    trace = [
        TraceStep(op="split_positive", text=f"|x - ({c})| = {d} gives x - ({c}) = {d}, so x = {high}."),
        TraceStep(op="split_negative", text=f"It also gives x - ({c}) = -{d}, so x = {lo}."),
        TraceStep(op="finish", text=f"So the solutions are {answer}.", after=answer),
    ]
    return make_sample(
        "absolute_value_schema.absolute_value_equation_basic",
        f"Solve |x - ({c})| = {d}.",
        trace,
        answer,
        {"c": c, "d": d, "difficulty": diff},
        verified=(abs(lo - c) == d and abs(high - c) == d),
    )


def gen_absolute_value_less_than(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    c = rng.randint(-hi, hi)
    d = rng.randint(1, hi)
    lo, high = c - d, c + d
    answer = fmt_interval(lo, high)
    expected = interval_set(lo, high, True, True)
    trace = [
        TraceStep(op="distance_rule", text=f"|x - ({c})| < {d} means x is within distance {d} of {c}."),
        TraceStep(op="compound", text=f"This gives {lo} < x < {high}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    actual = interval_set(lo, high, True, True)
    return make_sample(
        "absolute_value_schema.absolute_value_less_than",
        f"Solve |x - ({c})| < {d}.",
        trace,
        answer,
        {"c": c, "d": d, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_absolute_value_greater_than(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    c = rng.randint(-hi, hi)
    d = rng.randint(1, hi)
    lo, high = c - d, c + d
    answer = fmt_union([fmt_interval(None, lo), fmt_interval(high, None)])
    expected = interval_set(None, lo, True, True) + interval_set(high, None, True, True)
    trace = [
        TraceStep(op="distance_rule", text=f"|x - ({c})| > {d} means x is farther than distance {d} from {c}."),
        TraceStep(op="split", text=f"So x < {lo} or x > {high}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    actual = interval_set(None, lo, True, True) + interval_set(high, None, True, True)
    return make_sample(
        "absolute_value_schema.absolute_value_greater_than",
        f"Solve |x - ({c})| > {d}.",
        trace,
        answer,
        {"c": c, "d": d, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_absolute_value_piecewise_split(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    answer = f"x - {c} if x ≥ {c}; {c} - x if x < {c}"
    trace = [
        TraceStep(op="nonnegative_case", text=f"If x ≥ {c}, then x - {c} is nonnegative, so |x - {c}| = x - {c}."),
        TraceStep(op="negative_case", text=f"If x < {c}, then x - {c} is negative, so |x - {c}| = -(x - {c}) = {c} - x."),
        TraceStep(op="finish", text=f"So the piecewise form is {answer}.", after=answer),
    ]
    return make_sample(
        "absolute_value_schema.absolute_value_piecewise_split",
        f"Write |x - {c}| as a piecewise expression.",
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=True,
    )


def gen_nested_absolute_value_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 16}[diff]
    a = rng.randint(3, hi)
    b = rng.randint(1, a - 1)
    vals = [-(a + b), -(a - b), a - b, a + b]
    answer = "x=" + " or x=".join(str(v) for v in vals)
    trace = [
        TraceStep(op="outer_split", text=f"||x| - {a}| = {b} gives |x| - {a} = {b} or |x| - {a} = -{b}."),
        TraceStep(op="absolute_values", text=f"Thus |x| = {a + b} or |x| = {a - b}."),
        TraceStep(op="solve_inner", text=f"So x = {-(a + b)}, {-(a - b)}, {a - b}, or {a + b}."),
        TraceStep(op="finish", text=f"So the solutions are {answer}.", after=answer),
    ]
    return make_sample(
        "absolute_value_schema.nested_absolute_value_basic",
        f"Solve ||x| - {a}| = {b}.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=all(abs(abs(v) - a) == b for v in vals),
    )


REGISTRY: Dict[str, Any] = {
    "absolute_value_schema.absolute_value_equation_basic": gen_absolute_value_equation_basic,
    "absolute_value_schema.absolute_value_less_than": gen_absolute_value_less_than,
    "absolute_value_schema.absolute_value_greater_than": gen_absolute_value_greater_than,
    "absolute_value_schema.absolute_value_piecewise_split": gen_absolute_value_piecewise_split,
    "absolute_value_schema.nested_absolute_value_basic": gen_nested_absolute_value_basic,
}
