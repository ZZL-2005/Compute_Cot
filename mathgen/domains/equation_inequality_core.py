"""equation_inequality_core domain (design.md sec 3, 4).

Linear equations (one-step, multi-step, parentheses, variable-on-both-sides)
and linear inequalities. Equations are checked by back-substitution; inequalities
are checked by comparing the rendered solution set against sympy's solveset.

The inequality generators always state explicitly when multiplying/dividing by a
negative number flips the inequality sign (des_instruct.md sec 3.2).
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict, List

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction, fmt_linear, fmt_value, paren_if_negative
from mathgen.verify import X, check_solution, interval_set, linear_solution_set, sets_equal


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
            TraceStep(op="simplify", text=f"This gives x = {fmt_value(c)} {'-' if b > 0 else '+'} {moved} = {fmt_fraction(sol)}.", after=_ans_eq(sol)),
        ]
        lhs, rhs = X + b, c
        user = f"Solve {lhs_str} = {fmt_value(c)} for x."
    else:
        # a x = c
        a = _nonzero(rng, 2, hi)
        sol = Fraction(rng.randint(-hi, hi))
        c = a * sol
        trace = [
            TraceStep(op="isolate_variable", text=f"Divide both sides of {a}x = {fmt_value(c)} by {a}."),
            TraceStep(op="simplify", text=f"This gives x = {fmt_value(c)}/{a} = {fmt_fraction(sol)}.", after=_ans_eq(sol)),
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
        TraceStep(op="divide_by_coefficient", text=f"Divide both sides by {a}: x = {fmt_value(after_const)}/{a} = {fmt_fraction(sol)}.", after=_ans_eq(sol)),
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
        TraceStep(op="divide_by_coefficient", text=f"Divide both sides by {a}: x = {fmt_value(after_const)}/{a} = {fmt_fraction(sol)}.", after=_ans_eq(sol)),
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
        TraceStep(op="divide_by_coefficient", text=f"Divide both sides by {coef}: x = {fmt_value(const)}/{paren_if_negative(coef)} = {fmt_fraction(sol)}.", after=_ans_eq(sol)),
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
    trace = [move_step, divide_step]

    answer = f"x {final_op} {fmt_fraction(value)}"

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


REGISTRY: Dict[str, Any] = {
    "equation.one_step_linear": gen_one_step_linear,
    "equation.multi_step_linear": gen_multi_step_linear,
    "equation.equation_with_parentheses": gen_equation_with_parentheses,
    "equation.variable_on_both_sides": gen_variable_on_both_sides,
    "inequality.linear_inequality": gen_linear_inequality,
}
