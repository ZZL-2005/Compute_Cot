"""functions_core domain (design.md sec 5).

function_evaluation (substitute a value into a quadratic and evaluate term by
term) and composite_function (build f(g(x)) and simplify). Each result is
verified: evaluation by exact integer arithmetic, composition by sympy
equivalence. Every term is computed explicitly, so no step is skipped.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_add, fmt_linear, fmt_mul, fmt_poly, fmt_signed_term, paren_if_negative, sum_text
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


REGISTRY: Dict[str, Any] = {
    "function.function_evaluation": gen_function_evaluation,
    "function.composite_function": gen_composite_function,
}
