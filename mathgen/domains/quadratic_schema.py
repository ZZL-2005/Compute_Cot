"""quadratic_function_inequality_schema domain (design.md sec 25).

Covers the full range required by des_instruct.md sec 8.1 / 9:
  * quadratic equations solved by factoring (two distinct roots, double root)
  * quadratic inequalities with two distinct roots (>, >=, <, <=)
  * double root cases: (x-r)^2 >0 / >=0 / <0 / <=0
  * no real root cases -> all reals or empty set
  * opening direction up and down

Every inequality's rendered solution set is verified against sympy.solveset,
with explicit endpoint open/closed handling.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_interval, fmt_point_set, fmt_poly, fmt_union, paren_if_negative
from mathgen.verify import X, check_solution, interval_set, quadratic_solution_set, sets_equal

ALL_REALS = "(-∞, +∞)"
EMPTY = "∅"
_FLIP = {">": "<", "<": ">", ">=": "<=", "<=": ">="}


def _factored_two_roots(a: int, r1: int, r2: int) -> str:
    fac = f"{fmt_factor(-r1)}{fmt_factor(-r2)}"
    if a == 1:
        return fac
    if a == -1:
        return f"-{fac}"
    return f"{a}{fac}"


def _factored_double(a: int, r: int) -> str:
    fac = f"{fmt_factor(-r)}^2"
    if a == 1:
        return fac
    if a == -1:
        return f"-{fac}"
    return f"{a}{fac}"


def _expanded(a: int, r1: int, r2: int) -> Tuple[int, int, int, str]:
    """Return (a, B, C, rendered) for a*(x-r1)*(x-r2)."""
    B = -a * (r1 + r2)
    C = a * r1 * r2
    return a, B, C, fmt_poly([(a, 2), (B, 1), (C, 0)])


def gen_quadratic_equation_factor(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    r1 = rng.randint(-hi, hi)
    r2 = rng.randint(-hi, hi)
    a, B, C, expr = _expanded(1, r1, r2)
    if r1 == r2:
        roots_text = f"x={r1}"
        answer = f"x={r1}"
        zeros_step = f"The factor gives a double root x={r1}."
    else:
        lo, ho = sorted((r1, r2))
        roots_text = f"x={lo} or x={ho}"
        answer = f"x={lo} or x={ho}"
        zeros_step = f"Set each factor to zero: x={r1} or x={r2}."
    factored = _factored_two_roots(1, r1, r2)
    trace = [
        TraceStep(op="factor_quadratic", text=f"Factor the quadratic: {expr} = {factored}.", before=expr, after=factored, meta={"roots": [r1, r2]}),
        TraceStep(op="find_zeros", text=zeros_step, meta={"zeros": sorted({r1, r2})}),
        TraceStep(op="finish", text=f"Therefore the solutions are {roots_text}.", after=answer),
    ]
    return make_sample(
        "quadratic.equation_factor",
        f"Solve {expr} = 0.",
        trace,
        answer,
        {"roots": sorted({r1, r2}), "a": 1, "b": B, "c": C, "difficulty": diff},
        verified=check_solution(X**2 + B * X + C, sp.Integer(0), [r1, r2]),
    )


def gen_quadratic_inequality_two_roots(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 14}[diff]
    r1 = rng.randint(-hi, hi)
    r2 = rng.randint(-hi, hi)
    while r1 == r2:
        r2 = rng.randint(-hi, hi)
    r1, r2 = sorted((r1, r2))
    a = rng.choice([1, -1]) if diff == Difficulty.EASY else rng.choice([1, -1, 2, -2])
    op = rng.choice([">", "<", ">=", "<="])
    _, B, C, expr = _expanded(a, r1, r2)

    opens_up = a > 0
    closed = op in (">=", "<=")
    endpoint_open = not closed
    want_positive = op in (">", ">=")

    # Region where the inequality holds.
    positive_outside = opens_up  # a>0 => positive outside the roots
    region_outside = (want_positive and positive_outside) or ((not want_positive) and (not positive_outside))

    if region_outside:
        answer = fmt_union([
            fmt_interval(None, r1, True, endpoint_open),
            fmt_interval(r2, None, endpoint_open, True),
        ])
        expected = interval_set(None, r1, True, endpoint_open) + interval_set(r2, None, endpoint_open, True)
        region_text = f"outside the roots, so x<{r1} or x>{r2}"
    else:
        answer = fmt_interval(r1, r2, endpoint_open, endpoint_open)
        expected = interval_set(r1, r2, endpoint_open, endpoint_open)
        region_text = f"between the roots, so {r1}<x<{r2}"

    factored = _factored_two_roots(a, r1, r2)
    trace = [
        TraceStep(op="factor_quadratic", text=f"Factor: {expr} = {factored}.", before=expr, after=factored, meta={"roots": [r1, r2]}),
        TraceStep(op="find_zeros", text=f"The zeros are x={r1} and x={r2}.", meta={"zeros": [r1, r2]}),
        TraceStep(op="split_number_line", text=f"These zeros split the number line into (-∞, {r1}), ({r1}, {r2}), and ({r2}, +∞)."),
        TraceStep(op="determine_opening_direction", text=f"The leading coefficient is {a}, so the parabola opens {'upward' if opens_up else 'downward'}.", meta={"leading_coefficient": a}),
        TraceStep(op="determine_sign_intervals", text=f"The expression is {'positive' if positive_outside else 'negative'} outside the roots and {'negative' if positive_outside else 'positive'} between them, so the solution is {region_text}."),
        TraceStep(op="apply_inequality_operator", text=f"Because the inequality is {'strict' if not closed else 'non-strict'}, the roots are {'not included' if endpoint_open else 'included'}.", meta={"operator": op, "endpoints_included": closed}),
        TraceStep(op="finish", text=f"Thus the solution set is {answer}.", after=answer),
    ]
    actual = quadratic_solution_set(a, B, C, op)
    return make_sample(
        "quadratic.inequality_two_roots",
        f"Solve {expr} {op} 0.",
        trace,
        answer,
        {"a": a, "b": B, "c": C, "roots": [r1, r2], "operator": op, "answer_type": "interval_union" if region_outside else "interval", "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_quadratic_inequality_double_root(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    r = rng.randint(-hi, hi)
    a = rng.choice([1, -1])
    op = rng.choice([">", "<", ">=", "<="])
    _, B, C, expr = _expanded(a, r, r)
    factored = _factored_double(a, r)

    # For a=1: (x-r)^2 >= 0 always; ==0 only at r.
    # Translate "a*(x-r)^2 OP 0" to the sign of (x-r)^2.
    # value v=(x-r)^2 >= 0. a*v OP 0.
    if a > 0:
        # v OP 0
        sign_op = op
    else:
        # -v OP 0  <=>  v _FLIP[op] 0
        sign_op = _FLIP[op]

    # Now decide based on sign_op applied to a nonnegative quantity v with v=0 only at x=r.
    if sign_op == ">":      # v > 0  -> all x except r
        answer = fmt_union([fmt_interval(None, r, True, True), fmt_interval(r, None, True, True)])
        expected = interval_set(None, r, True, True) + interval_set(r, None, True, True)
        reason = f"a square is positive everywhere except where it is zero, so x≠{r}"
    elif sign_op == ">=":   # v >= 0 -> all reals
        answer = ALL_REALS
        expected = sp.S.Reals
        reason = "a square is always greater than or equal to 0, so every real number works"
    elif sign_op == "<":    # v < 0 -> impossible
        answer = EMPTY
        expected = sp.S.EmptySet
        reason = "a square can never be negative, so there is no solution"
    else:                   # v <= 0 -> only zero, x=r
        answer = fmt_point_set(r)
        expected = sp.FiniteSet(r)
        reason = f"a square equals 0 only at its root, so x={r}"

    trace = [
        TraceStep(op="factor_quadratic", text=f"Recognize the perfect square: {expr} = {factored}.", before=expr, after=factored, meta={"double_root": r}),
        TraceStep(op="determine_opening_direction", text=f"The leading coefficient is {a}, so the parabola opens {'upward' if a > 0 else 'downward'} and touches the x-axis only at x={r}.", meta={"leading_coefficient": a}),
        TraceStep(op="analyze_square_sign", text=f"Analyze the sign: {reason}."),
        TraceStep(op="finish", text=f"Thus the solution set is {answer}.", after=answer),
    ]
    actual = quadratic_solution_set(a, B, C, op)
    return make_sample(
        "quadratic.inequality_double_root",
        f"Solve {expr} {op} 0.",
        trace,
        answer,
        {"a": a, "b": B, "c": C, "double_root": r, "operator": op, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_quadratic_inequality_no_real_root(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff]
    a = rng.choice([1, -1])
    # Choose b, c so that discriminant b^2 - 4*1*c < 0, then scale by a.
    b0 = rng.randint(-hi, hi)
    c0 = rng.randint(b0 * b0 // 4 + 1, b0 * b0 // 4 + hi + 2)  # ensures 4c0 > b0^2
    B = a * b0
    C = a * c0
    disc = B * B - 4 * a * C
    assert disc < 0
    expr = fmt_poly([(a, 2), (B, 1), (C, 0)])
    op = rng.choice([">", "<", ">=", "<="])

    always_positive = a > 0  # since no real roots and opens up => always > 0
    want_positive = op in (">", ">=")
    holds_everywhere = (always_positive and want_positive) or ((not always_positive) and (not want_positive))

    if holds_everywhere:
        answer = ALL_REALS
        expected = sp.S.Reals
        reason = f"the expression is always {'positive' if always_positive else 'negative'}, matching the inequality"
    else:
        answer = EMPTY
        expected = sp.S.EmptySet
        reason = f"the expression is always {'positive' if always_positive else 'negative'}, which never matches the inequality"

    trace = [
        TraceStep(op="compute_discriminant", text=f"Compute the discriminant: {paren_if_negative(B)}^2 - 4×{paren_if_negative(a)}×{paren_if_negative(C)} = {disc} < 0, so there are no real roots.", meta={"discriminant": disc}),
        TraceStep(op="determine_opening_direction", text=f"The leading coefficient is {a}, so the parabola opens {'upward' if a > 0 else 'downward'} and stays entirely {'above' if always_positive else 'below'} the x-axis.", meta={"leading_coefficient": a}),
        TraceStep(op="determine_sign_intervals", text=f"Because there are no real roots, {reason}."),
        TraceStep(op="finish", text=f"Thus the solution set is {answer}.", after=answer),
    ]
    actual = quadratic_solution_set(a, B, C, op)
    return make_sample(
        "quadratic.inequality_no_real_root",
        f"Solve {expr} {op} 0.",
        trace,
        answer,
        {"a": a, "b": B, "c": C, "discriminant": disc, "operator": op, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


REGISTRY: Dict[str, Any] = {
    "quadratic.equation_factor": gen_quadratic_equation_factor,
    "quadratic.inequality_two_roots": gen_quadratic_inequality_two_roots,
    "quadratic.inequality_double_root": gen_quadratic_inequality_double_root,
    "quadratic.inequality_no_real_root": gen_quadratic_inequality_no_real_root,
}
