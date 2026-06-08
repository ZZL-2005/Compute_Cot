"""inequalities_advanced domain (design.md sec 4.2, 4.4, 4.5, 4.7, 4.8).

Compound, absolute-value, rational (sign chart), exponential and logarithmic
inequalities. Solution sets are rendered as intervals and verified against
sympy where applicable.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction, fmt_interval, fmt_linear, fmt_union
from mathgen.verify import X, interval_set, sets_equal


def _nz(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def gen_compound_inequality(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    a = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff])
    b = rng.randint(-hi, hi)
    lo = rng.randint(-hi, hi)
    width = rng.randint(2, hi)
    high = lo + a * width  # ensure lo < high
    L = Fraction(lo - b, a)
    U = Fraction(high - b, a)
    answer = fmt_interval(L, U, low_open=True, high_open=True)
    expr = fmt_linear(a, b)
    trace = [
        TraceStep(op="state_compound", text=f"Solve the double inequality {lo} < {expr} < {high} by working on all parts at once."),
        TraceStep(op="subtract_b", text=f"Subtract {b}: {lo - b} < {a}x < {high - b}."),
        TraceStep(op="divide_a", text=f"Divide by {a} (positive, keep directions): {fmt_fraction(L)} < x < {fmt_fraction(U)}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    actual = sp.solveset(a * X + b > lo, X, domain=sp.S.Reals).intersect(
        sp.solveset(a * X + b < high, X, domain=sp.S.Reals)
    )
    expected = interval_set(L, U, low_open=True, high_open=True)
    return make_sample(
        "inequality.compound_inequality",
        f"Solve {lo} < {expr} < {high}.",
        trace,
        answer,
        {"a": a, "b": b, "lo": lo, "high": high, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_absolute_value_inequality(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    c = rng.randint(-hi, hi)
    d = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    inner = fmt_linear(1, -c)
    less = rng.random() < 0.5
    if less:  # |x - c| < d  ->  (c-d, c+d)
        answer = fmt_interval(c - d, c + d, low_open=True, high_open=True)
        expected = interval_set(c - d, c + d, low_open=True, high_open=True)
        rel = "<"
        trace = [
            TraceStep(op="state_rule", text=f"|{inner}| < {d} means -{d} < {inner} < {d}."),
            TraceStep(op="add_c", text=f"Add {c} to all parts: {c - d} < x < {c + d}."),
        ]
    else:  # |x - c| > d  ->  (-inf, c-d) ∪ (c+d, inf)
        answer = fmt_union([
            fmt_interval(None, c - d, True, True),
            fmt_interval(c + d, None, True, True),
        ])
        expected = interval_set(None, c - d, True, True) + interval_set(c + d, None, True, True)
        rel = ">"
        trace = [
            TraceStep(op="state_rule", text=f"|{inner}| > {d} means {inner} < -{d} or {inner} > {d}."),
            TraceStep(op="split", text=f"Solving each: x < {c - d} or x > {c + d}."),
        ]
    trace.append(TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer))
    actual = sp.solveset(sp.Abs(X - c) < d if less else sp.Abs(X - c) > d, X, domain=sp.S.Reals)
    return make_sample(
        "inequality.absolute_value_inequality",
        f"Solve |{inner}| {rel} {d}.",
        trace,
        answer,
        {"c": c, "d": d, "rel": rel, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_rational_inequality(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    p = rng.randint(-hi, hi)
    q = rng.randint(-hi, hi)
    while p == q:
        q = rng.randint(-hi, hi)
    op = rng.choice([">", "<"])  # strict, so every endpoint is open
    lo, hi2 = sorted([p, q])

    def sign_at(t: Fraction) -> int:
        val = (t - p) / (t - q)
        return 1 if val > 0 else -1

    t1, t2, t3 = Fraction(lo - 1), Fraction(lo + hi2, 2), Fraction(hi2 + 1)
    regions = [
        (interval_set(None, lo, True, True), fmt_interval(None, lo, True, True), sign_at(t1)),
        (interval_set(lo, hi2, True, True), fmt_interval(lo, hi2, True, True), sign_at(t2)),
        (interval_set(hi2, None, True, True), fmt_interval(hi2, None, True, True), sign_at(t3)),
    ]
    want = 1 if op == ">" else -1
    chosen = [(s, txt) for s, txt, sg in regions if sg == want]
    parts = [txt for _, txt in chosen]
    answer = fmt_union(parts) if len(parts) > 1 else parts[0]
    expected = chosen[0][0]
    for s, _ in chosen[1:]:
        expected = expected + s

    num = fmt_linear(1, -p)
    den = fmt_linear(1, -q)
    trace = [
        TraceStep(op="find_critical", text=f"The expression ({num})/({den}) has a zero at x={p} and is undefined at x={q}."),
        TraceStep(op="split_line", text=f"These split the line into (-∞, {lo}), ({lo}, {hi2}), and ({hi2}, +∞)."),
        TraceStep(op="sign_chart", text=f"Test each region; the sign of the fraction is {'+' if regions[0][2] > 0 else '-'}, {'+' if regions[1][2] > 0 else '-'}, {'+' if regions[2][2] > 0 else '-'} respectively."),
        TraceStep(op="select", text=f"Keep the regions where the fraction is {'positive' if want > 0 else 'negative'}; endpoints are open ({p} excluded as strict, {q} excluded as a pole)."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    actual = sp.solveset(((X - p) / (X - q) > 0) if op == ">" else ((X - p) / (X - q) < 0), X, domain=sp.S.Reals)
    return make_sample(
        "inequality.rational_inequality",
        f"Solve ({num})/({den}) {op} 0.",
        trace,
        answer,
        {"p": p, "q": q, "op": op, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_exponential_inequality(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[diff])
    k = rng.randint(1, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 8}[diff])
    value = base**k
    answer = fmt_interval(k, None, low_open=True, high_open=True)
    trace = [
        TraceStep(op="same_base", text=f"Write {value} as a power of {base}: {value} = {base}^{k}."),
        TraceStep(op="compare_exponents", text=f"The inequality is {base}^x > {base}^{k}. Since the base {base} > 1, the function is increasing, so the inequality holds when x > {k}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "inequality.exponential_inequality",
        f"Solve {base}^x > {value}.",
        trace,
        answer,
        {"base": base, "k": k, "difficulty": diff},
        verified=(base**k == value and base > 1),
    )


def gen_logarithmic_inequality(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[diff])
    k = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff])
    value = base**k
    answer = fmt_interval(value, None, low_open=True, high_open=True)
    trace = [
        TraceStep(op="domain", text="The argument of a logarithm must be positive, so x > 0."),
        TraceStep(op="rewrite", text=f"log_{base}(x) > {k} means x > {base}^{k} = {value} (base {base} > 1, increasing)."),
        TraceStep(op="combine", text=f"Combined with x > 0, the binding condition is x > {value}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "inequality.logarithmic_inequality",
        f"Solve log_{base}(x) > {k}.",
        trace,
        answer,
        {"base": base, "k": k, "difficulty": diff},
        verified=(base**k == value and base > 1),
    )


REGISTRY: Dict[str, Any] = {
    "inequality.compound_inequality": gen_compound_inequality,
    "inequality.absolute_value_inequality": gen_absolute_value_inequality,
    "inequality.rational_inequality": gen_rational_inequality,
    "inequality.exponential_inequality": gen_exponential_inequality,
    "inequality.logarithmic_inequality": gen_logarithmic_inequality,
}
