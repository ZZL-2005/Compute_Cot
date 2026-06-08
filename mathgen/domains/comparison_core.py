"""comparison_order_estimation domain (design.md sec 11).

Comparing integers, fractions, decimals, radicals and powers; the sign of a
signed product/quotient; rounding; and bounding a square root between
consecutive integers. Every comparison is decided by an exact computation that
is shown step by step, and the result is verified.
"""

from __future__ import annotations

import math
import random
from decimal import Decimal
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample


def _rel(x, y) -> str:
    return "<" if x < y else ">"


def gen_integer_compare(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 50, Difficulty.MEDIUM: 500, Difficulty.HARD: 100000}[diff]
    a = rng.randint(-hi, hi)
    b = rng.randint(-hi, hi)
    while a == b:
        b = rng.randint(-hi, hi)
    rel = _rel(a, b)
    answer = f"{a} {rel} {b}"
    trace = [
        TraceStep(op="compare_signs", text=f"Compare {a} and {b} on the number line."),
        TraceStep(op="decide", text=f"Since {a} is to the {'left' if a < b else 'right'} of {b}, {a} is {'less than' if a < b else 'greater than'} {b}."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "comparison.integer_compare",
        f"Compare {a} and {b} using < or >.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=((rel == "<") == (a < b)),
    )


def gen_fraction_compare(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 9, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff]
    d1 = rng.randint(2, hi)
    d2 = rng.randint(2, hi)
    n1 = rng.randint(1, hi)
    n2 = rng.randint(1, hi)
    f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
    while f1 == f2:
        n2 = rng.randint(1, hi)
        f2 = Fraction(n2, d2)
    cross1 = n1 * d2
    cross2 = n2 * d1
    rel = _rel(f1, f2)
    answer = f"{n1}/{d1} {rel} {n2}/{d2}"
    trace = [
        TraceStep(op="cross_multiply", text=f"Both denominators are positive, so compare by cross-multiplying: {n1}×{d2} vs {n2}×{d1}."),
        TraceStep(op="compute_products", text=f"{n1}×{d2} = {cross1} and {n2}×{d1} = {cross2}."),
        TraceStep(op="decide", text=f"Since {cross1} {rel} {cross2}, the first fraction is {'smaller' if rel == '<' else 'larger'}."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "comparison.fraction_compare",
        f"Compare {n1}/{d1} and {n2}/{d2} using < or >.",
        trace,
        answer,
        {"n1": n1, "d1": d1, "n2": n2, "d2": d2, "difficulty": diff},
        verified=((rel == "<") == (f1 < f2)),
    )


def gen_decimal_compare(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    places = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    scale = 10**places
    a_scaled = rng.randint(1, 50 * scale)
    b_scaled = rng.randint(1, 50 * scale)
    while a_scaled == b_scaled:
        b_scaled = rng.randint(1, 50 * scale)
    a = Decimal(a_scaled) / Decimal(scale)
    b = Decimal(b_scaled) / Decimal(scale)
    a_str, b_str = f"{a:.{places}f}", f"{b:.{places}f}"
    rel = _rel(a, b)
    answer = f"{a_str} {rel} {b_str}"
    trace = [
        TraceStep(op="align_places", text=f"Both numbers have {places} decimal places, so compare digit by digit from the left."),
        TraceStep(op="scale", text=f"Equivalently, compare {a_scaled} and {b_scaled} (each number times {scale})."),
        TraceStep(op="decide", text=f"Since {a_scaled} {rel} {b_scaled}, the same order holds for the decimals."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "comparison.decimal_compare",
        f"Compare {a_str} and {b_str} using < or >.",
        trace,
        answer,
        {"a": a_str, "b": b_str, "difficulty": diff},
        verified=((rel == "<") == (a < b)),
    )


def gen_radical_compare(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    q = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff])
    qsq = q * q
    # pick p near q^2 but not a perfect square equal to q^2
    p = rng.randint(max(2, qsq - q), qsq + q)
    while p == qsq:
        p = rng.randint(max(2, qsq - q), qsq + q)
    rel = "<" if p < qsq else ">"
    answer = f"sqrt({p}) {rel} {q}"
    trace = [
        TraceStep(op="square_both", text=f"Both sqrt({p}) and {q} are positive, so compare their squares: sqrt({p})^2 = {p} and {q}^2 = {qsq}."),
        TraceStep(op="decide", text=f"Since {p} {rel} {qsq}, the same order holds for the positive roots."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "comparison.radical_compare",
        f"Compare sqrt({p}) and {q} using < or >.",
        trace,
        answer,
        {"p": p, "q": q, "difficulty": diff},
        verified=((rel == "<") == (p < qsq)),
    )


def gen_power_compare(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, 5)
    b = rng.randint(2, 5)
    m = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 8}[diff])
    n = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 8}[diff])
    va, vb = a**m, b**n
    while va == vb:
        n += 1
        vb = b**n
    rel = _rel(va, vb)
    answer = f"{a}^{m} {rel} {b}^{n}"
    trace = [
        TraceStep(op="evaluate_first", text=f"Evaluate {a}^{m} = {va}."),
        TraceStep(op="evaluate_second", text=f"Evaluate {b}^{n} = {vb}."),
        TraceStep(op="decide", text=f"Since {va} {rel} {vb}, the powers compare the same way."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "comparison.power_compare",
        f"Compare {a}^{m} and {b}^{n} using < or >.",
        trace,
        answer,
        {"a": a, "m": m, "b": b, "n": n, "difficulty": diff},
        verified=((rel == "<") == (va < vb)),
    )


def gen_sign_of_expression(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    count = {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff]
    factors = []
    for _ in range(count):
        v = rng.randint(2, 9)
        if rng.random() < 0.5:
            v = -v
        factors.append(v)
    neg = sum(1 for v in factors if v < 0)
    positive = (neg % 2 == 0)
    sign = "positive" if positive else "negative"
    expr = "×".join(f"({v})" if v < 0 else str(v) for v in factors)
    trace = [
        TraceStep(op="count_negatives", text=f"Count the negative factors in {expr}: there are {neg}."),
        TraceStep(op="parity_rule", text=f"A product is positive when the number of negative factors is even, and negative when it is odd. Here {neg} is {'even' if positive else 'odd'}."),
        TraceStep(op="finish", text=f"So the product is {sign}.", after=sign),
    ]
    return make_sample(
        "comparison.sign_of_expression",
        f"Is the product {expr} positive or negative?",
        trace,
        sign,
        {"factors": factors, "difficulty": diff},
        verified=((sign == "positive") == (math.prod(factors) > 0)),
    )


def gen_approximate_value(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    whole = rng.randint(1, {Difficulty.EASY: 20, Difficulty.MEDIUM: 200, Difficulty.HARD: 2000}[diff])
    tenth = rng.randint(0, 9)
    rest = rng.randint(0, 99)
    value_str = f"{whole}.{tenth}{rest:02d}"
    rounded = whole + (1 if tenth >= 5 else 0)
    trace = [
        TraceStep(op="locate_digit", text=f"To round {value_str} to the nearest integer, look at the tenths digit, which is {tenth}."),
        TraceStep(op="apply_rule", text=f"Since {tenth} is {'5 or more, round up' if tenth >= 5 else 'less than 5, round down'}."),
        TraceStep(op="finish", text=f"So {value_str} rounds to {rounded}.", after=str(rounded)),
    ]
    return make_sample(
        "comparison.approximate_value",
        f"Round {value_str} to the nearest integer.",
        trace,
        str(rounded),
        {"value": value_str, "difficulty": diff},
        verified=(rounded == round(Decimal(value_str))),
    )


def gen_bound_reasoning(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 25}[diff])
    n = rng.randint(k * k + 1, (k + 1) * (k + 1) - 1)
    answer = f"{k} < sqrt({n}) < {k + 1}"
    trace = [
        TraceStep(op="bracket_squares", text=f"Find consecutive squares around {n}: {k}^2 = {k * k} and {k + 1}^2 = {(k + 1) ** 2}."),
        TraceStep(op="locate", text=f"Since {k * k} < {n} < {(k + 1) ** 2}, taking square roots keeps the order."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "comparison.bound_reasoning",
        f"Between which two consecutive integers does sqrt({n}) lie?",
        trace,
        answer,
        {"n": n, "k": k, "difficulty": diff},
        verified=(k * k < n < (k + 1) ** 2),
    )


REGISTRY: Dict[str, Any] = {
    "comparison.integer_compare": gen_integer_compare,
    "comparison.fraction_compare": gen_fraction_compare,
    "comparison.decimal_compare": gen_decimal_compare,
    "comparison.radical_compare": gen_radical_compare,
    "comparison.power_compare": gen_power_compare,
    "comparison.sign_of_expression": gen_sign_of_expression,
    "comparison.approximate_value": gen_approximate_value,
    "comparison.bound_reasoning": gen_bound_reasoning,
}
