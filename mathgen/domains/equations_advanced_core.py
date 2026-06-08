"""equations_advanced domain (design.md sec 3.8-3.10).

Rational, radical, and absolute-value equations. Each is built from a known
solution and solved with explicit domain/validity checks, so the boxed answer
is fully justified. Solutions are verified by back-substitution.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_linear, paren_if_negative


def _nz(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def gen_rational_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    c = rng.randint(-hi, hi)
    d = _nz(rng, -6, 6)
    x0 = c + rng.choice([-1, 1]) * rng.randint(1, hi)  # x0 != c
    while x0 == c:
        x0 = c + rng.choice([-1, 1]) * rng.randint(1, hi)
    p = (x0 - c) * d  # so p/(x0-c) = d
    answer = f"x={x0}"
    trace = [
        TraceStep(op="state_domain", text=f"The denominator x - ({c}) cannot be 0, so x ≠ {c}."),
        TraceStep(op="clear_denominator", text=f"Multiply both sides by ({fmt_linear(1, -c)}): {p} = {d}({fmt_linear(1, -c)})."),
        TraceStep(op="solve_linear", text=f"So {fmt_linear(1, -c)} = {p}/{paren_if_negative(d)} = {x0 - c}, giving x = {x0 - c} + ({c}) = {x0}."),
        TraceStep(op="check_domain", text=f"Since {x0} ≠ {c}, the solution is valid."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "equation.rational_equation",
        f"Solve {p}/({fmt_linear(1, -c)}) = {d} for x.",
        trace,
        answer,
        {"p": p, "c": c, "d": d, "difficulty": diff},
        verified=(x0 != c and p == (x0 - c) * d),
    )


def gen_radical_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    d = rng.randint(1, {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff])
    c = rng.randint(-hi, hi)
    x0 = d * d - c  # sqrt(x0 + c) = d
    answer = f"x={x0}"
    inner = fmt_linear(1, c)
    trace = [
        TraceStep(op="state_condition", text=f"For sqrt({inner}) to be defined and equal to {d} ≥ 0, square both sides."),
        TraceStep(op="square", text=f"Squaring: {inner} = {d}^2 = {d * d}."),
        TraceStep(op="solve_linear", text=f"So x = {d * d} - ({c}) = {x0}."),
        TraceStep(op="check", text=f"Check: sqrt({x0} + ({c})) = sqrt({d * d}) = {d}, which matches."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "equation.radical_equation",
        f"Solve sqrt({inner}) = {d} for x.",
        trace,
        answer,
        {"c": c, "d": d, "difficulty": diff},
        verified=(x0 + c == d * d and d >= 0),
    )


def gen_absolute_value_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    c = rng.randint(-hi, hi)
    d = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    s1, s2 = sorted([c - d, c + d])
    inner = fmt_linear(1, -c)
    answer = f"x={s1} or x={s2}"
    trace = [
        TraceStep(op="state_rule", text=f"|{inner}| = {d} means {inner} = {d} or {inner} = -{d}."),
        TraceStep(op="case_positive", text=f"Case 1: {inner} = {d} gives x = {d} + ({c}) = {c + d}."),
        TraceStep(op="case_negative", text=f"Case 2: {inner} = -{d} gives x = -{d} + ({c}) = {c - d}."),
        TraceStep(op="finish", text=f"So the solutions are {answer}.", after=answer),
    ]
    return make_sample(
        "equation.absolute_value_equation",
        f"Solve |{inner}| = {d} for x.",
        trace,
        answer,
        {"c": c, "d": d, "difficulty": diff},
        verified=(abs(s1 - c) == d and abs(s2 - c) == d),
    )


REGISTRY: Dict[str, Any] = {
    "equation.rational_equation": gen_rational_equation,
    "equation.radical_equation": gen_radical_equation,
    "equation.absolute_value_equation": gen_absolute_value_equation,
}
