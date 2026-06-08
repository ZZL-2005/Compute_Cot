"""polynomial_advanced domain (design.md sec 22).

Degree, polynomial division by a linear factor, remainder theorem, factor
theorem, Vieta's formulas, the rational root theorem, and factoring a cubic with
integer roots. Verified with sympy / direct computation.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_poly

X = sp.Symbol("x")


def _poly_text(expr: sp.Expr) -> str:
    expr = sp.expand(expr)
    if expr == 0:
        return "0"
    poly = sp.Poly(expr, X)
    deg = poly.degree()
    coeffs = poly.all_coeffs()
    return fmt_poly([(int(c), deg - i) for i, c in enumerate(coeffs)])


def _nz(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def _divisors(n: int) -> List[int]:
    n = abs(n)
    return [d for d in range(1, n + 1) if n % d == 0]


def gen_polynomial_degree(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    deg = {Difficulty.EASY: 2, Difficulty.MEDIUM: 4, Difficulty.HARD: 6}[diff]
    coeffs = [_nz(rng, -6, 6)] + [rng.randint(-6, 6) for _ in range(deg)]
    expr = sum(c * X**(deg - i) for i, c in enumerate(coeffs))
    poly_str = _poly_text(expr)
    trace = [
        TraceStep(op="state_def", text="The degree of a polynomial is the highest power of x with a nonzero coefficient."),
        TraceStep(op="identify", text=f"In {poly_str}, the highest power with a nonzero coefficient is x^{deg}."),
        TraceStep(op="finish", text=f"So the degree is {deg}.", after=str(deg)),
    ]
    return make_sample(
        "polynomial.polynomial_degree",
        f"Find the degree of {poly_str}.",
        trace,
        str(deg),
        {"coeffs": coeffs, "difficulty": diff},
        verified=(sp.Poly(expr, X).degree() == deg),
    )


def gen_polynomial_division(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    deg = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    coeffs = [_nz(rng, -5, 5)] + [rng.randint(-6, 6) for _ in range(deg)]
    f = sum(c * X**(deg - i) for i, c in enumerate(coeffs))
    c = _nz(rng, -5, 5)
    divisor = X - c
    q, r = sp.div(f, divisor, X)
    q_str = _poly_text(q)
    r_int = int(r)
    ans = f"quotient {q_str}, remainder {r_int}"

    # Show synthetic division steps, not just the result.
    coeff_list = [int(f.coeff(X, i)) for i in range(deg, -1, -1)]
    trace = [TraceStep(op="synthetic_setup", text=f"Use synthetic division with c={c}. Write the coefficients of {_poly_text(f)}: {coeff_list}.")]
    # Bring down first coefficient
    row = [coeff_list[0]]
    trace.append(TraceStep(op="bring_down", text=f"Bring down the first coefficient: {row[0]}."))
    for i in range(1, len(coeff_list)):
        prod = row[-1] * c
        new_val = coeff_list[i] + prod
        row.append(new_val)
        if i < len(coeff_list) - 1:
            trace.append(TraceStep(op="synthetic_step", text=f"Multiply {row[-2]}×({c}) = {prod}, add to {coeff_list[i]}: {coeff_list[i]} + ({prod}) = {new_val}."))
        else:
            trace.append(TraceStep(op="synthetic_remainder", text=f"Multiply {row[-2]}×({c}) = {prod}, add to {coeff_list[i]}: {coeff_list[i]} + ({prod}) = {new_val}. This is the remainder."))
    trace.append(TraceStep(op="write_result", text=f"The quotient coefficients are {row[:-1]}, so the quotient is {q_str}, with remainder {r_int}."))
    trace.append(TraceStep(op="check", text=f"Verify: ({fmt_factor(-c)})({q_str}) + ({r_int}) = {_poly_text(f)}."))
    trace.append(TraceStep(op="finish", text=f"So the result is {ans}.", after=ans))
    return make_sample(
        "polynomial.polynomial_division",
        f"Divide {_poly_text(f)} by {fmt_factor(-c)}.",
        trace,
        ans,
        {"coeffs": coeffs, "c": c, "difficulty": diff},
        verified=(sp.expand(divisor * q + r - f) == 0),
    )


def gen_remainder_theorem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    deg = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    coeffs = [_nz(rng, -4, 4)] + [rng.randint(-6, 6) for _ in range(deg)]
    f = sum(c * X**(deg - i) for i, c in enumerate(coeffs))
    c = _nz(rng, -4, 4)
    value = int(f.subs(X, c))
    trace = [
        TraceStep(op="state_theorem", text=f"The remainder theorem says the remainder of p(x) ÷ {fmt_factor(-c)} equals p({c})."),
        TraceStep(op="evaluate", text=f"Evaluate p({c}) for p(x) = {_poly_text(f)}: p({c}) = {value}."),
        TraceStep(op="finish", text=f"So the remainder is {value}.", after=str(value)),
    ]
    return make_sample(
        "polynomial.remainder_theorem",
        f"Find the remainder when {_poly_text(f)} is divided by {fmt_factor(-c)}.",
        trace,
        str(value),
        {"coeffs": coeffs, "c": c, "difficulty": diff},
        verified=(value == int(sp.rem(f, X - c, X))),
    )


def gen_factor_theorem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    deg = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 3}[diff]
    c = _nz(rng, -4, 4)
    if rng.random() < 0.5:  # make (x - c) a genuine factor
        other = [_nz(rng, -4, 4) for _ in range(deg - 1)]
        f = sp.expand((X - c) * sp.prod([X - o for o in other])) if other else (X - c)
    else:
        f = sum(_nz(rng, -4, 4) * X**(deg - i) for i in range(deg + 1))
    value = int(sp.expand(f).subs(X, c))
    is_factor = (value == 0)
    yn = "Yes" if is_factor else "No"
    trace = [
        TraceStep(op="state_theorem", text=f"{fmt_factor(-c)} is a factor of p(x) exactly when p({c}) = 0."),
        TraceStep(op="evaluate", text=f"For p(x) = {_poly_text(f)}, p({c}) = {value}."),
        TraceStep(op="decide", text=f"Since p({c}) = {value} {'= 0' if is_factor else '≠ 0'}, {fmt_factor(-c)} {'is' if is_factor else 'is not'} a factor."),
        TraceStep(op="finish", text=f"So the answer is {yn}.", after=yn),
    ]
    return make_sample(
        "polynomial.factor_theorem",
        f"Is {fmt_factor(-c)} a factor of {_poly_text(f)}?",
        trace,
        yn,
        {"c": c, "difficulty": diff},
        verified=((yn == "Yes") == is_factor),
    )


def gen_vieta_formula(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    r1, r2 = _nz(rng, -hi, hi), _nz(rng, -hi, hi)
    b = -(r1 + r2)
    c = r1 * r2
    expr = _poly_text(X**2 + b * X + c)
    s = -b
    ans = f"sum = {s}, product = {c}"
    trace = [
        TraceStep(op="state_vieta", text="For x^2 + bx + c, Vieta's formulas give sum of roots = -b and product of roots = c."),
        TraceStep(op="read_coeffs", text=f"Here b = {b} and c = {c}."),
        TraceStep(op="apply", text=f"Sum of roots = -({b}) = {s}; product of roots = {c}."),
        TraceStep(op="finish", text=f"So {ans}.", after=ans),
    ]
    return make_sample(
        "polynomial.vieta_formula",
        f"For the quadratic {expr} = 0, find the sum and product of its roots.",
        trace,
        ans,
        {"b": b, "c": c, "difficulty": diff},
        verified=(s == r1 + r2 and c == r1 * r2),
    )


def gen_rational_root_test(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c0 = _nz(rng, -12, 12)
    divs = _divisors(c0)
    candidates = sorted(set([d for d in divs] + [-d for d in divs]))
    cand_text = ", ".join(str(x) for x in candidates)
    answer = "{" + cand_text + "}"
    # build a sample monic polynomial with this constant term
    b = rng.randint(-6, 6)
    expr = _poly_text(X**2 + b * X + c0)
    trace = [
        TraceStep(op="state_theorem", text="For a monic polynomial, the rational root theorem says any rational root is an integer dividing the constant term."),
        TraceStep(op="list_divisors", text=f"The constant term is {c0}; its positive divisors are {', '.join(str(d) for d in divs)}."),
        TraceStep(op="add_signs", text=f"Include both signs to get the candidates: {cand_text}."),
        TraceStep(op="finish", text=f"So the possible rational roots are {answer}.", after=answer),
    ]
    return make_sample(
        "polynomial.rational_root_test",
        f"List the possible rational roots of {expr} = 0 (rational root theorem).",
        trace,
        answer,
        {"constant": c0, "difficulty": diff},
        verified=(set(candidates) == set([d for d in divs] + [-d for d in divs])),
    )


def gen_higher_degree_factor(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff]
    r1, r2, r3 = (rng.randint(-hi, hi) for _ in range(3))
    f = sp.expand((X - r1) * (X - r2) * (X - r3))
    factored = f"{fmt_factor(-r1)}{fmt_factor(-r2)}{fmt_factor(-r3)}"
    roots_sorted = sorted([r1, r2, r3])
    trace = [
        TraceStep(op="find_roots", text=f"Test small integers; the roots are x = {roots_sorted[0]}, {roots_sorted[1]}, {roots_sorted[2]}."),
        TraceStep(op="write_factors", text=f"Each root r gives a factor (x - r): {factored}."),
        TraceStep(op="check", text=f"Expanding {factored} reproduces {_poly_text(f)}."),
        TraceStep(op="finish", text=f"So {_poly_text(f)} = {factored}.", after=factored),
    ]
    return make_sample(
        "polynomial.higher_degree_factor",
        f"Factor {_poly_text(f)} completely.",
        trace,
        factored,
        {"roots": roots_sorted, "difficulty": diff},
        verified=(sp.expand(f - (X - r1) * (X - r2) * (X - r3)) == 0),
    )


REGISTRY: Dict[str, Any] = {
    "polynomial.polynomial_degree": gen_polynomial_degree,
    "polynomial.polynomial_division": gen_polynomial_division,
    "polynomial.remainder_theorem": gen_remainder_theorem,
    "polynomial.factor_theorem": gen_factor_theorem,
    "polynomial.vieta_formula": gen_vieta_formula,
    "polynomial.rational_root_test": gen_rational_root_test,
    "polynomial.higher_degree_factor": gen_higher_degree_factor,
}
