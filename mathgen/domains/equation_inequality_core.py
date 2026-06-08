"""equation_inequality_core domain (design.md sec 3, 4).

Linear equations (one-step, multi-step, parentheses, variable-on-both-sides)
and linear inequalities. Equations are checked by back-substitution; inequalities
are checked by comparing the rendered solution set against sympy's solveset.

The inequality generators always state explicitly when multiplying/dividing by a
negative number flips the inequality sign (des_instruct.md sec 3.2).
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any, Dict, List

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import (
    fmt_add,
    fmt_fraction,
    fmt_linear,
    fmt_mul,
    fmt_poly,
    fmt_signed_term,
    fmt_sub,
    fmt_value,
    paren_if_negative,
)
from mathgen.verify import X, check_solution, interval_set, linear_solution_set, sets_equal, to_sympy_rational


def _nonzero(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def _ans_eq(value: Fraction) -> str:
    return f"x={fmt_fraction(value)}"


def gen_one_step_linear(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 40}[diff]
    if rng.random() < 0.5:
        # x + b = c
        b = _nonzero(rng, -hi, hi)
        sol = Fraction(rng.randint(-hi, hi))
        c = sol + b
        lhs_str = fmt_linear(1, b)
        op_word = "subtract" if b > 0 else "add"
        moved = abs(b)
        trace = [
            TraceStep(op="isolate_variable", text=f"To isolate x, {op_word} {moved} on both sides of {lhs_str} = {fmt_value(c)}."),
            TraceStep(op="simplify", text=f"This gives x = {fmt_value(c)} {'-' if b > 0 else '+'} {moved} = {fmt_fraction(sol)}."),
            TraceStep(op="state_solution", text=f"So the solution is {_ans_eq(sol)}.", after=_ans_eq(sol)),
        ]
        lhs, rhs = X + b, c
        user = f"Solve {lhs_str} = {fmt_value(c)} for x."
    else:
        # a x = c
        a = _nonzero(rng, 2, hi)
        sol = Fraction(rng.randint(-hi, hi))
        c = a * sol
        trace = [
            TraceStep(op="isolate_variable", text=f"To isolate x, divide both sides of {a}x = {fmt_value(c)} by {a}."),
            TraceStep(op="simplify", text=f"This gives x = {fmt_value(c)}/{a} = {fmt_fraction(sol)}."),
            TraceStep(op="state_solution", text=f"So the solution is {_ans_eq(sol)}.", after=_ans_eq(sol)),
        ]
        lhs, rhs = a * X, c
        user = f"Solve {a}x = {fmt_value(c)} for x."
    return make_sample(
        "equation.one_step_linear",
        user,
        trace,
        _ans_eq(sol),
        {"solution": fmt_fraction(sol), "difficulty": diff},
        verified=check_solution(lhs, rhs, [sol]),
    )


def gen_multi_step_linear(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 25}[diff]
    a = _nonzero(rng, 2, hi)
    b = _nonzero(rng, -hi, hi)
    sol = Fraction(rng.randint(-hi, hi))
    c = a * sol + b
    lhs_str = fmt_linear(a, b)
    moved = abs(b)
    step1_op = "Subtract" if b > 0 else "Add"
    after_const = c - b
    trace = [
        TraceStep(op="move_constant", text=f"{step1_op} {moved} on both sides of {lhs_str} = {fmt_value(c)} to get {a}x = {fmt_value(after_const)}.", meta={"a": a, "b": b, "rhs": fmt_value(after_const)}),
        TraceStep(op="divide_by_coefficient", text=f"Divide both sides by {a}: x = {fmt_value(after_const)}/{a} = {fmt_fraction(sol)}."),
        TraceStep(op="state_solution", text=f"So the solution is {_ans_eq(sol)}.", after=_ans_eq(sol)),
    ]
    return make_sample(
        "equation.multi_step_linear",
        f"Solve {lhs_str} = {fmt_value(c)} for x.",
        trace,
        _ans_eq(sol),
        {"a": a, "b": b, "solution": fmt_fraction(sol), "difficulty": diff},
        verified=check_solution(a * X + b, c, [sol]),
    )


def gen_equation_with_parentheses(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 18}[diff]
    a = _nonzero(rng, 2, hi)
    b = _nonzero(rng, -hi, hi)
    sol = Fraction(rng.randint(-hi, hi))
    # a (x + b) = c
    c = a * (sol + b)
    inner = fmt_linear(1, b)
    ab = a * b
    after_const = c - ab
    trace = [
        TraceStep(op="distribute", text=f"Distribute {a} over ({inner}): {a}x + {a}×{b if b >= 0 else f'({b})'} = {fmt_value(c)}, i.e. {fmt_linear(a, ab)} = {fmt_value(c)}.", meta={"a": a, "b": b}),
        TraceStep(op="move_constant", text=f"{'Subtract' if ab > 0 else 'Add'} {abs(ab)} on both sides to get {a}x = {fmt_value(after_const)}.", meta={"rhs": fmt_value(after_const)}),
        TraceStep(op="divide_by_coefficient", text=f"Divide both sides by {a}: x = {fmt_value(after_const)}/{a} = {fmt_fraction(sol)}."),
        TraceStep(op="state_solution", text=f"So the solution is {_ans_eq(sol)}.", after=_ans_eq(sol)),
    ]
    return make_sample(
        "equation.equation_with_parentheses",
        f"Solve {a}({inner}) = {fmt_value(c)} for x.",
        trace,
        _ans_eq(sol),
        {"a": a, "b": b, "solution": fmt_fraction(sol), "difficulty": diff},
        verified=check_solution(a * (X + b), c, [sol]),
    )


def gen_variable_on_both_sides(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    a = _nonzero(rng, -hi, hi)
    d = _nonzero(rng, -hi, hi)
    while a == d:
        d = _nonzero(rng, -hi, hi)
    b = _nonzero(rng, -hi, hi)
    sol = Fraction(rng.randint(-hi, hi))
    # a x + b = d x + e  =>  e = a*sol + b - d*sol  (integer, since sol is an integer)
    e = int(a * sol + b - d * sol)
    left = fmt_linear(a, b)
    right = fmt_linear(d, e)
    coef = a - d
    const = e - b
    trace = [
        TraceStep(op="collect_variable_terms", text=f"Move the variable terms to one side: subtract {fmt_linear(d, 0)} from both sides of {left} = {right} to get {fmt_linear(coef, b)} = {fmt_value(e)}.", meta={"coef": coef}),
        TraceStep(op="move_constant", text=f"{'Subtract' if b > 0 else 'Add'} {abs(b)} on both sides to get {fmt_linear(coef, 0)} = {fmt_value(const)}.", meta={"rhs": fmt_value(const)}),
        TraceStep(op="divide_by_coefficient", text=f"Divide both sides by {coef}: x = {fmt_value(const)}/{paren_if_negative(coef)} = {fmt_fraction(sol)}."),
        TraceStep(op="state_solution", text=f"So the solution is {_ans_eq(sol)}.", after=_ans_eq(sol)),
    ]
    return make_sample(
        "equation.variable_on_both_sides",
        f"Solve {left} = {right} for x.",
        trace,
        _ans_eq(sol),
        {"a": a, "b": b, "d": d, "e": e, "solution": fmt_fraction(sol), "difficulty": diff},
        verified=check_solution(a * X + b, d * X + e, [sol]),
    )


_FLIP = {">": "<", "<": ">", ">=": "<=", "<=": ">="}


def gen_linear_inequality(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 9, Difficulty.MEDIUM: 18, Difficulty.HARD: 30}[diff]
    a = _nonzero(rng, -hi, hi)
    b = _nonzero(rng, -hi, hi)
    c = rng.randint(-hi, hi)
    op = rng.choice([">", "<", ">=", "<="])
    lhs_str = fmt_linear(a, b)

    # a x + b OP c  ->  a x OP c - b  ->  x OP' (c-b)/a
    rhs_after = c - b
    value = Fraction(rhs_after, a)
    final_op = _FLIP[op] if a < 0 else op

    move_step = TraceStep(
        op="move_constant",
        text=f"{'Subtract' if b > 0 else 'Add'} {abs(b)} on both sides of {lhs_str} {op} {c} to get {a}x {op} {rhs_after}.",
        meta={"rhs": rhs_after},
    )
    if a < 0:
        divide_step = TraceStep(
            op="divide_by_negative_flip",
            text=f"Divide both sides by {a}. Because {a} is negative, flip the inequality sign: x {final_op} {fmt_value(rhs_after)}/{paren_if_negative(a)} = {fmt_fraction(value)}.",
            meta={"divisor": a, "flipped": True, "final_op": final_op},
            after=f"x {final_op} {fmt_fraction(value)}",
        )
    else:
        divide_step = TraceStep(
            op="divide_by_positive",
            text=f"Divide both sides by {a}. Since {a} is positive, keep the inequality sign: x {final_op} {fmt_value(rhs_after)}/{a} = {fmt_fraction(value)}.",
            meta={"divisor": a, "flipped": False, "final_op": final_op},
            after=f"x {final_op} {fmt_fraction(value)}",
        )
    answer = f"x {final_op} {fmt_fraction(value)}"
    state_step = TraceStep(op="state_solution", text=f"So the solution is {answer}.", after=answer)
    trace = [move_step, divide_step, state_step]

    # Verify: independently solve and compare solution sets.
    actual = linear_solution_set(a, b - c, op)
    if final_op in (">", ">="):
        expected = interval_set(value, None, low_open=(final_op == ">"), high_open=True)
    else:
        expected = interval_set(None, value, low_open=True, high_open=(final_op == "<"))

    return make_sample(
        "inequality.linear_inequality",
        f"Solve {lhs_str} {op} {c}.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "operator": op, "final_op": final_op, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def _fmt_xy(a: int, b: int) -> str:
    """Render an ``a x + b y`` left-hand side cleanly (both coefficients nonzero)."""
    return fmt_signed_term(a, "x", first=True) + fmt_signed_term(b, "y", first=False)


def gen_systems_linear_2x2(rng: random.Random, cfg: GenConfig) -> Sample:
    """Solve a 2x2 linear system by elimination (design.md sec 3.5).

    Built from an integer solution (x0, y0); every elimination/back-substitution
    step is shown, so the boxed solution is fully derived.
    """
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    sol_hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]

    for _ in range(10_000):
        a1 = rng.randint(1, hi)
        a2 = rng.randint(1, hi)
        b1 = _nonzero(rng, -hi, hi)
        b2 = _nonzero(rng, -hi, hi)
        det = a1 * b2 - a2 * b1
        if det != 0:
            break
    else:
        a1, b1, a2, b2, det = 1, 1, 1, -1, -2
    x0 = rng.randint(-sol_hi, sol_hi)
    y0 = rng.randint(-sol_hi, sol_hi)
    c1 = a1 * x0 + b1 * y0
    c2 = a2 * x0 + b2 * y0

    eq1 = f"{_fmt_xy(a1, b1)} = {c1}"
    eq2 = f"{_fmt_xy(a2, b2)} = {c2}"

    # Eliminate x: multiply eq1 by a2 and eq2 by a1 (both positive), then subtract.
    s1 = f"{_fmt_xy(a1 * a2, b1 * a2)} = {c1 * a2}"
    s2 = f"{_fmt_xy(a1 * a2, b2 * a1)} = {c2 * a1}"
    cy = b1 * a2 - b2 * a1  # = -det != 0
    rhs_y = c1 * a2 - c2 * a1  # = cy * y0

    # Back-substitute y0 into equation 1.
    const_from_y = b1 * y0
    rhs_x = c1 - const_from_y  # = a1 * x0

    # Avoid "+ (-N)×M" and "×-M" dirty patterns (des_instruct.md sec 5).
    sub_sign = " + " if const_from_y >= 0 else " - "
    sub_term = f"{abs(b1)}×{paren_if_negative(y0)}"
    sub_text = f"Substitute y={y0} into equation (1): {fmt_signed_term(a1, 'x', first=True)}{sub_sign}{sub_term} = {c1}, i.e. {fmt_signed_term(a1, 'x', first=True)} {'+' if const_from_y >= 0 else '-'} {abs(const_from_y)} = {c1}."

    answer = f"x={x0}, y={y0}"
    trace = [
        TraceStep(op="label_equations", text=f"Label the equations: (1) {eq1} and (2) {eq2}."),
        TraceStep(op="scale_for_elimination", text=f"To eliminate x, multiply equation (1) by {a2} and equation (2) by {a1}: (1') {s1} and (2') {s2}.", meta={"mult1": a2, "mult2": a1}),
        TraceStep(op="subtract_equations", text=f"Subtract (2') from (1'): the x-terms cancel, leaving {fmt_signed_term(cy, 'y', first=True)} = {rhs_y}.", meta={"cy": cy, "rhs_y": rhs_y}),
        TraceStep(op="solve_for_y", text=f"Divide both sides by {cy}: y = {rhs_y}/{paren_if_negative(cy)} = {y0}.", meta={"y": y0}),
        TraceStep(op="back_substitute", text=sub_text, meta={"const_from_y": const_from_y}),
        TraceStep(op="solve_for_x", text=f"So {fmt_signed_term(a1, 'x', first=True)} = {fmt_sub(c1, const_from_y)} = {rhs_x}, giving x = {rhs_x}/{a1} = {x0}.", meta={"x": x0}),
        TraceStep(op="state_solution", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "equation.systems_linear_2x2",
        f"Solve the system: {eq1}; {eq2}.",
        trace,
        answer,
        {"a1": a1, "b1": b1, "c1": c1, "a2": a2, "b2": b2, "c2": c2, "solution": [x0, y0], "difficulty": diff},
        verified=(c1 == a1 * x0 + b1 * y0 and c2 == a2 * x0 + b2 * y0 and cy == b1 * a2 - b2 * a1 and rhs_y == cy * y0),
    )


def gen_quadratic_formula(rng: random.Random, cfg: GenConfig) -> Sample:
    """Solve a quadratic with the quadratic formula (design.md sec 3.7).

    The discriminant is a perfect square so the roots are rational; allowing
    a != 1 makes the roots genuinely fractional, beyond integer factoring.
    """
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    for _ in range(10_000):
        a = rng.randint(1, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 5}[diff])
        b = _nonzero(rng, -2 * hi, 2 * hi)
        c = rng.randint(-hi * hi, hi * hi)
        disc = b * b - 4 * a * c
        if disc < 0:
            continue
        k = int(round(disc**0.5))
        if k * k != disc:
            continue
        x1 = Fraction(-b + k, 2 * a)
        x2 = Fraction(-b - k, 2 * a)
        break
    else:
        a, b, c, disc, k = 1, -3, 2, 1, 1
        x1, x2 = Fraction(2), Fraction(1)

    nb = -b
    expr = fmt_poly([(a, 2), (b, 1), (c, 0)])
    roots = sorted({x1, x2})
    if len(roots) == 1:
        answer = f"x={fmt_fraction(roots[0])}"
        finish_text = f"So the only solution is {answer}."
    else:
        answer = f"x={fmt_fraction(roots[0])} or x={fmt_fraction(roots[1])}"
        finish_text = f"So the solutions are {answer}."

    trace = [
        TraceStep(op="identify_coefficients", text=f"Identify the coefficients: a={a}, b={b}, c={c}."),
        TraceStep(op="state_formula", text="Apply the quadratic formula x = (-b ± sqrt(b^2 - 4ac)) / (2a)."),
        TraceStep(op="compute_discriminant", text=f"Compute the discriminant: {paren_if_negative(b)}^2 - 4×{a}×{paren_if_negative(c)} = {disc}.", meta={"discriminant": disc}),
        TraceStep(op="square_root", text=f"Since {disc} = {k}^2, sqrt({disc}) = {k}."),
        TraceStep(op="substitute_formula", text=f"Substitute: x = ({nb} ± {k}) / {2 * a}.", meta={"neg_b": nb, "two_a": 2 * a}),
        TraceStep(op="root_plus", text=f"Taking +: x = ({fmt_add(nb, k)})/{2 * a} = {fmt_fraction(x1)}.", after=f"x={fmt_fraction(x1)}"),
        TraceStep(op="root_minus", text=f"Taking -: x = ({fmt_sub(nb, k)})/{2 * a} = {fmt_fraction(x2)}.", after=f"x={fmt_fraction(x2)}"),
        TraceStep(op="state_solution", text=finish_text, after=answer),
    ]
    roots_sympy = [to_sympy_rational(x1), to_sympy_rational(x2)]
    return make_sample(
        "equation.quadratic_formula",
        f"Use the quadratic formula to solve {expr} = 0.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "discriminant": disc, "roots": [fmt_fraction(r) for r in roots], "difficulty": diff},
        verified=check_solution(a * X**2 + b * X + c, sp.Integer(0), roots_sympy),
    )


# -----------------------------------------------------------------------------
# Missing equation generators (added per coverage review)
# -----------------------------------------------------------------------------


def gen_linear_equation_fraction_coeff(rng: random.Random, cfg: GenConfig) -> Sample:
    """Solve a linear equation with fractional coefficients (e.g. (2/3)x + 1/2 = 5/6)."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]

    # Build from the solution: (p/q)x + (b/c) = rhs, with x = sol.
    p = _nonzero(rng, 1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff])
    q = rng.randint(2, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 12}[diff])
    while math.gcd(p, q) != 1:
        p = _nonzero(rng, 1, 8)
    coef_frac = Fraction(p, q)

    sol = Fraction(rng.randint(-hi, hi))

    # Const term as a fraction b/c with clean denominators.
    b_const = _nonzero(rng, -hi, hi)
    c_const = rng.randint(2, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 12}[diff])
    while math.gcd(abs(b_const), c_const) != 1:
        b_const = _nonzero(rng, -hi, hi)
    const_frac = Fraction(b_const, c_const)

    # rhs = coef * sol + const (so sol is a true solution)
    rhs = coef_frac * sol + const_frac

    # Use lcm for clear display step.
    denoms = [q, c_const, rhs.denominator]
    lcd = 1
    for d in denoms:
        lcd = lcd * d // math.gcd(lcd, d)

    lhs_scaled = Fraction(p * lcd, q)
    const_scaled = const_frac * lcd
    rhs_scaled = rhs * lcd

    trace = [
        TraceStep(op="multiply_by_lcd", text=f"The equation has fractions with denominators {q}, {c_const}, and {rhs.denominator}. Multiply both sides by lcd={lcd}."),
        TraceStep(op="clear_fractions", text=f"This gives {fmt_fraction(lhs_scaled)}x {fmt_signed_term(const_scaled, '', first=False)} = {fmt_fraction(rhs_scaled)}."),
        TraceStep(op="move_constant", text=f"{'Subtract' if const_scaled > 0 else 'Add'} {fmt_fraction(abs(const_scaled))} on both sides: {fmt_fraction(lhs_scaled)}x = {fmt_fraction(rhs_scaled - const_scaled)}."),
        TraceStep(op="divide_by_coefficient", text=f"Divide by {fmt_fraction(lhs_scaled)}: x = {fmt_fraction(Fraction(rhs_scaled - const_scaled, lhs_scaled))}."),
        TraceStep(op="state_solution", text=f"So the solution is x={fmt_fraction(sol)}.", after=f"x={fmt_fraction(sol)}"),
    ]
    lhs = X * coef_frac + const_frac
    return make_sample(
        "equation.linear_equation_fraction_coeff",
        f"Solve {fmt_fraction(coef_frac)}x {fmt_signed_term(const_frac, '', first=False)} = {fmt_fraction(rhs)}.",
        trace,
        f"x={fmt_fraction(sol)}",
        {"coef": str(coef_frac), "const": str(const_frac), "rhs": str(rhs), "lcd": lcd, "difficulty": diff},
        verified=check_solution(lhs, rhs, [to_sympy_rational(sol)]),
    )


