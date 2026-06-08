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
from fractions import Fraction
from typing import Any, Dict, List, Tuple

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_fraction, fmt_interval, fmt_point_set, fmt_poly, fmt_union, paren_if_negative
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


# ---------------------------------------------------------------------------
# Missing quadratic generators (design.md sec 25 gaps)
# ---------------------------------------------------------------------------


def gen_discriminant_classification(rng: random.Random, cfg: GenConfig) -> Sample:
    """Classify how many real roots a quadratic has based on its discriminant."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]

    # Build quadratic with known root count.
    case = rng.choice(["two", "double", "none"])
    a = rng.choice([1, -1, 2, -2]) if diff != Difficulty.EASY else rng.choice([1, -1])
    if case == "two":
        r1 = rng.randint(-hi, hi)
        r2 = rng.randint(-hi, hi)
        while r2 == r1:
            r2 = rng.randint(-hi, hi)
        B = -a * (r1 + r2)
        C = a * r1 * r2
        disc = B * B - 4 * a * C
        answer = "two distinct real roots"
        detail = f"Since Δ > 0, the quadratic has two distinct real roots, x = {min(r1, r2)} and x = {max(r1, r2)}."
    elif case == "double":
        r = rng.randint(-hi, hi)
        B = -2 * a * r
        C = a * r * r
        disc = 0
        answer = "one double real root"
        detail = f"Since Δ = 0, the quadratic has one double root, x = {r}."
    else:
        B = rng.randint(-hi, hi)
        # Choose C large enough so B^2 - 4aC < 0
        min_c = (B * B) // (4 * abs(a)) + 1
        C = rng.randint(min_c, min_c + hi)
        if a < 0:
            C = -C
        disc = B * B - 4 * a * C
        answer = "no real roots"
        detail = "Since Δ < 0, the quadratic has no real roots."

    expr = fmt_poly([(a, 2), (B, 1), (C, 0)])
    trace = [
        TraceStep(op="identify_coefficients", text=f"For {expr}, the coefficients are a={a}, b={B}, c={C}."),
        TraceStep(op="compute_discriminant", text=f"Compute the discriminant Δ = b² - 4ac = {paren_if_negative(B)}² - 4·{paren_if_negative(a)}·{paren_if_negative(C)} = {disc}.",
                  meta={"a": a, "b": B, "c": C, "discriminant": disc}),
        TraceStep(op="classify", text=detail, meta={"num_roots": case}),
        TraceStep(op="finish", text=f"So {expr} has {answer}.", after=answer),
    ]
    return make_sample(
        "quadratic.discriminant_classification",
        f"Classify the roots of {expr} = 0 using the discriminant.",
        trace,
        answer,
        {"a": a, "b": B, "c": C, "discriminant": disc, "difficulty": diff},
        verified=True,
    )


def gen_quadratic_vertex_axis_range(rng: random.Random, cfg: GenConfig) -> Sample:
    """Find the vertex, axis of symmetry, and range of a quadratic function."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a = rng.choice([1, -1]) if diff == Difficulty.EASY else rng.choice([1, -1, 2, -2, 3, -3])
    b = rng.randint(-hi, hi)
    c = rng.randint(-hi, hi)

    h = Fraction(-b, 2 * a)
    k = Fraction(4 * a * c - b * b, 4 * a)

    vertex = f"({fmt_fraction(h)}, {fmt_fraction(k)})"
    axis = f"x = {fmt_fraction(h)}"
    opens = "upward" if a > 0 else "downward"
    if a > 0:
        range_ans = fmt_interval(k, None, False, True)
    else:
        range_ans = fmt_interval(None, k, True, False)

    answer = f"vertex {vertex}, axis {axis}, range {range_ans}"
    expr = fmt_poly([(a, 2), (b, 1), (c, 0)])
    trace = [
        TraceStep(op="identify_coefficients", text=f"For f(x) = {expr}, a={a}, b={b}, c={c}."),
        TraceStep(op="vertex_x", text=f"The axis of symmetry is x = -b/(2a) = -({b})/(2·{a}) = {fmt_fraction(h)}."),
        TraceStep(op="vertex_y", text=f"Substitute into the function: the vertex y-coordinate is {fmt_fraction(k)}."),
        TraceStep(op="state_vertex", text=f"So the vertex is {vertex} and the axis of symmetry is {axis}.", after=vertex),
        TraceStep(op="range", text=f"Since a={a} {'>' if a > 0 else '<'} 0, the parabola opens {opens}, so the range is {range_ans}."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "quadratic.quadratic_vertex_axis_range",
        f"Find the vertex, axis of symmetry, and range of f(x) = {expr}.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "vertex": vertex, "axis": axis, "range": range_ans, "difficulty": diff},
        verified=True,
    )


def gen_quadratic_parameter_discriminant_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    """For what parameter k does the quadratic have 2/1/0 real roots?"""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]

    # Build: x² + bx + k = 0 or x² + kx + c = 0
    if rng.random() < 0.5:
        # x² + bx + k = 0 → discriminant = b² - 4k
        b_val = rng.randint(1, hi)
        # For 2 roots: k < b²/4. For 1 root: k = b²/4. For 0 roots: k > b²/4.
        target = rng.choice(["two", "one", "none"])
        if target == "two":
            k_val = Fraction(b_val * b_val, 4) - Fraction(rng.randint(1, hi), 1)
            answer = f"k < {Fraction(b_val * b_val, 4)}"
        elif target == "one":
            k_val = Fraction(b_val * b_val, 4)
            answer = f"k = {k_val}"
        else:
            k_val = Fraction(b_val * b_val, 4) + Fraction(rng.randint(1, hi), 1)
            answer = f"k > {Fraction(b_val * b_val, 4)}"
        expr = f"x² + {b_val}x + k"
    else:
        # x² + kx + c = 0 → discriminant = k² - 4c
        c_val = rng.randint(1, hi * hi)
        target = rng.choice(["two", "one", "none"])
        four_c = 4 * c_val
        if target == "two":
            k_val = rng.randint(int(four_c**0.5) + 1, int(four_c**0.5) + hi)
            answer = f"k < {-int(four_c**0.5)} or k > {int(four_c**0.5)}"
        elif target == "one":
            k_val = int(four_c**0.5)
            if k_val * k_val != four_c:
                # Adjust c to make it a perfect square
                k_val = rng.randint(2, hi)
                c_val = k_val * k_val // 4
                four_c = 4 * c_val
            answer = f"k = {-k_val} or k = {k_val}"
        else:
            k_val = rng.randint(0, int(four_c**0.5) - 1) if four_c > 0 else 0
            answer = f"{-int(four_c**0.5)} < k < {int(four_c**0.5)}"
        expr = f"x² + kx + {c_val}"

    trace = [
        TraceStep(op="identify_coefficients", text=f"For {expr} = 0, the coefficients are a=1, with k as a parameter."),
        TraceStep(op="write_discriminant", text=f"The discriminant is Δ = b² - 4ac."),
        TraceStep(op="set_condition", text=f"For {target} real root(s), the discriminant condition gives {answer}."),
        TraceStep(op="finish", text=f"So {expr} = 0 has {target} real root(s) when {answer}.", after=answer),
    ]
    return make_sample(
        "quadratic.quadratic_parameter_discriminant_basic",
        f"For which values of k does the equation {expr} = 0 have {target} real root(s)?",
        trace,
        answer,
        {"a": 1, "k_type": "parameter", "target": target, "difficulty": diff},
        verified=True,
    )


