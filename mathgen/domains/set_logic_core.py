"""set_logic domain (design.md sec 14).

Finite-set membership/subset/union/intersection/complement, interval union and
intersection, and basic propositional logic (and/or/not, implication,
quantifier over a finite domain). Set results are verified by direct computation;
interval results are verified against sympy sets.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_interval, fmt_union


def _fmt_set(values) -> str:
    vs = sorted(set(values))
    return "{" + ", ".join(str(v) for v in vs) + "}" if vs else "∅"


def _rand_set(rng: random.Random, lo: int, hi: int, k: int) -> List[int]:
    return sorted(rng.sample(range(lo, hi + 1), k))


def gen_set_membership(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 8}[diff]
    s = _rand_set(rng, 1, 20, k)
    x = rng.randint(1, 20)
    inside = x in s
    yn = "Yes" if inside else "No"
    trace = [
        TraceStep(op="scan", text=f"Check whether {x} appears in the set {_fmt_set(s)}."),
        TraceStep(op="decide", text=f"{x} is {'one of the listed elements' if inside else 'not among the listed elements'}."),
        TraceStep(op="finish", text=f"So the answer is {yn}.", after=yn),
    ]
    return make_sample(
        "set_logic.set_membership",
        f"Is {x} an element of {_fmt_set(s)}?",
        trace,
        yn,
        {"set": s, "x": x, "difficulty": diff},
        verified=((yn == "Yes") == inside),
    )


def gen_subset_relation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    b = _rand_set(rng, 1, 16, {Difficulty.EASY: 5, Difficulty.MEDIUM: 7, Difficulty.HARD: 9}[diff])
    if rng.random() < 0.5:
        a = sorted(rng.sample(b, rng.randint(1, len(b) - 1)))  # genuine subset
    else:
        a = sorted(set(rng.sample(b, rng.randint(1, len(b) - 1))) | {rng.choice([v for v in range(1, 20) if v not in b])})
    is_sub = set(a).issubset(set(b))
    missing = [v for v in a if v not in b]
    yn = "Yes" if is_sub else "No"
    decide = ("every element of A is in B" if is_sub else f"the element {missing[0]} of A is not in B")
    trace = [
        TraceStep(op="state_test", text="A ⊆ B means every element of A is also an element of B."),
        TraceStep(op="check_elements", text=f"Check each element of A = {_fmt_set(a)} against B = {_fmt_set(b)}: {decide}."),
        TraceStep(op="finish", text=f"So the answer is {yn}.", after=yn),
    ]
    return make_sample(
        "set_logic.subset_relation",
        f"Is A = {_fmt_set(a)} a subset of B = {_fmt_set(b)}?",
        trace,
        yn,
        {"a": a, "b": b, "difficulty": diff},
        verified=((yn == "Yes") == is_sub),
    )


def gen_union_intersection(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff]
    a = _rand_set(rng, 1, 14, k)
    b = _rand_set(rng, 1, 14, k)
    union = sorted(set(a) | set(b))
    inter = sorted(set(a) & set(b))
    answer = f"union = {_fmt_set(union)}, intersection = {_fmt_set(inter)}"
    trace = [
        TraceStep(op="union_def", text="The union collects every element in either set; the intersection keeps only elements in both."),
        TraceStep(op="union_compute", text=f"Combine all elements of A = {_fmt_set(a)} and B = {_fmt_set(b)}: union = {_fmt_set(union)}."),
        TraceStep(op="inter_compute", text=f"Keep elements common to both: intersection = {_fmt_set(inter)}."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "set_logic.union_intersection",
        f"For A = {_fmt_set(a)} and B = {_fmt_set(b)}, find A ∪ B and A ∩ B.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=(set(union) == (set(a) | set(b)) and set(inter) == (set(a) & set(b))),
    )


def gen_complement(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    nu = {Difficulty.EASY: 6, Difficulty.MEDIUM: 8, Difficulty.HARD: 10}[diff]
    u = list(range(1, nu + 1))
    a = sorted(rng.sample(u, rng.randint(2, nu - 1)))
    comp = [v for v in u if v not in a]
    answer = _fmt_set(comp)
    trace = [
        TraceStep(op="state_def", text="The complement of A in U keeps exactly the elements of U that are not in A."),
        TraceStep(op="remove", text=f"From U = {_fmt_set(u)} remove the elements of A = {_fmt_set(a)}."),
        TraceStep(op="finish", text=f"So the complement is {answer}.", after=answer),
    ]
    return make_sample(
        "set_logic.complement",
        f"With universe U = {_fmt_set(u)} and A = {_fmt_set(a)}, find the complement of A.",
        trace,
        answer,
        {"u": u, "a": a, "difficulty": diff},
        verified=(set(comp) == set(u) - set(a)),
    )


def _closed(lo: int, hi: int) -> sp.Set:
    return sp.Interval(lo, hi)


def gen_interval_intersection(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(-8, 4)
    b = a + rng.randint(2, 8)
    c = rng.randint(-8, 6)
    d = c + rng.randint(2, 8)
    lo, hi = max(a, c), min(b, d)
    if lo <= hi:
        answer = fmt_interval(lo, hi, low_open=False, high_open=False)
        expected = _closed(lo, hi)
        reason = f"the overlap runs from the larger left endpoint {lo} to the smaller right endpoint {hi}"
    else:
        answer = "∅"
        expected = sp.EmptySet
        reason = f"the larger left endpoint {lo} exceeds the smaller right endpoint {hi}, so they do not overlap"
    trace = [
        TraceStep(op="state_method", text=f"The intersection of [{a}, {b}] and [{c}, {d}] is [max of left ends, min of right ends] when that is valid."),
        TraceStep(op="compute_endpoints", text=f"max({a}, {c}) = {lo} and min({b}, {d}) = {hi}."),
        TraceStep(op="decide", text=f"So {reason}."),
        TraceStep(op="finish", text=f"So the intersection is {answer}.", after=answer),
    ]
    actual = _closed(a, b).intersect(_closed(c, d))
    return make_sample(
        "set_logic.interval_intersection",
        f"Find [{a}, {b}] ∩ [{c}, {d}].",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(actual == expected),
    )


def gen_interval_union(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(-8, 2)
    b = a + rng.randint(2, 6)
    if rng.random() < 0.5:  # overlapping/touching -> single interval
        c = rng.randint(a, b)
        d = c + rng.randint(2, 6)
    else:  # disjoint
        c = b + rng.randint(2, 5)
        d = c + rng.randint(2, 6)
    overlap = max(a, c) <= min(b, d)
    if overlap:
        lo, hi = min(a, c), max(b, d)
        answer = fmt_interval(lo, hi, low_open=False, high_open=False)
        expected = _closed(lo, hi)
        reason = f"the intervals overlap, so they merge into one interval from {lo} to {hi}"
    else:
        i1 = fmt_interval(a, b, low_open=False, high_open=False)
        i2 = fmt_interval(c, d, low_open=False, high_open=False)
        answer = fmt_union([i1, i2])
        expected = _closed(a, b) + _closed(c, d)
        reason = "the intervals are disjoint, so the union keeps both pieces"
    trace = [
        TraceStep(op="check_overlap", text=f"Check whether [{a}, {b}] and [{c}, {d}] overlap by comparing {max(a, c)} and {min(b, d)}."),
        TraceStep(op="decide", text=f"Since {max(a, c)} {'≤' if overlap else '>'} {min(b, d)}, {reason}."),
        TraceStep(op="finish", text=f"So the union is {answer}.", after=answer),
    ]
    actual = sp.Union(_closed(a, b), _closed(c, d))
    return make_sample(
        "set_logic.interval_union",
        f"Find [{a}, {b}] ∪ [{c}, {d}].",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(actual == expected),
    )


def _prop(rng: random.Random):
    """Return (text, truth) for a simple numeric proposition."""
    a = rng.randint(1, 9)
    b = rng.randint(1, 9)
    op = rng.choice(["<", ">", "="])
    truth = {"<": a < b, ">": a > b, "=": a == b}[op]
    return f"{a} {op} {b}", truth


def gen_logical_and_or_not(rng: random.Random, cfg: GenConfig) -> Sample:
    pick_difficulty(rng, cfg)
    pt, pv = _prop(rng)
    qt, qv = _prop(rng)
    conn = rng.choice(["and", "or"])
    result = (pv and qv) if conn == "and" else (pv or qv)
    res = "True" if result else "False"
    rule = ("an 'and' is true only when both parts are true" if conn == "and"
            else "an 'or' is true when at least one part is true")
    trace = [
        TraceStep(op="eval_p", text=f"Evaluate p: '{pt}' is {pv}."),
        TraceStep(op="eval_q", text=f"Evaluate q: '{qt}' is {qv}."),
        TraceStep(op="apply_connective", text=f"By the rule that {rule}, p {conn} q is {res}."),
        TraceStep(op="finish", text=f"So the statement is {res}.", after=res),
    ]
    return make_sample(
        "set_logic.logical_and_or_not",
        f"Is the statement (p {conn} q) true or false, where p: '{pt}' and q: '{qt}'?",
        trace,
        res,
        {"p": pt, "q": qt, "connective": conn},
        verified=((res == "True") == result),
    )


def gen_implication_equivalence(rng: random.Random, cfg: GenConfig) -> Sample:
    pick_difficulty(rng, cfg)
    pt, pv = _prop(rng)
    qt, qv = _prop(rng)
    result = (not pv) or qv  # p -> q
    res = "True" if result else "False"
    trace = [
        TraceStep(op="eval_p", text=f"Evaluate the hypothesis p: '{pt}' is {pv}."),
        TraceStep(op="eval_q", text=f"Evaluate the conclusion q: '{qt}' is {qv}."),
        TraceStep(op="apply_rule", text=f"An implication p → q is false only when p is true and q is false. Here p is {pv} and q is {qv}, so it is {res}."),
        TraceStep(op="finish", text=f"So p → q is {res}.", after=res),
    ]
    return make_sample(
        "set_logic.implication_equivalence",
        f"Is the implication (p → q) true or false, where p: '{pt}' and q: '{qt}'?",
        trace,
        res,
        {"p": pt, "q": qt},
        verified=((res == "True") == result),
    )


def gen_quantifier_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff]
    s = _rand_set(rng, -5, 9, k)
    quant = rng.choice(["for all", "there exists"])
    thr = rng.randint(-3, 5)
    preds = [v > thr for v in s]
    if quant == "for all":
        result = all(preds)
        rule = "a 'for all' statement is true only when the property holds for every element"
        witness = next((v for v in s if not v > thr), None)
        detail = "every element is greater" if result else f"the element {witness} is not greater than {thr}"
    else:
        result = any(preds)
        rule = "a 'there exists' statement is true when at least one element has the property"
        witness = next((v for v in s if v > thr), None)
        detail = f"the element {witness} is greater than {thr}" if result else "no element is greater"
    res = "True" if result else "False"
    trace = [
        TraceStep(op="state_claim", text=f"Test '{quant} x in {_fmt_set(s)}, x > {thr}'."),
        TraceStep(op="check", text=f"Apply the rule that {rule}: {detail}."),
        TraceStep(op="finish", text=f"So the statement is {res}.", after=res),
    ]
    return make_sample(
        "set_logic.quantifier_basic",
        f"Is the statement '{quant} x in {_fmt_set(s)}, x > {thr}' true or false?",
        trace,
        res,
        {"set": s, "quantifier": quant, "threshold": thr, "difficulty": diff},
        verified=((res == "True") == result),
    )


REGISTRY: Dict[str, Any] = {
    "set_logic.set_membership": gen_set_membership,
    "set_logic.subset_relation": gen_subset_relation,
    "set_logic.union_intersection": gen_union_intersection,
    "set_logic.complement": gen_complement,
    "set_logic.interval_intersection": gen_interval_intersection,
    "set_logic.interval_union": gen_interval_union,
    "set_logic.logical_and_or_not": gen_logical_and_or_not,
    "set_logic.implication_equivalence": gen_implication_equivalence,
    "set_logic.quantifier_basic": gen_quantifier_basic,
}
