"""sympy-backed verification helpers (des_instruct.md sec 7).

Used by the symbolic domains to independently confirm that the rendered answer
is mathematically correct: expression equivalence, solution substitution, and
inequality solution-set equality over the reals.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Sequence, Tuple

import sympy as sp

X = sp.Symbol("x", real=True)


def to_sympy_rational(v) -> sp.Expr:
    if isinstance(v, Fraction):
        return sp.Rational(v.numerator, v.denominator)
    return sp.Integer(v)


def check_equiv(a: sp.Expr, b: sp.Expr) -> bool:
    """True iff expressions a and b are symbolically identical."""
    return sp.simplify(sp.expand(a - b)) == 0


def check_factorization(expanded: sp.Expr, factored: sp.Expr) -> bool:
    return check_equiv(expanded, factored)


def check_solution(lhs: sp.Expr, rhs: sp.Expr, solutions: Sequence[sp.Expr], var: sp.Symbol = X) -> bool:
    """Substitute each solution back into lhs = rhs and confirm equality."""
    for s in solutions:
        if sp.simplify((lhs - rhs).subs(var, s)) != 0:
            return False
    return True


def quadratic_solution_set(a, b, c, op: str, var: sp.Symbol = X) -> sp.Set:
    """Independently solve a*x^2 + b*x + c OP 0 over the reals with sympy."""
    a, b, c = to_sympy_rational(a), to_sympy_rational(b), to_sympy_rational(c)
    expr = a * var**2 + b * var + c
    rel = {
        ">": expr > 0,
        ">=": expr >= 0,
        "<": expr < 0,
        "<=": expr <= 0,
    }[op]
    return sp.solveset(rel, var, domain=sp.S.Reals)


def linear_solution_set(a, b, op: str, var: sp.Symbol = X) -> sp.Set:
    """Solve a*x + b OP 0 over the reals."""
    a, b = to_sympy_rational(a), to_sympy_rational(b)
    expr = a * var + b
    rel = {
        ">": expr > 0,
        ">=": expr >= 0,
        "<": expr < 0,
        "<=": expr <= 0,
    }[op]
    return sp.solveset(rel, var, domain=sp.S.Reals)


def interval_set(low, high, low_open: bool, high_open: bool, var: sp.Symbol = X) -> sp.Set:
    lo = sp.S.NegativeInfinity if low is None else to_sympy_rational(low)
    hi = sp.S.Infinity if high is None else to_sympy_rational(high)
    return sp.Interval(lo, hi, left_open=(low is None or low_open), right_open=(high is None or high_open))


def sets_equal(a: sp.Set, b: sp.Set) -> bool:
    try:
        diff1 = a - b
        diff2 = b - a
        return diff1 == sp.S.EmptySet and diff2 == sp.S.EmptySet
    except Exception:
        return a == b
