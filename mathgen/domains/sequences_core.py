"""sequences_core domain (design.md sec 16).

arithmetic_sequence_nth, arithmetic_sequence_sum and geometric_sequence_nth.
Each formula application is broken into explicit arithmetic steps and the result
is checked against a direct computation, so no step is skipped.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_add, fmt_mul, paren_if_negative


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
        f"In an arithmetic sequence the first term is {a1} and the common difference is {d}. Find the {n}th term.",
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
        f"In a geometric sequence the first term is {a1} and the common ratio is {r}. Find the {n}th term.",
        trace,
        str(result),
        {"a1": a1, "r": r, "n": n, "difficulty": diff},
        verified=(result == a1 * r ** (n - 1)),
    )


REGISTRY: Dict[str, Any] = {
    "sequence.arithmetic_nth_term": gen_arithmetic_nth_term,
    "sequence.arithmetic_series_sum": gen_arithmetic_series_sum,
    "sequence.geometric_nth_term": gen_geometric_nth_term,
}
