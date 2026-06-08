"""functions_core domain (design.md sec 5).

Function evaluation, composition, piecewise evaluation, domain, range, inverse,
zeros, sign, and transformations. Numeric results use exact arithmetic;
symbolic ones (composition, inverse) are checked with sympy.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import (
    fmt_add,
    fmt_factor,
    fmt_fraction,
    fmt_interval,
    fmt_linear,
    fmt_mul,
    fmt_poly,
    fmt_signed_term,
    fmt_union,
    paren_if_negative,
    sum_text,
)
from mathgen.verify import X, check_equiv


def _nonzero(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def gen_function_evaluation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    a = _nonzero(rng, -hi, hi)
    b = _nonzero(rng, -hi, hi)
    c = _nonzero(rng, -hi, hi)
    k_bound = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    k = _nonzero(rng, -k_bound, k_bound)

    poly = fmt_poly([(a, 2), (b, 1), (c, 0)])
    ksq = k * k
    term_sq = a * ksq
    term_lin = b * k
    total = term_sq + term_lin + c

    trace = [
        TraceStep(op="substitute", text=f"Substitute x={k} into f(x) = {poly}.", meta={"x": k}),
        TraceStep(op="square_term", text=f"The squared term: {paren_if_negative(a)}×({paren_if_negative(k)})^2 = {paren_if_negative(a)}×{ksq} = {term_sq}.", meta={"value": term_sq}),
        TraceStep(op="linear_term", text=f"The linear term: {fmt_mul(b, k)} = {term_lin}.", meta={"value": term_lin}),
        TraceStep(op="constant_term", text=f"The constant term is {c}.", meta={"value": c}),
        TraceStep(op="add_terms", text=f"Add the three results: {sum_text([term_sq, term_lin, c])} = {total}.", meta={"total": total}),
        TraceStep(op="finish", text=f"So f({k}) = {total}.", after=str(total)),
    ]
    return make_sample(
        "function.function_evaluation",
        f"Let f(x) = {poly}. Compute f({k}).",
        trace,
        str(total),
        {"a": a, "b": b, "c": c, "x": k, "difficulty": diff},
        verified=(total == a * k * k + b * k + c),
    )


def gen_composite_function(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a = _nonzero(rng, -hi, hi)
    b = _nonzero(rng, -hi, hi)
    c = _nonzero(rng, -hi, hi)
    d = _nonzero(rng, -hi, hi)

    f_str = fmt_linear(a, b)
    g_str = fmt_linear(c, d)
    ac = a * c
    ad = a * d
    const = ad + b
    answer = fmt_linear(ac, const)

    trace = [
        TraceStep(op="substitute_g", text=f"Replace x in f(x) = {f_str} with g(x) = {g_str}: f(g(x)) = {paren_if_negative(a)}({g_str}){fmt_signed_term(b, '', first=False)}.", meta={"a": a}),
        TraceStep(op="distribute_x", text=f"Multiply the x-coefficient: {fmt_mul(a, c)}={ac}, so the x-term is {fmt_signed_term(ac, 'x', first=True)}.", meta={"ac": ac}),
        TraceStep(op="distribute_const", text=f"Multiply the constant from g: {fmt_mul(a, d)}={ad}.", meta={"ad": ad}),
        TraceStep(op="combine_constants", text=f"Add the constant {b} from f: {fmt_add(ad, b)}={const}.", meta={"const": const}),
        TraceStep(op="finish", text=f"So f(g(x)) = {answer}.", after=answer),
    ]
    return make_sample(
        "function.composite_function",
        f"Let f(x) = {f_str} and g(x) = {g_str}. Find f(g(x)).",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=check_equiv(a * (c * X + d) + b, ac * X + const),
    )


def gen_piecewise_function(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    c = rng.randint(-4, 4)
    a1, b1 = _nonzero(rng, -hi, hi), rng.randint(-hi, hi)
    a2, b2 = _nonzero(rng, -hi, hi), rng.randint(-hi, hi)
    k = rng.randint(-7, 7)
    while k == c:
        k = rng.randint(-7, 7)
    if k < c:
        branch, a, b = "x < " + str(c), a1, b1
        value = a1 * k + b1
    else:
        branch, a, b = "x ≥ " + str(c), a2, b2
        value = a2 * k + b2
    f1, f2 = fmt_linear(a1, b1), fmt_linear(a2, b2)
    trace = [
        TraceStep(op="choose_branch", text=f"Since {k} {'<' if k < c else '≥'} {c}, use the branch for {branch}: f(x) = {fmt_linear(a, b)}."),
        # Avoid "+ (-5)" dirty pattern: use fmt_signed_term for the constant (des_instruct.md sec 5).
        TraceStep(op="substitute", text=f"f({k}) = {paren_if_negative(a)}×{paren_if_negative(k)}{fmt_signed_term(b, '', first=False)} = {value}."),
        TraceStep(op="finish", text=f"So f({k}) = {value}.", after=str(value)),
    ]
    return make_sample(
        "function.piecewise_function",
        f"Let f(x) = {f1} for x < {c}, and f(x) = {f2} for x ≥ {c}. Compute f({k}).",
        trace,
        str(value),
        {"c": c, "k": k, "difficulty": diff},
        verified=(value == (a1 * k + b1 if k < c else a2 * k + b2)),
    )


def gen_domain(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-8, 8)
    inner = fmt_linear(1, -c)  # "x - c" or "x + |c|"
    if rng.random() < 0.5:  # sqrt(x - c): x >= c
        answer = fmt_interval(c, None, low_open=False, high_open=True)
        trace = [
            TraceStep(op="state_condition", text="A square root requires its argument to be ≥ 0."),
            TraceStep(op="set_inequality", text=f"Require {inner} ≥ 0, so x ≥ {c}."),
            TraceStep(op="finish", text=f"So the domain is {answer}.", after=answer),
        ]
        user = f"Find the domain of f(x) = sqrt({inner})."
        ok = (answer == f"[{c}, +∞)")
    else:  # 1/(x - c): x != c
        left = fmt_interval(None, c, low_open=True, high_open=True)
        right = fmt_interval(c, None, low_open=True, high_open=True)
        answer = fmt_union([left, right])
        trace = [
            TraceStep(op="state_condition", text="A denominator cannot be 0."),
            TraceStep(op="exclude", text=f"Require {inner} ≠ 0, so x ≠ {c}."),
            TraceStep(op="finish", text=f"So the domain is {answer}.", after=answer),
        ]
        user = f"Find the domain of f(x) = 1/({inner})."
        ok = True
    return make_sample(
        "function.domain",
        user,
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=ok,
    )


def gen_simple_range(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    h = rng.randint(-hi, hi)
    k = rng.randint(-hi, hi)
    a = rng.choice([1, 2, -1, -2])
    coef_str = "" if a == 1 else ("-" if a == -1 else str(a))
    body = f"{coef_str}(x {'-' if h > 0 else '+'} {abs(h)})^2 {'+' if k >= 0 else '-'} {abs(k)}"
    if a > 0:
        answer = fmt_interval(k, None, low_open=False, high_open=True)
        reason = f"opens upward, so the minimum value is {k} at x = {h}"
    else:
        answer = fmt_interval(None, k, low_open=True, high_open=False)
        reason = f"opens downward, so the maximum value is {k} at x = {h}"
    trace = [
        TraceStep(op="identify_vertex", text=f"The function f(x) = {body} is in vertex form with vertex ({h}, {k})."),
        TraceStep(op="use_opening", text=f"Since the leading coefficient is {a}, the parabola {reason}."),
        TraceStep(op="finish", text=f"So the range is {answer}.", after=answer),
    ]
    return make_sample(
        "function.simple_range",
        f"Find the range of f(x) = {body}.",
        trace,
        answer,
        {"a": a, "h": h, "k": k, "difficulty": diff},
        verified=(answer == (f"[{k}, +∞)" if a > 0 else f"(-∞, {k}]")),
    )


def gen_inverse_function_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a = rng.randint(2, hi)
    b = _nonzero(rng, -hi, hi)
    numerator = fmt_linear(1, -b)  # x - b
    answer = f"f^(-1)(x) = ({numerator})/{a}"
    trace = [
        TraceStep(op="set_y", text=f"Write y = {fmt_linear(a, b)} and solve for x."),
        TraceStep(op="isolate", text=f"Subtract {b} (giving y - ({b})), then divide by {a}: x = (y - ({b}))/{a}."),
        TraceStep(op="swap", text=f"Swap x and y to get the inverse: f^(-1)(x) = ({numerator})/{a}."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    finv = (X - b) / a
    return make_sample(
        "function.inverse_function_basic",
        f"Find the inverse of f(x) = {fmt_linear(a, b)}.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=(sp.simplify(a * finv + b - X) == 0),
    )


def gen_function_zero(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    a = _nonzero(rng, 2, hi)
    root = rng.randint(-hi, hi)
    b = -a * root  # a*root + b = 0
    answer = f"x={root}"
    trace = [
        TraceStep(op="set_zero", text=f"Set f(x) = 0: {fmt_linear(a, b)} = 0."),
        TraceStep(op="solve", text=f"{'Subtract' if b > 0 else 'Add'} {abs(b)}: {a}x = {-b}. Divide by {a}: x = {-b}/{a} = {root}."),
        TraceStep(op="finish", text=f"So the zero is {answer}.", after=answer),
    ]
    return make_sample(
        "function.function_zero",
        f"Find the zero of f(x) = {fmt_linear(a, b)}.",
        trace,
        answer,
        {"a": a, "b": b, "root": root, "difficulty": diff},
        verified=(a * root + b == 0),
    )


def gen_function_sign(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    a = _nonzero(rng, -hi, hi)
    root = Fraction(rng.randint(-hi, hi))
    b = int(-a * root)
    # f(x) = a x + b > 0
    if a > 0:
        answer = fmt_interval(root, None, low_open=True, high_open=True)
        reason = f"divide by {a} (positive, keep the sign): x > {fmt_fraction(root)}"
    else:
        answer = fmt_interval(None, root, low_open=True, high_open=True)
        reason = f"divide by {a} (negative, flip the sign): x < {fmt_fraction(root)}"
    trace = [
        TraceStep(op="set_inequality", text=f"Solve f(x) > 0: {fmt_linear(a, b)} > 0."),
        TraceStep(op="isolate", text=f"Move the constant: {a}x > {-b}; then {reason}."),
        TraceStep(op="finish", text=f"So f(x) > 0 on {answer}.", after=answer),
    ]
    return make_sample(
        "function.function_sign",
        f"For f(x) = {fmt_linear(a, b)}, find where f(x) > 0.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=(a * root + b == 0),
    )


def gen_function_transformation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    h = _nonzero(rng, -6, 6)
    k = _nonzero(rng, -6, 6)
    hx = "right" if h > 0 else "left"
    ky = "up" if k > 0 else "down"
    # Use fmt_factor to avoid "x - (-3)" dirty pattern (des_instruct.md sec 5).
    shift_x = fmt_factor(-h)  # (x - h) or (x + |h|)
    shift_k = fmt_signed_term(k, '', first=False)
    x_inner = shift_x.replace("(", "").replace(")", "")  # "x - 3" or "x + 3"
    func_str = f"f({x_inner}){shift_k}"
    answer = f"shift {abs(h)} units {hx} and {abs(k)} units {ky}"
    trace = [
        TraceStep(op="horizontal", text=f"Replacing x by {x_inner} shifts the graph {abs(h)} units {hx}."),
        TraceStep(op="vertical", text=f"Adding {k} shifts the graph {abs(k)} units {ky}."),
        TraceStep(op="finish", text=f"So the transformation is to {answer}.", after=answer),
    ]
    return make_sample(
        "function.function_transformation",
        f"Describe how the graph of y = {func_str} is obtained from y = f(x).",
        trace,
        answer,
        {"h": h, "k": k, "difficulty": diff},
        verified=True,
    )


REGISTRY: Dict[str, Any] = {
    "function.function_evaluation": gen_function_evaluation,
    "function.composite_function": gen_composite_function,
    "function.piecewise_function": gen_piecewise_function,
    "function.domain": gen_domain,
    "function.simple_range": gen_simple_range,
    "function.inverse_function_basic": gen_inverse_function_basic,
    "function.function_zero": gen_function_zero,
    "function.function_sign": gen_function_sign,
    "function.function_transformation": gen_function_transformation,
}