def gen_quadratic_sign_chart(rng: random.Random, cfg: GenConfig) -> Sample:
    """Create a sign chart for a quadratic expression to determine where it is positive/negative."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a = rng.choice([1, -1]) if diff == Difficulty.EASY else rng.choice([1, -1, 2, -2])
    r1 = rng.randint(-hi, hi)
    r2 = rng.randint(-hi, hi)
    while r2 == r1:
        r2 = rng.randint(-hi, hi)
    lo, hi_r = sorted((r1, r2))
    B = -a * (r1 + r2)
    C = a * r1 * r2
    expr = fmt_poly([(a, 2), (B, 1), (C, 0)])
    factored = _factored_two_roots(a, r1, r2)

    opens_up = a > 0
    trace = [
        TraceStep(op="factor_quadratic", text=f"Factor: {expr} = {factored}.", after=factored),
        TraceStep(op="find_zeros", text=f"The zeros are x={lo} and x={hi_r}."),
        TraceStep(op="split_number_line", text=f"These split the line into (-∞, {lo}), ({lo}, {hi_r}), and ({hi_r}, +∞)."),
        TraceStep(op="determine_opening", text=f"Since a={a} {'>' if opens_up else '<'} 0, the parabola opens {'upward' if opens_up else 'downward'}."),
        TraceStep(op="sign_chart", text=f"Sign chart: {'+' if opens_up else '-'} | {'-' if opens_up else '+'} | {'+' if opens_up else '-'} for the three intervals."),
    ]

    if a > 0:
        positive_on = f"(-∞, {lo}) ∪ ({hi_r}, +∞)"
        negative_on = f"({lo}, {hi_r})"
    else:
        positive_on = f"({lo}, {hi_r})"
        negative_on = f"(-∞, {lo}) ∪ ({hi_r}, +∞)"
    answer = f"positive on {positive_on}, negative on {negative_on}"
    trace.append(TraceStep(op="finish", text=f"So {expr} is {answer}.", after=answer))

    return make_sample(
        "quadratic.quadratic_sign_chart",
        f"Use a sign chart to find where {expr} is positive and where it is negative.",
        trace,
        answer,
        {"a": a, "b": B, "c": C, "roots": [lo, hi_r], "difficulty": diff},
        verified=True,
    )


def gen_quadratic_function_positive_negative_interval(rng: random.Random, cfg: GenConfig) -> Sample:
    """Find intervals where a quadratic function is positive or negative."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a = rng.choice([1, -1, 2, -2])
    r1 = rng.randint(-hi, hi)
    r2 = rng.randint(-hi, hi)
    while r2 == r1:
        r2 = rng.randint(-hi, hi)
    lo, hi_r = sorted((r1, r2))
    B = -a * (r1 + r2)
    C = a * r1 * r2
    expr = fmt_poly([(a, 2), (B, 1), (C, 0)])

    # Randomly ask for positive or negative interval
    ask_positive = rng.random() < 0.5
    opens_up = a > 0
    positive_outside = opens_up

    if ask_positive:
        if positive_outside:
            answer = fmt_union([fmt_interval(None, lo, True, True), fmt_interval(hi_r, None, True, True)])
        else:
            answer = fmt_interval(lo, hi_r, True, True)
    else:
        if positive_outside:
            answer = fmt_interval(lo, hi_r, True, True)
        else:
            answer = fmt_union([fmt_interval(None, lo, True, True), fmt_interval(hi_r, None, True, True)])

    trace = [
        TraceStep(op="find_zeros", text=f"Set {expr} = 0. The roots are x={lo} and x={hi_r}."),
        TraceStep(op="determine_opening", text=f"The leading coefficient is {a}, so the parabola opens {'upward' if opens_up else 'downward'}."),
        TraceStep(op="sign_analysis", text=f"A quadratic with a={'positive' if opens_up else 'negative'} leading coefficient is {'positive' if positive_outside else 'negative'} outside the roots and {'negative' if positive_outside else 'positive'} between them."),
        TraceStep(op="finish", text=f"So f(x) {'>' if ask_positive else '<'} 0 on {answer}.", after=answer),
    ]
    return make_sample(
        "quadratic.quadratic_function_positive_negative_interval",
        f"Find where f(x) = {expr} is {'positive' if ask_positive else 'negative'}.",
        trace,
        answer,
        {"a": a, "roots": [lo, hi_r], "ask_positive": ask_positive, "difficulty": diff},
        verified=True,
    )


REGISTRY: Dict[str, Any] = {
    "quadratic.equation_factor": gen_quadratic_equation_factor,
    "quadratic.inequality_two_roots": gen_quadratic_inequality_two_roots,
    "quadratic.inequality_double_root": gen_quadratic_inequality_double_root,
    "quadratic.inequality_no_real_root": gen_quadratic_inequality_no_real_root,
    "quadratic.discriminant_classification": gen_discriminant_classification,
    "quadratic.quadratic_vertex_axis_range": gen_quadratic_vertex_axis_range,
    "quadratic.quadratic_parameter_discriminant_basic": gen_quadratic_parameter_discriminant_basic,
    "quadratic.quadratic_sign_chart": gen_quadratic_sign_chart,
    "quadratic.quadratic_function_positive_negative_interval": gen_quadratic_function_positive_negative_interval,
}
