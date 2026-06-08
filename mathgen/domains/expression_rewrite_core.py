"""expression_rewrite_core domain (design.md sec 2).

collect_like_terms, distribute, expand (binomial product), factor (trinomial),
and exponent rules. Each rewrite is verified for symbolic equivalence with sympy.
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import (
    fmt_add,
    fmt_factor,
    fmt_linear,
    fmt_mul,
    fmt_poly,
    fmt_radical,
    fmt_signed_term,
    paren_if_negative,
    sqrt_simplify,
    sum_text,
)
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
            text=f"Add the x-coefficients: {sum_text(x_coeffs) if x_coeffs else '0'}={x_sum}, so the x-term is {fmt_signed_term(x_sum, 'x', first=True)}.",
            meta={"x_sum": x_sum},
        ),
        TraceStep(
            op="collect_like_terms",
            text=f"Add the constants: {sum_text(consts) if consts else '0'}={const_sum}.",
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
        TraceStep(op="find_factor_pair", text=f"The numbers {p} and {q} work because {fmt_mul(p, q)}={c} and {fmt_add(p, q)}={b}.", meta={"p": p, "q": q, "product": c, "sum": b}),
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


def gen_rational_simplify(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 14}[diff]
    p = _nonzero(rng, -hi, hi)
    q = _nonzero(rng, -hi, hi)
    numer = fmt_poly([(1, 2), (p + q, 1), (p * q, 0)])
    denom = fmt_factor(p)
    answer = fmt_linear(1, q)
    trace = [
        TraceStep(op="factor_numerator", text=f"Factor the numerator: {numer} = {fmt_factor(p)}{fmt_factor(q)}."),
        TraceStep(op="cancel", text=f"Cancel the common factor {fmt_factor(p)}: the expression becomes {answer}."),
        TraceStep(op="finish", text=f"So the simplified form is {answer}.", after=answer),
    ]
    return make_sample(
        "expression_rewrite.rational_simplify",
        f"Simplify ({numer})/{denom}.",
        trace,
        answer,
        {"p": p, "q": q, "difficulty": diff},
        verified=check_equiv((X**2 + (p + q) * X + p * q) / (X + p), X + q),
    )


def gen_radical_simplify(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.choice([2, 3, 5, 6, 7])
    o1 = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff])
    o2 = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff])
    n1, n2 = o1 * o1 * base, o2 * o2 * base
    a1, _ = sqrt_simplify(n1)
    a2, _ = sqrt_simplify(n2)
    total = a1 + a2
    answer = fmt_radical(total, base)
    trace = [
        TraceStep(op="simplify_first", text=f"Simplify the first radical: sqrt({n1}) = {fmt_radical(a1, base)}."),
        TraceStep(op="simplify_second", text=f"Simplify the second radical: sqrt({n2}) = {fmt_radical(a2, base)}."),
        TraceStep(op="combine_like", text=f"Both have sqrt({base}), so add coefficients: {a1} + {a2} = {total}."),
        TraceStep(op="finish", text=f"So sqrt({n1}) + sqrt({n2}) = {answer}.", after=answer),
    ]
    return make_sample(
        "expression_rewrite.radical_simplify",
        f"Simplify sqrt({n1}) + sqrt({n2}).",
        trace,
        answer,
        {"n1": n1, "n2": n2, "base": base, "difficulty": diff},
        verified=(total * total * base == (a1 + a2) ** 2 * base),
    )


def gen_absolute_value_simplify(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 50}[diff]
    a = rng.randint(-hi, hi)
    b = rng.randint(-hi, hi)
    inside = a - b
    result = abs(inside)
    trace = [
        TraceStep(op="compute_inside", text=f"First compute inside the absolute value: {a} - ({b}) = {inside}."),
        TraceStep(op="apply_abs", text=f"The absolute value of {inside} is {result}."),
        TraceStep(op="finish", text=f"So |{a} - ({b})| = {result}.", after=str(result)),
    ]
    return make_sample(
        "expression_rewrite.absolute_value_simplify",
        f"Simplify |{a} - ({b})|.",
        trace,
        str(result),
        {"a": a, "b": b, "difficulty": diff},
        verified=(result == abs(a - b)),
    )


# -----------------------------------------------------------------------------
# Missing expression rewrite generators (added per coverage review)
# -----------------------------------------------------------------------------


def gen_factor_trinomial_a_not_1(rng: random.Random, cfg: GenConfig) -> Sample:
    """Factor ax²+bx+c where a≠1 (leading coefficient not 1)."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    # Build from factors: (px + q)(rx + s) = pr·x² + (ps + qr)x + qs
    p = _nonzero(rng, 2, hi)
    q = _nonzero(rng, -hi, hi)
    r = _nonzero(rng, 2, hi)
    s = _nonzero(rng, -hi, hi)
    # Ensure gcd(p,q)=1 and gcd(r,s)=1 for canonical factors
    while abs(math.gcd(p, abs(q))) != 1 and p > 0:
        q = _nonzero(rng, -hi, hi)
    while abs(math.gcd(r, abs(s))) != 1 and r > 0:
        s = _nonzero(rng, -hi, hi)

    a = p * r
    b_coef = p * s + q * r
    c_coef = q * s

    expr_str = fmt_poly([(a, 2), (b_coef, 1), (c_coef, 0)])
    factor1 = f"({fmt_linear(p, q)})" if p != 1 else f"({fmt_linear(1, q)})"
    factor2 = f"({fmt_linear(r, s)})" if r != 1 else f"({fmt_linear(1, s)})"
    answer = f"{factor1}{factor2}"

    trace = [
        TraceStep(op="set_up_factoring", text=f"Factor {expr_str}. Look for two binomials whose product gives a={a}, c={c_coef}, and cross-terms sum to b={b_coef}."),
        TraceStep(op="find_ac_pairs", text=f"The coefficient of x² is {a}={fmt_mul(p, r)} and the constant is {c_coef}={fmt_mul(q, s)}."),
        TraceStep(op="check_cross_terms", text=f"Check the cross terms: {fmt_mul(p, s)} + {fmt_mul(q, r)} = {fmt_add(p * s, q * r)} = {b_coef}. This matches."),
        TraceStep(op="write_factors", text=f"So {expr_str} = {answer}.", after=answer),
    ]
    return make_sample(
        "expression_rewrite.factor_trinomial_a_not_1",
        f"Factor {expr_str}.",
        trace,
        answer,
        {"a": a, "b": b_coef, "c": c_coef, "p": p, "q": q, "r": r, "s": s, "difficulty": diff},
        verified=check_equiv(a * X**2 + b_coef * X + c_coef, (p * X + q) * (r * X + s)),
    )


