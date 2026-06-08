"""rational_inequality_schema domain (design.md sec 26)."""

from __future__ import annotations

import random
from typing import Any, Dict

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_interval, fmt_union
from mathgen.verify import X, interval_set, sets_equal


def _distinct_points(rng: random.Random, hi: int, n: int) -> list[int]:
    vals = rng.sample(range(-hi, hi + 1), n)
    return sorted(vals)


def gen_find_zeros_and_poles(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a, b, c = _distinct_points(rng, hi, 3)
    answer = f"zeros: {a}, {b}; pole: {c}"
    trace = [
        TraceStep(op="set_numerator_zero", text=f"Zeros come from the numerator: {fmt_factor(-a)}{fmt_factor(-b)} = 0 gives x = {a} or x = {b}."),
        TraceStep(op="set_denominator_zero", text=f"Poles come from the denominator: {fmt_factor(-c)} = 0 gives x = {c}."),
        TraceStep(op="finish", text=f"So the critical data are {answer}.", after=answer),
    ]
    return make_sample(
        "rational_inequality_schema.find_zeros_and_poles",
        f"Find the zeros and pole of ({fmt_factor(-a)}{fmt_factor(-b)})/{fmt_factor(-c)}.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "difficulty": diff},
        verified=(len({a, b, c}) == 3),
    )


def gen_split_intervals_by_critical_points(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a, b, c = _distinct_points(rng, hi, 3)
    parts = [fmt_interval(None, a), fmt_interval(a, b), fmt_interval(b, c), fmt_interval(c, None)]
    answer = fmt_union(parts)
    trace = [
        TraceStep(op="sort_points", text=f"Sort the critical points: {a} < {b} < {c}."),
        TraceStep(op="split_line", text=f"These points split the real line into {answer}."),
        TraceStep(op="finish", text=f"So the test intervals are {answer}.", after=answer),
    ]
    return make_sample(
        "rational_inequality_schema.split_intervals_by_critical_points",
        f"Split the real line using the critical points {a}, {b}, and {c}.",
        trace,
        answer,
        {"points": [a, b, c], "difficulty": diff},
        verified=(a < b < c),
    )


def gen_sign_chart_for_fraction(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a, b = _distinct_points(rng, hi, 2)
    answer = fmt_union([fmt_interval(None, a), fmt_interval(b, None)])
    expected = interval_set(None, a, True, True) + interval_set(b, None, True, True)
    trace = [
        TraceStep(op="critical_points", text=f"The numerator is zero at x = {a}, and the denominator is zero at x = {b}."),
        TraceStep(op="sign_chart", text=f"For (x - ({a}))/(x - ({b})), the signs are positive outside the two critical points and negative between them."),
        TraceStep(op="exclude_points", text="The inequality is strict, so the zero is not included, and the pole is never included."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    actual = sp.solveset((X - a) / (X - b) > 0, X, domain=sp.S.Reals)
    return make_sample(
        "rational_inequality_schema.sign_chart_for_fraction",
        f"Solve ({fmt_factor(-a)})/{fmt_factor(-b)} > 0 using a sign chart.",
        trace,
        answer,
        {"zero": a, "pole": b, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_exclude_denominator_zeros(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    c = rng.randint(-hi, hi)
    answer = f"x ≠ {c}"
    trace = [
        TraceStep(op="state_rule", text="A rational expression is undefined where its denominator is zero."),
        TraceStep(op="solve_denominator", text=f"Set {fmt_factor(-c)} = 0, which gives x = {c}."),
        TraceStep(op="exclude", text=f"Exclude this value from any solution set: {answer}."),
        TraceStep(op="finish", text=f"So the denominator restriction is {answer}.", after=answer),
    ]
    return make_sample(
        "rational_inequality_schema.exclude_denominator_zeros",
        f"State the denominator restriction for 1/{fmt_factor(-c)}.",
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=True,
    )


def gen_interval_solution_with_open_closed_endpoints(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a, b, c = _distinct_points(rng, hi, 3)
    if rng.random() < 0.5:
        op = ">="
        answer = fmt_union([fmt_interval(a, b, False, False), fmt_interval(c, None, True, True)])
        expected = interval_set(a, b, False, False) + interval_set(c, None, True, True)
        keep = "the positive intervals, including numerator zeros and excluding the pole"
    else:
        op = "<="
        answer = fmt_union([fmt_interval(None, a, True, False), fmt_interval(b, c, False, True)])
        expected = interval_set(None, a, True, False) + interval_set(b, c, False, True)
        keep = "the negative intervals, including numerator zeros and excluding the pole"
    trace = [
        TraceStep(op="critical_points", text=f"The zeros are x = {a} and x = {b}; the pole is x = {c}."),
        TraceStep(op="sign_chart", text=f"For {fmt_factor(-a)}{fmt_factor(-b)}/{fmt_factor(-c)}, the signs from left to right are negative, positive, negative, positive."),
        TraceStep(op="endpoint_rules", text=f"For {op} 0, keep {keep}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    rel = ((X - a) * (X - b) / (X - c) >= 0) if op == ">=" else ((X - a) * (X - b) / (X - c) <= 0)
    actual = sp.solveset(rel, X, domain=sp.S.Reals)
    return make_sample(
        "rational_inequality_schema.interval_solution_with_open_closed_endpoints",
        f"Solve {fmt_factor(-a)}{fmt_factor(-b)}/{fmt_factor(-c)} {op} 0, showing endpoint inclusion.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "op": op, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


REGISTRY: Dict[str, Any] = {
    "rational_inequality_schema.find_zeros_and_poles": gen_find_zeros_and_poles,
    "rational_inequality_schema.split_intervals_by_critical_points": gen_split_intervals_by_critical_points,
    "rational_inequality_schema.sign_chart_for_fraction": gen_sign_chart_for_fraction,
    "rational_inequality_schema.exclude_denominator_zeros": gen_exclude_denominator_zeros,
    "rational_inequality_schema.interval_solution_with_open_closed_endpoints": gen_interval_solution_with_open_closed_endpoints,
}
