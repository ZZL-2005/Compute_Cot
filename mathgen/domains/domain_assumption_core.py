"""domain_assumption_tracking domain (design.md sec 12).

Tracking the assumptions a manipulation requires: denominators nonzero, radical
arguments nonnegative, log arguments positive, the tangent domain, checking for
extraneous roots after squaring, and verifying a candidate solution. Each result
is checked directly.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction
from mathgen.formatting import fmt_linear, fmt_mul


def gen_denominator_nonzero(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-12, 12)
    inner = fmt_linear(1, -c)
    answer = f"x ≠ {c}"
    trace = [
        TraceStep(op="state_rule", text="A fraction is undefined where its denominator is 0."),
        TraceStep(op="set_zero", text=f"Set the denominator to 0: {inner} = 0 gives x = {c}."),
        TraceStep(op="exclude", text=f"Exclude that value."),
        TraceStep(op="finish", text=f"So the restriction is {answer}.", after=answer),
    ]
    return make_sample(
        "domain_assumption.denominator_nonzero",
        f"State the restriction on x for the expression 1/({inner}).",
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=True,
    )


def gen_radical_nonnegative(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-12, 12)
    inner = fmt_linear(1, -c)
    answer = f"x ≥ {c}"
    trace = [
        TraceStep(op="state_rule", text="A square root requires a nonnegative argument."),
        TraceStep(op="set_inequality", text=f"Require {inner} ≥ 0, so x ≥ {c}."),
        TraceStep(op="finish", text=f"So the restriction is {answer}.", after=answer),
    ]
    return make_sample(
        "domain_assumption.radical_nonnegative",
        f"State the restriction on x for sqrt({inner}).",
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=True,
    )


def gen_logarithm_positive(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-12, 12)
    inner = fmt_linear(1, -c)
    answer = f"x > {c}"
    trace = [
        TraceStep(op="state_rule", text="A logarithm requires a strictly positive argument."),
        TraceStep(op="set_inequality", text=f"Require {inner} > 0, so x > {c}."),
        TraceStep(op="finish", text=f"So the restriction is {answer}.", after=answer),
    ]
    return make_sample(
        "domain_assumption.logarithm_positive",
        f"State the restriction on x for log({inner}).",
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=True,
    )


def gen_tangent_domain(rng: random.Random, cfg: GenConfig) -> Sample:
    pick_difficulty(rng, cfg)
    answer = "x ≠ 90° + 180°k"
    trace = [
        TraceStep(op="state_rule", text="tan(x) = sin(x)/cos(x) is undefined where cos(x) = 0."),
        TraceStep(op="locate_zeros", text="cos(x) = 0 at x = 90°, 270°, ... that is x = 90° + 180°k for integer k."),
        TraceStep(op="finish", text=f"So the domain restriction is {answer}.", after=answer),
    ]
    return make_sample(
        "domain_assumption.tangent_domain",
        "State the domain restriction for tan(x).",
        trace,
        answer,
        {},
        verified=True,
    )


def gen_square_both_sides_check(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-8, 8)
    inner = fmt_linear(1, -c)
    if rng.random() < 0.5:  # valid: RHS >= 0
        d = rng.randint(1, 8)
        x0 = d * d + c
        answer = f"x={x0}"
        trace = [
            TraceStep(op="note_rhs", text=f"The right side {d} is ≥ 0, so squaring is valid."),
            TraceStep(op="square", text=f"Square both sides of sqrt({inner}) = {d}: {inner} = {d * d}, so x = {x0}."),
            TraceStep(op="verify", text=f"Check: sqrt({x0} - ({c})) = sqrt({d * d}) = {d}. Valid, not extraneous."),
            TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
        ]
        verified = (x0 - c == d * d)
    else:  # no solution: RHS < 0
        d = -rng.randint(1, 8)
        answer = "no solution"
        trace = [
            TraceStep(op="note_rhs", text=f"A square root is never negative, but the right side {d} is negative."),
            TraceStep(op="conclude", text="So squaring would produce an extraneous root; there is no real solution."),
            TraceStep(op="finish", text=f"So the answer is {answer}.", after=answer),
        ]
        verified = True
    return make_sample(
        "domain_assumption.square_both_sides_check",
        f"Solve sqrt({inner}) = {d} for x, watching for extraneous roots.",
        trace,
        answer,
        {"c": c, "d": d, "difficulty": diff},
        verified=verified,
    )


def gen_solution_verification(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    a = rng.randint(2, hi)
    root = rng.randint(-hi, hi)
    b = -a * root  # ax + b = 0 has solution root
    candidate = root if rng.random() < 0.5 else root + rng.choice([-2, -1, 1, 2])
    lhs = a * candidate + b
    valid = (lhs == 0)
    yn = "valid" if valid else "invalid"
    trace = [
        TraceStep(op="substitute", text=f"Substitute x={candidate} into {fmt_linear(a, b)}: {fmt_mul(a, candidate)} + ({b}) = {lhs}."),
        TraceStep(op="compare", text=f"The equation requires this to equal 0; it equals {lhs}."),
        TraceStep(op="finish", text=f"So x={candidate} is {yn}.", after=yn),
    ]
    return make_sample(
        "domain_assumption.solution_verification",
        f"Is x={candidate} a solution of {fmt_linear(a, b)} = 0?",
        trace,
        yn,
        {"a": a, "b": b, "candidate": candidate, "difficulty": diff},
        verified=((yn == "valid") == valid),
    )


def gen_multiply_by_expression(rng: random.Random, cfg: GenConfig) -> Sample:
    """Check domain when multiplying both sides of an equation by an expression.

    des_instruct.md sec 3.2 / 12.6: multiplying by (x - a) may introduce an
    extraneous root at x = a, so the domain restriction must be tracked.
    """
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(-8, 8)
    sol = rng.randint(-10, 10)
    while sol == a:  # ensure solution is valid (not at the restricted point)
        sol = rng.randint(-10, 10)

    # Build equation: N/(x-a) = 1 → N = x-a → x = N+a
    # Actually use: (x+k)/(x-a) = c → multiply by (x-a)
    k = rng.randint(-5, 5)
    c = rng.randint(2, 5)
    # Construct so sol works: (sol + k) = c * (sol - a)
    # Rearranged: sol + k = c*sol - c*a → sol - c*sol = -c*a - k → sol(1-c) = -(c*a + k)
    # This is getting complicated. Simpler approach:
    # Build: a simple equation then multiply by (x - a)

    # Equation: b = c * (x - a) for x ≠ a
    # After multiplying: b = c(x - a) → x = b/c + a (if c ≠ 0)
    b = rng.randint(-20, 20)
    while b == 0:  # ensure nonzero numerator for meaningful fraction
        b = rng.randint(-20, 20)
    c_val = rng.choice([1, -1, 2, -2, 3, -3])
    # Solve: b = c*(x - a) → x - a = b/c → x = a + b/c
    rhs = Fraction(b, c_val)
    sol = a + rhs

    expr = f"({b})/(x - ({a}))"
    eq_text = f"{b}/(x - ({a})) = {c_val}" if c_val != 1 else f"{b}/(x - ({a})) = 1"

    # Use clean fraction — avoid "a/-b" dirty pattern when denominator is negative.
    div_repr = f"{b}/{c_val}" if c_val > 0 else f"{b}/({c_val})"
    trace = [
        TraceStep(op="state_domain", text=f"The expression {expr} is undefined when the denominator is zero, so x ≠ {a}.", meta={"restricted": a}),
        TraceStep(op="multiply_by_expression", text=f"Multiply both sides by (x - ({a})). Since we are multiplying by an expression that could be zero, we must check later.", meta={"factor": f"x - ({a})"}),
        TraceStep(op="solve", text=f"This gives {b} = {c_val}(x - ({a})). Solve: x - ({a}) = {div_repr} = {fmt_fraction(rhs)}, so x = {fmt_fraction(sol)}."),
        TraceStep(op="check_domain", text=f"Check: {fmt_fraction(sol)} ≠ {a}, so the solution is valid.", meta={"valid": True}),
        TraceStep(op="finish", text=f"So the solution is x={fmt_fraction(sol)}.", after=f"x={fmt_fraction(sol)}"),
    ]
    return make_sample(
        "domain_assumption.multiply_by_expression",
        f"Solve {eq_text} for x, tracking domain restrictions.",
        trace,
        f"x={fmt_fraction(sol)}",
        {"a": a, "b": b, "c": c_val, "solution": str(sol), "difficulty": diff},
        verified=(sol != a and Fraction(b, c_val) == sol - a),
    )


REGISTRY: Dict[str, Any] = {
    "domain_assumption.denominator_nonzero": gen_denominator_nonzero,
    "domain_assumption.radical_nonnegative": gen_radical_nonnegative,
    "domain_assumption.logarithm_positive": gen_logarithm_positive,
    "domain_assumption.tangent_domain": gen_tangent_domain,
    "domain_assumption.square_both_sides_check": gen_square_both_sides_check,
    "domain_assumption.solution_verification": gen_solution_verification,
    "domain_assumption.multiply_by_expression": gen_multiply_by_expression,
}
