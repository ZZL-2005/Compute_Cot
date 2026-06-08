"""sequences_core domain (design.md sec 16).

arithmetic_sequence_nth, arithmetic_sequence_sum and geometric_sequence_nth.
Each formula application is broken into explicit arithmetic steps and the result
is checked against a direct computation, so no step is skipped.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_add, fmt_fraction, fmt_mul, fmt_signed_term, ordinal, paren_if_negative


def _nonzero(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def gen_arithmetic_nth_term(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff]
    a1 = rng.randint(-hi, hi)
    d = _nonzero(rng, -hi, hi)
    n = rng.randint(4, {Difficulty.EASY: 8, Difficulty.MEDIUM: 20, Difficulty.HARD: 50}[diff])

    nm1 = n - 1
    prod = nm1 * d
    result = a1 + prod

    trace = [
        TraceStep(op="identify", text=f"This is an arithmetic sequence with first term a_1={a1} and common difference d={d}."),
        TraceStep(op="state_formula", text="Use a_n = a_1 + (n - 1)d."),
        TraceStep(op="compute_index", text=f"Here n={n}, so n - 1 = {nm1}."),
        TraceStep(op="multiply", text=f"Compute (n - 1)d: {fmt_mul(nm1, d)} = {prod}.", meta={"prod": prod}),
        TraceStep(op="add", text=f"Add the first term: {fmt_add(a1, prod)} = {result}.", meta={"result": result}),
        TraceStep(op="finish", text=f"So a_{n} = {result}.", after=str(result)),
    ]
    return make_sample(
        "sequence.arithmetic_nth_term",
        f"In an arithmetic sequence the first term is {a1} and the common difference is {d}. Find the {ordinal(n)} term.",
        trace,
        str(result),
        {"a1": a1, "d": d, "n": n, "difficulty": diff},
        verified=(result == a1 + (n - 1) * d),
    )


def gen_arithmetic_series_sum(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff]
    a1 = rng.randint(-hi, hi)
    d = _nonzero(rng, -hi, hi)
    n = rng.randint(4, {Difficulty.EASY: 8, Difficulty.MEDIUM: 16, Difficulty.HARD: 30}[diff])

    nm1 = n - 1
    an = a1 + nm1 * d
    pair = a1 + an
    ns = n * pair
    result = ns // 2

    trace = [
        TraceStep(op="identify", text=f"This is an arithmetic sequence with first term a_1={a1}, common difference d={d}, and n={n} terms."),
        TraceStep(op="last_term", text=f"Find the last term a_{n} = a_1 + (n - 1)d = {a1} + {fmt_mul(nm1, d)} = {an}.", meta={"an": an}),
        TraceStep(op="state_formula", text="Use S_n = n × (a_1 + a_n) / 2."),
        TraceStep(op="add_first_last", text=f"Add the first and last term: {fmt_add(a1, an)} = {pair}.", meta={"pair": pair}),
        TraceStep(op="multiply_by_n", text=f"Multiply by n: {fmt_mul(n, pair)} = {ns}.", meta={"ns": ns}),
        TraceStep(op="divide_by_two", text=f"Divide by 2: {ns}/2 = {result}.", meta={"result": result}),
        TraceStep(op="finish", text=f"So S_{n} = {result}.", after=str(result)),
    ]
    return make_sample(
        "sequence.arithmetic_series_sum",
        f"Find the sum of the first {n} terms of the arithmetic sequence with first term {a1} and common difference {d}.",
        trace,
        str(result),
        {"a1": a1, "d": d, "n": n, "difficulty": diff},
        verified=(ns == 2 * result and result == sum(a1 + i * d for i in range(n))),
    )


def gen_geometric_nth_term(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1_bound = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 12}[diff]
    a1 = _nonzero(rng, -a1_bound, a1_bound)
    r = rng.choice([-3, -2, 2, 3] if diff != Difficulty.EASY else [2, 3])
    n = rng.randint(3, {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff])

    nm1 = n - 1
    power = r**nm1
    result = a1 * power

    trace = [
        TraceStep(op="identify", text=f"This is a geometric sequence with first term a_1={a1} and common ratio r={r}."),
        TraceStep(op="state_formula", text="Use a_n = a_1 × r^(n - 1)."),
        TraceStep(op="compute_index", text=f"Here n={n}, so n - 1 = {nm1}."),
        TraceStep(op="compute_power", text=f"Compute r^(n - 1): {paren_if_negative(r)}^{nm1} = {power}.", meta={"power": power}),
        TraceStep(op="multiply", text=f"Multiply by the first term: {fmt_mul(a1, power)} = {result}.", meta={"result": result}),
        TraceStep(op="finish", text=f"So a_{n} = {result}.", after=str(result)),
    ]
    return make_sample(
        "sequence.geometric_nth_term",
        f"In a geometric sequence the first term is {a1} and the common ratio is {r}. Find the {ordinal(n)} term.",
        trace,
        str(result),
        {"a1": a1, "r": r, "n": n, "difficulty": diff},
        verified=(result == a1 * r ** (n - 1)),
    )


def gen_geometric_series_sum(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1 = rng.randint(1, {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff])
    r = rng.choice([2, 3] if diff != Difficulty.HARD else [2, 3, 4])
    n = rng.randint(3, {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff])
    rn = r**n
    num = rn - 1
    den = r - 1
    result = a1 * num // den

    trace = [
        TraceStep(op="identify", text=f"This is a geometric sequence with first term a_1={a1}, common ratio r={r}, and n={n} terms."),
        TraceStep(op="state_formula", text="Use S_n = a_1 × (r^n - 1) / (r - 1)."),
        TraceStep(op="compute_power", text=f"Compute r^n = {r}^{n} = {rn}."),
        TraceStep(op="numerator", text=f"Numerator: r^n - 1 = {rn} - 1 = {num}."),
        TraceStep(op="denominator", text=f"Denominator: r - 1 = {r} - 1 = {den}."),
        TraceStep(op="combine", text=f"So S_n = {a1} × {num}/{den} = {a1} × {num // den} = {result}."),
        TraceStep(op="finish", text=f"So S_{n} = {result}.", after=str(result)),
    ]
    return make_sample(
        "sequence.geometric_series_sum",
        f"Find the sum of the first {n} terms of the geometric sequence with first term {a1} and common ratio {r}.",
        trace,
        str(result),
        {"a1": a1, "r": r, "n": n, "difficulty": diff},
        verified=(result == sum(a1 * r**i for i in range(n))),
    )


def gen_recurrence_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1 = rng.randint(-5, 5)
    p = rng.randint(2, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff])
    q = _nonzero(rng, -6, 6)
    k = rng.randint(4, {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff])

    # Avoid "+ (-5)" pattern per des_instruct.md sec 5.
    q_sign = fmt_signed_term(q, '', first=False)

    terms = [a1]
    trace = [
        TraceStep(op="state_rule", text=f"The recurrence is a_(n+1) = {p}·a_n{q_sign}, with a_1 = {a1}."),
        TraceStep(op="first_term", text=f"a_1 = {a1}."),
    ]
    for idx in range(1, k):
        prev = terms[-1]
        pa = p * prev
        nxt = pa + q
        trace.append(TraceStep(
            op="next_term",
            text=f"a_{idx+1} = {p}×{paren_if_negative(prev)}{q_sign} = {pa}{q_sign} = {nxt}.",
            meta={"index": idx + 1, "value": nxt},
        ))
        terms.append(nxt)
    result = terms[-1]
    trace.append(TraceStep(op="finish", text=f"So a_{k} = {result}.", after=str(result)))
    return make_sample(
        "sequence.recurrence_basic",
        f"A sequence satisfies a_1 = {a1} and a_(n+1) = {p}·a_n{q_sign}. Find a_{k}.",
        trace,
        str(result),
        {"a1": a1, "p": p, "q": q, "k": k, "difficulty": diff},
        verified=(len(terms) == k),
    )


def gen_sigma_notation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff])
    b = _nonzero(rng, -6, 8)
    n = rng.randint(3, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    tri = n * (n + 1) // 2
    a_tri = a * tri
    bn = b * n
    result = a_tri + bn

    # Avoid "+ (-5)" pattern per des_instruct.md sec 5.
    b_sign = fmt_signed_term(b, '', first=False)

    trace = [
        TraceStep(op="split_sum", text=f"Split the sum: sum_(i=1)^{n} ({a}i{b_sign}) = {a}·sum_(i=1)^{n} i + sum_(i=1)^{n} ({b})."),
        TraceStep(op="sum_of_i", text=f"Use sum_(i=1)^{n} i = n(n+1)/2 = {n}×{n+1}/2 = {tri}."),
        TraceStep(op="scale_first", text=f"Multiply by {a}: {a}×{tri} = {a_tri}."),
        TraceStep(op="sum_constant", text=f"The constant term adds {n} times: {b}×{n} = {bn}."),
        TraceStep(op="combine", text=f"Add the parts: {fmt_add(a_tri, bn)} = {result}."),
        TraceStep(op="finish", text=f"So the sum is {result}.", after=str(result)),
    ]
    return make_sample(
        "sequence.sigma_notation",
        f"Evaluate sum_(i=1)^{n} ({a}i{b_sign}).",
        trace,
        str(result),
        {"a": a, "b": b, "n": n, "difficulty": diff},
        verified=(result == sum(a * i + b for i in range(1, n + 1))),
    )


def gen_telescoping_sum(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(3, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 20}[diff])
    result = Fraction(n, n + 1)
    trace = [
        TraceStep(op="partial_fractions", text="Decompose each term: 1/(k(k+1)) = 1/k - 1/(k+1)."),
        TraceStep(op="write_telescope", text=f"So the sum is (1/1 - 1/2) + (1/2 - 1/3) + ... + (1/{n} - 1/{n+1})."),
        TraceStep(op="cancel", text=f"All middle terms cancel, leaving 1 - 1/{n+1}."),
        TraceStep(op="combine", text=f"Combine: 1 - 1/{n+1} = {fmt_fraction(result)}."),
        TraceStep(op="finish", text=f"So the sum is {fmt_fraction(result)}.", after=fmt_fraction(result)),
    ]
    return make_sample(
        "sequence.telescoping_sum",
        f"Evaluate sum_(k=1)^{n} 1/(k(k+1)).",
        trace,
        fmt_fraction(result),
        {"n": n, "difficulty": diff},
        verified=(result == sum(Fraction(1, k * (k + 1)) for k in range(1, n + 1))),
    )


REGISTRY: Dict[str, Any] = {
    "sequence.arithmetic_nth_term": gen_arithmetic_nth_term,
    "sequence.arithmetic_series_sum": gen_arithmetic_series_sum,
    "sequence.geometric_nth_term": gen_geometric_nth_term,
    "sequence.geometric_series_sum": gen_geometric_series_sum,
    "sequence.recurrence_basic": gen_recurrence_basic,
    "sequence.sigma_notation": gen_sigma_notation,
    "sequence.telescoping_sum": gen_telescoping_sum,
}