def gen_system_substitution_method(rng: random.Random, cfg: GenConfig) -> Sample:
    """Solve a 2×2 linear system using the substitution method."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff]
    sol_hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff]

    # Build a system where eq1 is already solved for y: y = mx + c1
    m = _nonzero(rng, -hi, hi)
    x0 = rng.randint(-sol_hi, sol_hi)
    y0 = rng.randint(-sol_hi, sol_hi)
    c1 = y0 - m * x0

    # eq2: ax + by = c2
    a = _nonzero(rng, -hi, hi)
    b = _nonzero(rng, -hi, hi)
    c2 = a * x0 + b * y0

    eq1_str = f"y = {fmt_linear(m, c1)}"
    eq2_str = f"{_fmt_xy(a, b)} = {c2}"

    # Substitution: replace y in eq2 with m*x + c1
    sub_expr = a * X + b * (m * X + c1)
    coef_x = a + b * m
    const_val = b * c1
    rhs_x = c2 - const_val  # coef_x * x0

    answer = f"x={x0}, y={y0}"
    # Avoid "+ -5" dirty pattern when b is negative.
    b_str = f" + {b}" if b >= 0 else f" - {abs(b)}"
    trace = [
        TraceStep(op="label_equations", text=f"Equation (1) is {eq1_str}. Equation (2) is {eq2_str}."),
        TraceStep(op="substitute", text=f"Substitute y from (1) into (2): {a}x{b_str}({fmt_linear(m, c1)}) = {c2}."),
        TraceStep(op="distribute", text=f"Distribute: {a}x {fmt_signed_term(b * m, 'x', first=False)} {fmt_signed_term(const_val, '', first=False)} = {c2}."),
        TraceStep(op="collect", text=f"Collect x terms: {fmt_linear(coef_x, const_val)} = {c2}."),
        TraceStep(op="move_constant", text=f"Move constant: {fmt_linear(coef_x, 0)} = {rhs_x}."),
        TraceStep(op="solve_for_x", text=f"Divide by {coef_x}: x = {x0}."),
        TraceStep(op="back_substitute", text=f"Substitute x={x0} into (1): y = {m}×{paren_if_negative(x0)} {fmt_signed_term(c1, '', first=False)} = {y0}."),
        TraceStep(op="state_solution", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "equation.system_substitution_method",
        f"Solve the system {eq1_str}; {eq2_str}.",
        trace,
        answer,
        {"m": m, "c1": c1, "a": a, "b": b, "c2": c2, "solution": [x0, y0], "difficulty": diff},
        verified=(y0 == m * x0 + c1 and a * x0 + b * y0 == c2),
    )


def gen_completing_the_square(rng: random.Random, cfg: GenConfig) -> Sample:
    """Solve x²+bx+c=0 by completing the square."""
    diff = pick_difficulty(rng, cfg)
    # Construct from roots to guarantee clean solution.
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    r1 = rng.randint(-hi, hi)
    r2 = rng.randint(-hi, hi)
    b_total = -(r1 + r2)
    c_const = r1 * r2

    half_b = Fraction(b_total, 2)
    half_b_sq = half_b**2
    # (x + half_b)² = half_b² - c
    rhs_sq = half_b_sq - Fraction(c_const)

    expr = fmt_poly([(1, 2), (b_total, 1), (c_const, 0)])
    if r1 == r2:
        answer = f"x={fmt_fraction(Fraction(r1))}"
    else:
        roots = sorted({r1, r2})
        answer = f"x={fmt_fraction(Fraction(roots[0]))} or x={fmt_fraction(Fraction(roots[1]))}"

    trace = [
        TraceStep(op="move_constant", text=f"Move the constant {c_const} to the right side: x² {fmt_signed_term(b_total, 'x', first=False)} = {-c_const}."),
        TraceStep(op="half_coefficient", text=f"Take half the coefficient of x: {half_b}. Its square is {fmt_fraction(half_b_sq)}."),
        TraceStep(op="add_to_both_sides", text=f"Add {fmt_fraction(half_b_sq)} to both sides: x² {fmt_signed_term(b_total, 'x', first=False)} + {fmt_fraction(half_b_sq)} = {fmt_fraction(rhs_sq)}."),
        TraceStep(op="write_square", text=f"The left side becomes a perfect square: (x {fmt_signed_term(half_b, '', first=False)})² = {fmt_fraction(rhs_sq)}."),
    ]
    if rhs_sq == 0:
        trace.append(TraceStep(op="solve", text=f"Take square root: x {fmt_signed_term(half_b, '', first=False)} = 0, so x = {fmt_fraction(Fraction(r1))}."))
    else:
        sqrt_rhs = Fraction(abs(r1 - r2), 2)  # sqrt(rhs_sq) = |r1 - r2| / 2
        trace.append(TraceStep(op="take_square_root", text=f"Take square root on both sides: x {fmt_signed_term(half_b, '', first=False)} = ±{fmt_fraction(sqrt_rhs)}."))
        trace.append(TraceStep(op="solve", text=f"So x = {fmt_fraction(Fraction(-half_b - sqrt_rhs))} or x = {fmt_fraction(Fraction(-half_b + sqrt_rhs))}."))
    trace.append(TraceStep(op="state_solution", text=f"So the solutions are {answer}.", after=answer))

    roots_sympy = [to_sympy_rational(Fraction(r1)), to_sympy_rational(Fraction(r2))]
    return make_sample(
        "equation.completing_the_square",
        f"Solve {expr} = 0 by completing the square.",
        trace,
        answer,
        {"b": b_total, "c": c_const, "half_b": fmt_fraction(half_b), "roots": [r1, r2], "difficulty": diff},
        verified=check_solution(X**2 + b_total * X + c_const, sp.Integer(0), roots_sympy),
    )


REGISTRY: Dict[str, Any] = {
    "equation.one_step_linear": gen_one_step_linear,
    "equation.multi_step_linear": gen_multi_step_linear,
    "equation.equation_with_parentheses": gen_equation_with_parentheses,
    "equation.variable_on_both_sides": gen_variable_on_both_sides,
    "equation.systems_linear_2x2": gen_systems_linear_2x2,
    "equation.quadratic_formula": gen_quadratic_formula,
    "inequality.linear_inequality": gen_linear_inequality,
    "equation.linear_equation_fraction_coeff": gen_linear_equation_fraction_coeff,
    "equation.system_substitution_method": gen_system_substitution_method,
    "equation.completing_the_square": gen_completing_the_square,
}
