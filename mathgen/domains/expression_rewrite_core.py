"""expression_rewrite_core domain (design.md sec 2).

collect_like_terms, distribute, expand (binomial product), factor (trinomial),
and exponent rules. Each rewrite is verified for symbolic equivalence with sympy.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_poly, fmt_signed_term, paren_if_negative
from mathgen.verify import X, check_equiv


def _nonzero(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def gen_collect_like_terms(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    n_terms = {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff]

    x_coeffs: List[int] = []
    consts: List[int] = []
    pieces: List[str] = []
    first = True
    for _ in range(n_terms):
        if rng.random() < 0.55:
            c = _nonzero(rng, -hi, hi)
            x_coeffs.append(c)
            pieces.append(fmt_signed_term(c, "x", first=first))
        else:
            c = _nonzero(rng, -hi, hi)
            consts.append(c)
            pieces.append(fmt_signed_term(c, "", first=first))
        first = False
    expr_str = "".join(pieces)

    x_sum = sum(x_coeffs)
    const_sum = sum(consts)
    answer = fmt_poly([(x_sum, 1), (const_sum, 0)])

    trace = [
        TraceStep(
            op="identify_like_terms",
            text=f"Group the x-terms {', '.join(fmt_signed_term(c, 'x', first=True) for c in x_coeffs) or 'none'} and the constant terms {', '.join(str(c) for c in consts) or 'none'}.",
            meta={"x_coeffs": x_coeffs, "consts": consts},
        ),
        TraceStep(
            op="collect_like_terms",
            text=f"Add the x-coefficients: {'+'.join(str(c) for c in x_coeffs) if x_coeffs else '0'}={x_sum}, so the x-term is {fmt_signed_term(x_sum, 'x', first=True)}.",
            meta={"x_sum": x_sum},
        ),
        TraceStep(
            op="collect_like_terms",
            text=f"Add the constants: {'+'.join(str(c) for c in consts) if consts else '0'}={const_sum}.",
            meta={"const_sum": const_sum},
        ),
        TraceStep(op="finish", text=f"Combine to get {answer}.", after=answer),
    ]
    before = sum(c * X for c in x_coeffs) + sum(consts)
    after = x_sum * X + const_sum
    return make_sample(
        "expression_rewrite.collect_like_terms",
        f"Simplify {expr_str}.",
        trace,
        answer,
        {"x_coeffs": x_coeffs, "consts": consts, "difficulty": diff},
        verified=check_equiv(before, after),
    )


def gen_distribute(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    a = _nonzero(rng, -hi, hi)
    b = _nonzero(rng, -hi, hi)
    c = _nonzero(rng, -hi, hi)
    # a * (b x + c)
    inner = fmt_poly([(b, 1), (c, 0)])
    expr_str = f"{paren_if_negative(a)}({inner})"
    pb, pc = a * b, a * c
    answer = fmt_poly([(pb, 1), (pc, 0)])
    trace = [
        TraceStep(op="distribute", text=f"Multiply {paren_if_negative(a)} by each term inside the parentheses."),
        TraceStep(op="partial_product", text=f"Multiply the coefficients for the x-term: {paren_if_negative(a)}×{paren_if_negative(b)}={pb}, giving {fmt_signed_term(pb, 'x', first=True)}.", meta={"factor": a, "term": b, "result": pb}),
        TraceStep(op="partial_product", text=f"Multiply for the constant: {paren_if_negative(a)}×{paren_if_negative(c)}={pc}.", meta={"factor": a, "term": c, "result": pc}),
        TraceStep(op="finish", text=f"Combine the products: {answer}.", after=answer),
    ]
    return make_sample(
        "expression_rewrite.distribute",
        f"Expand {expr_str}.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "difficulty": diff},
        verified=check_equiv(a * (b * X + c), pb * X + pc),
    )


def gen_expand_binomial_product(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    p = _nonzero(rng, -hi, hi)
    q = _nonzero(rng, -hi, hi)
    # (x + p)(x + q)
    expr_str = f"{fmt_factor(p)}{fmt_factor(q)}"
    b = p + q
    c = p * q
    answer = fmt_poly([(1, 2), (b, 1), (c, 0)])
    trace = [
        TraceStep(op="foil_first", text=f"Multiply the first terms: x×x=x^2."),
        TraceStep(op="foil_outer_inner", text=f"The x-terms give {fmt_signed_term(p, 'x', first=True)} and {fmt_signed_term(q, 'x', first=True)}, which add to {fmt_signed_term(b, 'x', first=True)}.", meta={"p": p, "q": q, "sum": b}),
        TraceStep(op="foil_last", text=f"Multiply the constants: {paren_if_negative(p)}×{paren_if_negative(q)}={c}.", meta={"product": c}),
        TraceStep(op="finish", text=f"Combine to get {answer}.", after=answer),
    ]
    return make_sample(
        "expression_rewrite.expand_binomial_product",
        f"Expand {expr_str}.",
        trace,
        answer,
        {"p": p, "q": q, "difficulty": diff},
        verified=check_equiv((X + p) * (X + q), X**2 + b * X + c),
    )


def gen_factor_trinomial(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 14}[diff]
    p = _nonzero(rng, -hi, hi)
    q = _nonzero(rng, -hi, hi)
    b = p + q
    c = p * q
    expr_str = fmt_poly([(1, 2), (b, 1), (c, 0)])
    answer = f"{fmt_factor(p)}{fmt_factor(q)}"
    trace = [
        TraceStep(op="set_up_factoring", text=f"Look for two numbers whose product is {c} and whose sum is {b}."),
        TraceStep(op="find_factor_pair", text=f"The numbers {p} and {q} work because {paren_if_negative(p)}×{paren_if_negative(q)}={c} and {p}+{q}={b}.", meta={"p": p, "q": q, "product": c, "sum": b}),
        TraceStep(op="write_factors", text=f"Therefore {expr_str}={answer}.", after=answer),
    ]
    return make_sample(
        "expression_rewrite.factor_trinomial",
        f"Factor {expr_str}.",
        trace,
        answer,
        {"p": p, "q": q, "b": b, "c": c, "difficulty": diff},
        verified=check_equiv(X**2 + b * X + c, (X + p) * (X + q)),
    )


def gen_exponent_product(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 9}[diff]
    a = rng.randint(2, hi)
    b = rng.randint(2, hi)
    m = rng.randint(1, hi)
    n = rng.randint(1, hi)
    coef = a * b
    power = m + n
    left = f"{a}x^{m}" if m > 1 else f"{a}x"
    right = f"{b}x^{n}" if n > 1 else f"{b}x"
    expr_str = f"{left} × {right}"
    answer = f"{coef}x^{power}" if power > 1 else f"{coef}x"
    trace = [
        TraceStep(op="multiply_coefficients", text=f"Multiply the coefficients: {a}×{b}={coef}.", meta={"a": a, "b": b, "coef": coef}),
        TraceStep(op="add_exponents", text=f"Add the exponents of x: x^{m}×x^{n}=x^({m}+{n})=x^{power}.", meta={"m": m, "n": n, "power": power}),
        TraceStep(op="finish", text=f"Therefore {expr_str}={answer}.", after=answer),
    ]
    return make_sample(
        "expression_rewrite.exponent_product",
        f"Simplify {expr_str}.",
        trace,
        answer,
        {"a": a, "b": b, "m": m, "n": n, "difficulty": diff},
        verified=check_equiv(a * X**m * (b * X**n), coef * X**power),
    )


REGISTRY: Dict[str, Any] = {
    "expression_rewrite.collect_like_terms": gen_collect_like_terms,
    "expression_rewrite.distribute": gen_distribute,
    "expression_rewrite.expand_binomial_product": gen_expand_binomial_product,
    "expression_rewrite.factor_trinomial": gen_factor_trinomial,
    "expression_rewrite.exponent_product": gen_exponent_product,
}