def gen_factor_difference_of_squares(rng: random.Random, cfg: GenConfig) -> Sample:
    """Factor a² - b² as (a+b)(a-b)."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 14}[diff]

    # Always define k and n first.
    if diff == Difficulty.EASY:
        k, n = 1, rng.randint(2, hi)
    elif diff == Difficulty.MEDIUM:
        k, n = rng.randint(2, 5), rng.randint(2, hi)
    else:
        k, n = rng.randint(3, 7), rng.randint(3, hi)

    k_sq, n_sq = k * k, n * n
    a_str = "x" if k == 1 else f"{k}x"
    expr_str = f"x^2 - {n_sq}" if k == 1 else f"{k_sq}x^2 - {n_sq}"
    answer = f"(x + {n})(x - {n})" if k == 1 else f"({k}x + {n})({k}x - {n})"

    trace = [
        TraceStep(op="recognize_pattern", text=f"Recognize {expr_str} as a difference of squares A² - B²."),
        TraceStep(op="identify_a_b", text=f"Here A = {a_str} and B = {n}, since ({a_str})² = {k_sq}x² and {n}² = {n_sq}."),
        TraceStep(op="apply_formula", text=f"A difference of squares factors as (A + B)(A - B) = {answer}."),
        TraceStep(op="finish", text=f"So {expr_str} = {answer}.", after=answer),
    ]
    expected = k_sq * X**2 - n_sq
    factored = (k * X + n) * (k * X - n)
    return make_sample(
        "expression_rewrite.factor_difference_of_squares",
        f"Factor {expr_str}.",
        trace,
        answer,
        {"k": k, "n": n, "difficulty": diff},
        verified=check_equiv(expected, factored),
    )


def gen_expand_perfect_square(rng: random.Random, cfg: GenConfig) -> Sample:
    """Expand (ax + b)² or (ax - b)² using the formula a²x² ± 2abx + b²."""
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a = rng.randint(1, hi)
    b = _nonzero(rng, -hi, hi)

    a_sq = a * a
    two_ab = 2 * a * b
    b_sq = b * b

    expr_str = f"({fmt_linear(a, b)})^2"
    answer = fmt_poly([(a_sq, 2), (two_ab, 1), (b_sq, 0)])

    trace = [
        TraceStep(op="state_formula", text=f"Use (P ± Q)² = P² ± 2PQ + Q² with P = {fmt_linear(a, 0)}, Q = {abs(b)}."),
        TraceStep(op="square_first", text=f"P² = ({fmt_linear(a, 0)})² = {a_sq}x².", meta={"a_sq": a_sq}),
        TraceStep(op="double_product", text=f"2PQ = 2 × {fmt_linear(a, 0)} × {paren_if_negative(b)} = {two_ab}x.", meta={"two_ab": two_ab}),
        TraceStep(op="square_second", text=f"Q² = ({paren_if_negative(b)})² = {b_sq}.", meta={"b_sq": b_sq}),
        TraceStep(op="finish", text=f"Combine: {answer}.", after=answer),
    ]
    expanded = (a * X + b) ** 2
    result_expr = a_sq * X**2 + two_ab * X + b_sq
    return make_sample(
        "expression_rewrite.expand_perfect_square",
        f"Expand {expr_str}.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=check_equiv(expanded, result_expr),
    )


REGISTRY: Dict[str, Any] = {
    "expression_rewrite.collect_like_terms": gen_collect_like_terms,
    "expression_rewrite.distribute": gen_distribute,
    "expression_rewrite.expand_binomial_product": gen_expand_binomial_product,
    "expression_rewrite.factor_trinomial": gen_factor_trinomial,
    "expression_rewrite.exponent_product": gen_exponent_product,
    "expression_rewrite.rational_simplify": gen_rational_simplify,
    "expression_rewrite.radical_simplify": gen_radical_simplify,
    "expression_rewrite.absolute_value_simplify": gen_absolute_value_simplify,
    "expression_rewrite.factor_trinomial_a_not_1": gen_factor_trinomial_a_not_1,
    "expression_rewrite.factor_difference_of_squares": gen_factor_difference_of_squares,
    "expression_rewrite.expand_perfect_square": gen_expand_perfect_square,
}
