"""sequence_schema domain (design.md sec 30)."""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction


def gen_arithmetic_sequence_nth_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1 = rng.randint(1, 20)
    d = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    n = rng.randint(3, {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff])
    ans = a1 + (n - 1) * d
    trace = [
        TraceStep(op="formula", text=f"For an arithmetic sequence, a_n = a_1 + (n - 1)d."),
        TraceStep(op="substitute", text=f"a_{n} = {a1} + ({n} - 1)×{d} = {a1} + {(n - 1) * d} = {ans}."),
        TraceStep(op="finish", text=f"So a_{n} = {ans}.", after=str(ans)),
    ]
    return make_sample("sequence_schema.arithmetic_sequence_nth_schema", f"In an arithmetic sequence, a_1={a1} and d={d}. Find a_{n}.", trace, str(ans), {"a1": a1, "d": d, "n": n, "difficulty": diff}, verified=(ans == a1 + (n - 1) * d))


def gen_arithmetic_sequence_sum_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1 = rng.randint(1, 20)
    d = rng.randint(1, 12)
    n = rng.randint(3, {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff])
    an = a1 + (n - 1) * d
    total = n * (a1 + an) // 2
    trace = [
        TraceStep(op="find_last", text=f"First find a_{n} = {a1} + ({n} - 1)×{d} = {an}."),
        TraceStep(op="sum_formula", text=f"S_n = n(a_1 + a_n)/2 = {n}×({a1} + {an})/2 = {total}."),
        TraceStep(op="finish", text=f"So S_{n} = {total}.", after=str(total)),
    ]
    return make_sample("sequence_schema.arithmetic_sequence_sum_schema", f"In an arithmetic sequence, a_1={a1} and d={d}. Find S_{n}.", trace, str(total), {"a1": a1, "d": d, "n": n, "difficulty": diff}, verified=(total == n * (a1 + an) // 2))


def gen_geometric_sequence_nth_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1 = rng.randint(1, 8)
    r = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff])
    n = rng.randint(3, {Difficulty.EASY: 6, Difficulty.MEDIUM: 8, Difficulty.HARD: 10}[diff])
    ans = a1 * (r ** (n - 1))
    trace = [
        TraceStep(op="formula", text="For a geometric sequence, a_n = a_1 r^(n - 1)."),
        TraceStep(op="substitute", text=f"a_{n} = {a1}×{r}^{n - 1} = {a1}×{r ** (n - 1)} = {ans}."),
        TraceStep(op="finish", text=f"So a_{n} = {ans}.", after=str(ans)),
    ]
    return make_sample("sequence_schema.geometric_sequence_nth_schema", f"In a geometric sequence, a_1={a1} and r={r}. Find a_{n}.", trace, str(ans), {"a1": a1, "r": r, "n": n, "difficulty": diff}, verified=(ans == a1 * r ** (n - 1)))


def gen_geometric_sequence_sum_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1 = rng.randint(1, 8)
    r = rng.randint(2, 5)
    n = rng.randint(3, {Difficulty.EASY: 6, Difficulty.MEDIUM: 8, Difficulty.HARD: 10}[diff])
    total = a1 * (r**n - 1) // (r - 1)
    trace = [
        TraceStep(op="formula", text="For r not equal to 1, S_n = a_1(r^n - 1)/(r - 1)."),
        TraceStep(op="substitute", text=f"S_{n} = {a1}×({r}^{n} - 1)/({r} - 1) = {total}."),
        TraceStep(op="finish", text=f"So S_{n} = {total}.", after=str(total)),
    ]
    return make_sample("sequence_schema.geometric_sequence_sum_schema", f"In a geometric sequence, a_1={a1} and r={r}. Find S_{n}.", trace, str(total), {"a1": a1, "r": r, "n": n, "difficulty": diff}, verified=(total == sum(a1 * r**i for i in range(n))))


def gen_recurrence_to_terms(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a1 = rng.randint(1, 20)
    d = rng.randint(1, 10)
    n = rng.randint(4, {Difficulty.EASY: 6, Difficulty.MEDIUM: 8, Difficulty.HARD: 10}[diff])
    terms = [a1 + i * d for i in range(n)]
    answer = ", ".join(str(t) for t in terms)
    trace = [
        TraceStep(op="start", text=f"Start with a_1 = {a1}."),
        TraceStep(op="apply_recurrence", text=f"Each next term adds {d}, producing {answer}."),
        TraceStep(op="finish", text=f"So the first {n} terms are {answer}.", after=answer),
    ]
    return make_sample("sequence_schema.recurrence_to_terms", f"Given a_1={a1} and a_n=a_(n-1)+{d}, list the first {n} terms.", trace, answer, {"a1": a1, "d": d, "n": n, "difficulty": diff}, verified=(terms == [a1 + i * d for i in range(n)]))


def gen_telescoping_sum_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(3, {Difficulty.EASY: 8, Difficulty.MEDIUM: 20, Difficulty.HARD: 50}[diff])
    ans_fr = Fraction(n, n + 1)
    ans = fmt_fraction(ans_fr)
    trace = [
        TraceStep(op="expand", text=f"The sum is (1 - 1/2) + (1/2 - 1/3) + ... + (1/{n} - 1/{n + 1})."),
        TraceStep(op="cancel", text=f"All middle terms cancel, leaving 1 - 1/{n + 1}."),
        TraceStep(op="finish", text=f"So the sum is {ans}.", after=ans),
    ]
    return make_sample("sequence_schema.telescoping_sum_schema", f"Compute sum from i=1 to {n} of (1/i - 1/(i+1)).", trace, ans, {"n": n, "difficulty": diff}, verified=(ans_fr == sum(Fraction(1, i) - Fraction(1, i + 1) for i in range(1, n + 1))))


REGISTRY: Dict[str, Any] = {
    "sequence_schema.arithmetic_sequence_nth_schema": gen_arithmetic_sequence_nth_schema,
    "sequence_schema.arithmetic_sequence_sum_schema": gen_arithmetic_sequence_sum_schema,
    "sequence_schema.geometric_sequence_nth_schema": gen_geometric_sequence_nth_schema,
    "sequence_schema.geometric_sequence_sum_schema": gen_geometric_sequence_sum_schema,
    "sequence_schema.recurrence_to_terms": gen_recurrence_to_terms,
    "sequence_schema.telescoping_sum_schema": gen_telescoping_sum_schema,
}
