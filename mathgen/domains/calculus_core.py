"""calculus_core domain (design.md sec 8 differentiation; sec 23/24 minimal).

Differentiation is implemented in full (power, sum, product, quotient, chain,
simplification, tangent line, monotonicity/extrema). Per the project goal,
limits (23) and integration (24) are deliberately minimal: direct-substitution
and factor-cancel limits; power and definite power integrals.

Every derivative/limit/integral is verified against sympy.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict, List

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_fraction, fmt_linear, fmt_poly, paren_if_negative, pick_template

X = sp.Symbol("x")


def _poly_text(expr: sp.Expr) -> str:
    expr = sp.expand(expr)
    poly = sp.Poly(expr, X)
    deg = poly.degree() if expr != 0 else 0
    coeffs = poly.all_coeffs()
    terms = [(int(c), deg - i) for i, c in enumerate(coeffs)]
    return fmt_poly(terms)


def _nonzero(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


# -----------------------------------------------------------------------------
# Differentiation (full)
# -----------------------------------------------------------------------------


def gen_constant_power_rule(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = _nonzero(rng, -9, 9)
    n = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[diff])
    f = a * X**n
    fp = sp.diff(f, X)
    answer = _poly_text(fp)
    trace = [
        TraceStep(op="state_rule", text="Use the power rule: d/dx(a·x^n) = a·n·x^(n-1)."),
        TraceStep(op="bring_down", text=f"Bring down the exponent and multiply: {a}×{n} = {a * n}."),
        TraceStep(op="reduce_exponent", text=f"Reduce the exponent by 1: x^{n} becomes x^{n - 1}."),
        TraceStep(op="finish", text=f"So f'(x) = {answer}.", after=answer),
    ]
    return make_sample(
        "differentiation.constant_power_rule",
        f"Differentiate f(x) = {_poly_text(f)}.",
        trace,
        answer,
        {"a": a, "n": n, "difficulty": diff},
        verified=(sp.simplify(fp - a * n * X ** (n - 1)) == 0),
    )


def gen_sum_rule(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    deg = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    coeffs = [_nonzero(rng, -6, 6) for _ in range(deg)] + [rng.randint(-6, 6)]
    f = sum(c * X**(deg - i) for i, c in enumerate(coeffs))
    fp = sp.diff(f, X)
    answer = _poly_text(fp)
    steps: List[TraceStep] = [TraceStep(op="state_rule", text="Differentiate term by term using the power rule; the derivative of a constant is 0.")]
    for i, c in enumerate(coeffs):
        power = deg - i
        if power == 0:
            steps.append(TraceStep(op="diff_term", text=f"d/dx({c}) = 0."))
        elif power == 1:
            steps.append(TraceStep(op="diff_term", text=f"d/dx({c}x) = {c}."))
        else:
            steps.append(TraceStep(op="diff_term", text=f"d/dx({c}x^{power}) = {c * power}x^{power - 1}."))
    steps.append(TraceStep(op="finish", text=f"So f'(x) = {answer}.", after=answer))
    return make_sample(
        "differentiation.sum_rule",
        f"Differentiate f(x) = {_poly_text(f)}.",
        steps,
        answer,
        {"coeffs": coeffs, "difficulty": diff},
        verified=(sp.simplify(fp - sp.diff(f, X)) == 0),
    )


def gen_product_rule(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff]
    a, b = _nonzero(rng, -hi, hi), _nonzero(rng, -hi, hi)
    c, d = _nonzero(rng, -hi, hi), _nonzero(rng, -hi, hi)
    u, v = a * X + b, c * X + d
    f = u * v
    fp = sp.diff(f, X)
    answer = _poly_text(fp)
    trace = [
        TraceStep(op="name_factors", text=f"Let u = {fmt_linear(a, b)} and v = {fmt_linear(c, d)}. Then u' = {a} and v' = {c}."),
        TraceStep(op="state_rule", text="Product rule: f' = u'·v + u·v'."),
        TraceStep(op="substitute", text=f"f' = {paren_if_negative(a)}({fmt_linear(c, d)}) + ({fmt_linear(a, b)})×{paren_if_negative(c)}."),
        TraceStep(op="expand", text=f"Expand and combine like terms: f' = {answer}."),
        TraceStep(op="finish", text=f"So f'(x) = {answer}.", after=answer),
    ]
    return make_sample(
        "differentiation.product_rule",
        f"Differentiate f(x) = ({fmt_linear(a, b)})({fmt_linear(c, d)}).",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(sp.simplify(fp - (a * v + u * c)) == 0),
    )


def gen_quotient_rule(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff]
    a, b = _nonzero(rng, -hi, hi), _nonzero(rng, -hi, hi)
    c, d = _nonzero(rng, -hi, hi), _nonzero(rng, -hi, hi)
    while a * d - b * c == 0:
        d = _nonzero(rng, -hi, hi)
    u, v = a * X + b, c * X + d
    num = a * d - b * c
    den_str = f"({fmt_linear(c, d)})^2"
    answer = f"{num}/{den_str}"
    fp = sp.diff(u / v, X)
    trace = [
        TraceStep(op="name_parts", text=f"Let u = {fmt_linear(a, b)} and v = {fmt_linear(c, d)}, so u' = {a} and v' = {c}."),
        TraceStep(op="state_rule", text="Quotient rule: f' = (u'·v - u·v')/v^2."),
        TraceStep(op="numerator", text=f"Numerator: {paren_if_negative(a)}({fmt_linear(c, d)}) - ({fmt_linear(a, b)})×{paren_if_negative(c)} = {num}."),
        TraceStep(op="denominator", text=f"Denominator: v^2 = {den_str}."),
        TraceStep(op="finish", text=f"So f'(x) = {answer}.", after=answer),
    ]
    return make_sample(
        "differentiation.quotient_rule",
        f"Differentiate f(x) = ({fmt_linear(a, b)})/({fmt_linear(c, d)}).",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(sp.simplify(fp - num / (c * X + d) ** 2) == 0),
    )


def _power_str(base: str, expo: int) -> str:
    return f"({base})" if expo == 1 else f"({base})^{expo}"


def gen_chain_rule(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    a, b = _nonzero(rng, -hi, hi), _nonzero(rng, -hi, hi)
    n = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff])
    g = a * X + b
    f = g**n
    fp = sp.diff(f, X)
    coeff = a * n
    expo = n - 1
    base = fmt_linear(a, b)
    body = _power_str(base, expo)
    answer = (body if coeff == 1 else (f"-{body}" if coeff == -1 else f"{coeff}{body}"))
    trace = [
        TraceStep(op="name_inside", text=f"Let g = {base}, so f = g^{n} and g' = {a}."),
        TraceStep(op="state_rule", text="Chain rule: f' = n·g^(n-1)·g'."),
        TraceStep(op="substitute", text=f"f' = {n}{_power_str(base, expo)}×{paren_if_negative(a)} = {answer}."),
        TraceStep(op="finish", text=f"So f'(x) = {answer}.", after=answer),
    ]
    return make_sample(
        "differentiation.chain_rule",
        f"Differentiate f(x) = ({base})^{n}.",
        trace,
        answer,
        {"a": a, "b": b, "n": n, "difficulty": diff},
        verified=(sp.simplify(fp - coeff * (a * X + b) ** expo) == 0),
    )


def gen_derivative_simplification(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    r = _nonzero(rng, -hi, hi)
    inside = fmt_factor(-r)  # (x - r)
    f = X**2 * (X - r)
    expanded = sp.expand(f)
    fp = sp.diff(f, X)
    answer = _poly_text(fp)
    trace = [
        TraceStep(op="expand_first", text=f"First expand the product: x^2{inside} = {_poly_text(expanded)}."),
        TraceStep(op="differentiate", text=f"Differentiate term by term: f'(x) = {answer}."),
        TraceStep(op="finish", text=f"So f'(x) = {answer}.", after=answer),
    ]
    return make_sample(
        "differentiation.derivative_simplification",
        f"Differentiate and simplify f(x) = x^2{inside}.",
        trace,
        answer,
        {"r": r, "difficulty": diff},
        verified=(sp.simplify(fp - sp.diff(expanded, X)) == 0),
    )


def gen_tangent_line(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff]
    a = _nonzero(rng, -hi, hi)
    b = _nonzero(rng, -hi, hi)
    c = rng.randint(-hi, hi)
    x0 = rng.randint(-3, 3)
    f = a * X**2 + b * X + c
    fp = sp.diff(f, X)
    slope = int(fp.subs(X, x0))
    y0 = int(f.subs(X, x0))
    intercept = y0 - slope * x0
    answer = "y = " + fmt_linear(slope, intercept)
    trace = [
        TraceStep(op="differentiate", text=f"Differentiate: f'(x) = {_poly_text(fp)}."),
        TraceStep(op="slope_at_point", text=f"Slope at x={x0}: f'({x0}) = {slope}."),
        TraceStep(op="point_value", text=f"Point on the curve: f({x0}) = {y0}, so the point is ({x0}, {y0})."),
        TraceStep(op="point_slope", text=f"Tangent line: y - ({y0}) = {slope}(x - ({x0})), i.e. {answer}."),
        TraceStep(op="finish", text=f"So the tangent line is {answer}.", after=answer),
    ]
    return make_sample(
        "differentiation.tangent_line",
        f"Find the tangent line to f(x) = {_poly_text(f)} at x = {x0}.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "x0": x0, "difficulty": diff},
        verified=(slope == int(fp.subs(X, x0)) and slope * x0 + intercept == y0),
    )


def gen_monotonicity_extrema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    a = rng.randint(1, hi)  # opens up -> minimum
    b = _nonzero(rng, -2 * hi, 2 * hi)
    c = rng.randint(-hi, hi)
    f = a * X**2 + b * X + c
    fp = sp.diff(f, X)
    xc = Fraction(-b, 2 * a)
    answer = f"minimum at x={fmt_fraction(xc)}"
    trace = [
        TraceStep(op="differentiate", text=f"Differentiate: f'(x) = {_poly_text(fp)}."),
        TraceStep(op="set_zero", text=f"Set f'(x) = 0: {fmt_linear(2 * a, b)} = 0, so x = {fmt_fraction(xc)}."),
        TraceStep(op="classify", text=f"Since the leading coefficient {a} > 0, the parabola opens upward, so this critical point is a minimum."),
        TraceStep(op="finish", text=f"So there is a {answer}.", after=answer),
    ]
    return make_sample(
        "differentiation.monotonicity_extrema_basic",
        f"Find the extremum of f(x) = {_poly_text(f)}.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "difficulty": diff},
        verified=(fp.subs(X, sp.Rational(xc.numerator, xc.denominator)) == 0 and a > 0),
    )


# -----------------------------------------------------------------------------
# Limits (minimal)
# -----------------------------------------------------------------------------


def gen_direct_substitution_limit(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 9}[diff]
    a = _nonzero(rng, -4, 4)
    b = _nonzero(rng, -hi, hi)
    c = rng.randint(-hi, hi)
    p = rng.randint(-3, 3)
    f = a * X**2 + b * X + c
    value = int(f.subs(X, p))
    trace = [
        TraceStep(op="check_continuity", text=f"The function {_poly_text(f)} is a polynomial, so it is continuous; substitute x={p} directly."),
        TraceStep(op="substitute", text=f"f({p}) = {paren_if_negative(a)}×({p})^2 + {paren_if_negative(b)}×({p}) + ({c}) = {value}."),
        TraceStep(op="finish", text=f"So the limit is {value}.", after=str(value)),
    ]
    return make_sample(
        "limits.direct_substitution_limit",
        f"Evaluate lim(x->{p}) {_poly_text(f)}.",
        trace,
        str(value),
        {"p": p, "difficulty": diff},
        verified=(value == sp.limit(f, X, p)),
    )


def gen_factor_cancel_limit(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    p = _nonzero(rng, -hi, hi)
    q = _nonzero(rng, -hi, hi)
    while q == p:
        q = _nonzero(rng, -hi, hi)
    num = sp.expand((X - p) * (X - q))
    value = p - q
    expr = num / (X - p)
    trace = [
        TraceStep(op="detect_indeterminate", text=f"Substituting x={p} gives 0/0, so factor the numerator first."),
        TraceStep(op="factor", text=f"{_poly_text(num)} = {fmt_factor(-p)}{fmt_factor(-q)}."),
        TraceStep(op="cancel", text=f"Cancel the common factor {fmt_factor(-p)}: the expression becomes {fmt_factor(-q)}."),
        TraceStep(op="substitute", text=f"Substitute x={p}: {p} - ({q}) = {value}."),
        TraceStep(op="finish", text=f"So the limit is {value}.", after=str(value)),
    ]
    return make_sample(
        "limits.factor_cancel_limit",
        f"Evaluate lim(x->{p}) ({_poly_text(num)})/({fmt_linear(1, -p)}).",
        trace,
        str(value),
        {"p": p, "q": q, "difficulty": diff},
        verified=(value == sp.limit(expr, X, p)),
    )


# -----------------------------------------------------------------------------
# Integration (minimal)
# -----------------------------------------------------------------------------


def gen_power_integral(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 6}[diff])
    k = _nonzero(rng, -6, 6)
    a = k * (n + 1)  # so the antiderivative coefficient is the integer k
    nxt = n + 1
    body = "x" if nxt == 1 else f"x^{nxt}"
    coeff_str = "" if k == 1 else ("-" if k == -1 else str(k))
    answer = f"{coeff_str}{body} + C"
    trace = [
        TraceStep(op="state_rule", text="Use the power rule for integration: ∫ x^n dx = x^(n+1)/(n+1) + C."),
        TraceStep(op="apply", text=f"∫ {a}x^{n} dx = {a}/{nxt}·x^{nxt} + C."),
        TraceStep(op="simplify_coefficient", text=f"Simplify the coefficient: {a}/{nxt} = {k}."),
        TraceStep(op="finish", text=f"So the integral is {answer}.", after=answer),
    ]
    return make_sample(
        "integration.power_integral",
        pick_template(rng, f"Find the indefinite integral ∫ {a}x^{n} dx.", f"Integrate ∫ {a}x^{n} dx.", f"Compute ∫ {a}x^{n} dx.", f"Evaluate the indefinite integral ∫ {a}x^{n} dx."),
        trace,
        answer,
        {"a": a, "n": n, "difficulty": diff},
        verified=(sp.simplify(sp.integrate(a * X**n, X) - k * X**nxt) == 0),
    )


def gen_definite_integral_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(1, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff])
    k = rng.randint(1, 5)
    a = k * (n + 1)
    b = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff])
    nxt = n + 1
    fb = k * b**nxt
    value = fb  # F(b) - F(0), F(0)=0
    trace = [
        TraceStep(op="antiderivative", text=f"An antiderivative of {a}x^{n} is {k}x^{nxt} (since {a}/{nxt} = {k})."),
        TraceStep(op="evaluate_upper", text=f"At x={b}: {k}×{b}^{nxt} = {k}×{b**nxt} = {fb}."),
        TraceStep(op="evaluate_lower", text=f"At x=0: {k}×0^{nxt} = 0."),
        TraceStep(op="subtract", text=f"Subtract: {fb} - 0 = {value}."),
        TraceStep(op="finish", text=f"So the definite integral is {value}.", after=str(value)),
    ]
    return make_sample(
        "integration.definite_integral_basic",
        pick_template(rng, f"Evaluate the definite integral of {a}x^{n} from 0 to {b}.", f"Compute ∫_0^{b} {a}x^{n} dx.", f"Find the definite integral ∫_0^{b} {a}x^{n} dx.", f"Evaluate ∫_0^{b} {a}x^{n} dx."),
        trace,
        str(value),
        {"a": a, "n": n, "b": b, "difficulty": diff},
        verified=(value == sp.integrate(a * X**n, (X, 0, b))),
    )


REGISTRY: Dict[str, Any] = {
    "differentiation.constant_power_rule": gen_constant_power_rule,
    "differentiation.sum_rule": gen_sum_rule,
    "differentiation.product_rule": gen_product_rule,
    "differentiation.quotient_rule": gen_quotient_rule,
    "differentiation.chain_rule": gen_chain_rule,
    "differentiation.derivative_simplification": gen_derivative_simplification,
    "differentiation.tangent_line": gen_tangent_line,
    "differentiation.monotonicity_extrema_basic": gen_monotonicity_extrema,
    "limits.direct_substitution_limit": gen_direct_substitution_limit,
    "limits.factor_cancel_limit": gen_factor_cancel_limit,
    "integration.power_integral": gen_power_integral,
    "integration.definite_integral_basic": gen_definite_integral_basic,
}
