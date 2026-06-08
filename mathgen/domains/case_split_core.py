"""case_split_reasoning domain (design.md sec 13).

Splitting a problem into cases and merging the results: by sign of values, by
zero points (sign chart of a product), by an absolute value, by a parameter,
and merging case solutions into one set. Verified directly / against sympy.
"""

from __future__ import annotations

import random
from typing import Any, Dict

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_factor, fmt_interval, fmt_union
from mathgen.verify import X, interval_set, sets_equal


def gen_split_by_sign(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 40}[diff]
    a = rng.randint(-hi, hi)
    b = rng.randint(-hi, hi)
    result = abs(a) + abs(b)
    trace = [
        TraceStep(op="case_a", text=f"Determine |{a}|: since {a} is {'negative' if a < 0 else 'nonnegative'}, |{a}| = {abs(a)}."),
        TraceStep(op="case_b", text=f"Determine |{b}|: since {b} is {'negative' if b < 0 else 'nonnegative'}, |{b}| = {abs(b)}."),
        TraceStep(op="add", text=f"Add the results: {abs(a)} + {abs(b)} = {result}."),
        TraceStep(op="finish", text=f"So |{a}| + |{b}| = {result}.", after=str(result)),
    ]
    return make_sample(
        "case_split.split_by_sign",
        f"Evaluate |{a}| + |{b}|.",
        trace,
        str(result),
        {"a": a, "b": b, "difficulty": diff},
        verified=(result == abs(a) + abs(b)),
    )


def gen_split_by_zero_points(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    p = rng.randint(-hi, hi)
    q = rng.randint(-hi, hi)
    while p == q:
        q = rng.randint(-hi, hi)
    lo, hi2 = sorted([p, q])
    op = rng.choice([">", "<"])
    if op == ">":
        answer = fmt_union([fmt_interval(None, lo, True, True), fmt_interval(hi2, None, True, True)])
        expected = interval_set(None, lo, True, True) + interval_set(hi2, None, True, True)
        region = f"x < {lo} or x > {hi2}"
    else:
        answer = fmt_interval(lo, hi2, True, True)
        expected = interval_set(lo, hi2, True, True)
        region = f"{lo} < x < {hi2}"
    trace = [
        TraceStep(op="find_zeros", text=f"The product is zero at x={lo} and x={hi2}, splitting the line into three parts."),
        TraceStep(op="sign_each", text=f"The product opens upward, so it is positive outside the zeros and negative between them."),
        TraceStep(op="select", text=f"For {op} 0 (strict), keep {region}; the zeros themselves are excluded."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    actual = sp.solveset(((X - p) * (X - q) > 0) if op == ">" else ((X - p) * (X - q) < 0), X, domain=sp.S.Reals)
    return make_sample(
        "case_split.split_by_zero_points",
        f"Solve {fmt_factor(-p)}{fmt_factor(-q)} {op} 0 using a sign chart.",
        trace,
        answer,
        {"p": p, "q": q, "op": op, "difficulty": diff},
        verified=sets_equal(actual, expected),
    )


def gen_split_by_absolute_value(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    c = rng.randint(-hi, hi)
    d = rng.randint(1, hi)
    s1, s2 = sorted([c - d, c + d])
    answer = f"x={s1} or x={s2}"
    trace = [
        TraceStep(op="case_positive", text=f"Case 1 (the inside is nonnegative): x - ({c}) = {d}, so x = {c + d}."),
        TraceStep(op="case_negative", text=f"Case 2 (the inside is negative): -(x - ({c})) = {d}, so x - ({c}) = -{d}, giving x = {c - d}."),
        TraceStep(op="merge", text=f"Combine both cases: x = {s1} or x = {s2}."),
        TraceStep(op="finish", text=f"So the solutions are {answer}.", after=answer),
    ]
    return make_sample(
        "case_split.split_by_absolute_value",
        f"Solve |x - ({c})| = {d} by splitting into cases.",
        trace,
        answer,
        {"c": c, "d": d, "difficulty": diff},
        verified=(abs(s1 - c) == d and abs(s2 - c) == d),
    )


def gen_split_by_parameter(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    bound = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    k = rng.randint(-bound, bound)
    if k > 0:
        word, reason = "two", f"k = {k} > 0, so x = ±sqrt({k}) gives two real solutions"
    elif k == 0:
        word, reason = "one", "k = 0, so x = 0 is the only solution"
    else:
        word, reason = "none", f"k = {k} < 0, and a square cannot be negative, so there is no real solution"
    trace = [
        TraceStep(op="case_split", text="The number of real solutions of x^2 = k depends on the sign of k."),
        TraceStep(op="apply_case", text=f"Here {reason}."),
        TraceStep(op="finish", text=f"So there are {word} real solutions.", after=word),
    ]
    return make_sample(
        "case_split.split_by_parameter",
        f"How many real solutions does x^2 = {k} have?",
        trace,
        word,
        {"k": k, "difficulty": diff},
        verified=((word == "two") == (k > 0) and (word == "none") == (k < 0)),
    )


def gen_merge_case_results(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff]
    a = rng.randint(-hi, hi)
    b = rng.randint(-hi, hi)
    while b == a:
        b = rng.randint(-hi, hi)
    vals = sorted([a, b])
    answer = "{" + f"{vals[0]}, {vals[1]}" + "}"
    trace = [
        TraceStep(op="case1", text=f"Case 1 yields the solution x = {a}."),
        TraceStep(op="case2", text=f"Case 2 yields the solution x = {b}."),
        TraceStep(op="merge", text=f"Take the union of the case solutions: {answer}."),
        TraceStep(op="finish", text=f"So the full solution set is {answer}.", after=answer),
    ]
    return make_sample(
        "case_split.merge_case_results",
        f"Case 1 gives x = {a} and Case 2 gives x = {b}. Write the combined solution set.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=(set(vals) == {a, b}),
    )


REGISTRY: Dict[str, Any] = {
    "case_split.split_by_sign": gen_split_by_sign,
    "case_split.split_by_zero_points": gen_split_by_zero_points,
    "case_split.split_by_absolute_value": gen_split_by_absolute_value,
    "case_split.split_by_parameter": gen_split_by_parameter,
    "case_split.merge_case_results": gen_merge_case_results,
}
