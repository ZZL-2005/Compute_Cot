"""combinatorics_probability_statistics domain (design.md sec 20).

Permutations, combinations, the counting principle, binomial coefficients,
basic / conditional / independent probability, expectation, mean-median-mode,
and population variance. Exact integer/fraction arithmetic verified directly.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from fractions import Fraction
from typing import Any, Dict, List

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import pick_template,  fmt_fraction, fmt_value


def gen_permutation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(4, {Difficulty.EASY: 6, Difficulty.MEDIUM: 9, Difficulty.HARD: 12}[diff])
    r = rng.randint(2, n - 1)
    factors = list(range(n, n - r, -1))
    result = math.perm(n, r)
    prod_text = "×".join(str(f) for f in factors)
    trace = [
        TraceStep(op="state_formula", text=f"A permutation counts ordered choices: P(n, r) = n!/(n-r)! = n×(n-1)×...×(n-r+1)."),
        TraceStep(op="expand", text=f"P({n}, {r}) = {prod_text} ({r} factors counting down from {n})."),
        TraceStep(op="multiply", text=f"{prod_text} = {result}."),
        TraceStep(op="finish", text=f"So P({n}, {r}) = {result}.", after=str(result)),
    ]
    return make_sample(
        "combinatorics.permutation",
        pick_template(rng, f"Compute the number of permutations P({n}, {r}).", f"Find P({n}, {r}).", f"How many permutations of {n} items taken {r} at a time?", f"Calculate the number of ordered arrangements of {r} items from {n}."),
        trace,
        str(result),
        {"n": n, "r": r, "difficulty": diff},
        verified=(result == math.perm(n, r)),
    )


def gen_combination(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(4, {Difficulty.EASY: 6, Difficulty.MEDIUM: 9, Difficulty.HARD: 12}[diff])
    r = rng.randint(2, n - 1)
    perm = math.perm(n, r)
    rfact = math.factorial(r)
    result = math.comb(n, r)
    factors = "×".join(str(f) for f in range(n, n - r, -1))
    trace = [
        TraceStep(op="state_formula", text="A combination counts unordered choices: C(n, r) = P(n, r)/r! = n×...×(n-r+1) / r!."),
        TraceStep(op="numerator", text=f"Numerator: {factors} = {perm}."),
        TraceStep(op="denominator", text=f"Denominator: {r}! = {rfact}."),
        TraceStep(op="divide", text=f"C({n}, {r}) = {perm}/{rfact} = {result}."),
        TraceStep(op="finish", text=f"So C({n}, {r}) = {result}.", after=str(result)),
    ]
    return make_sample(
        "combinatorics.combination",
        pick_template(rng, f"Compute the number of combinations C({n}, {r}).", f"Find C({n}, {r}).", f"How many ways to choose {r} items from {n}?", f"Calculate the number of unordered selections of {r} from {n}."),
        trace,
        str(result),
        {"n": n, "r": r, "difficulty": diff},
        verified=(result == math.comb(n, r)),
    )


def gen_counting_principle(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    choices = [rng.randint(2, 6) for _ in range(k)]
    result = math.prod(choices)
    prod_text = "×".join(str(c) for c in choices)
    trace = [
        TraceStep(op="state_principle", text="By the multiplication principle, independent stages multiply their counts."),
        TraceStep(op="list_stages", text=f"The stages have {', '.join(str(c) for c in choices)} options."),
        TraceStep(op="multiply", text=f"Total = {prod_text} = {result}."),
        TraceStep(op="finish", text=f"So there are {result} possibilities.", after=str(result)),
    ]
    return make_sample(
        "combinatorics.counting_principle",
        f"How many outcomes are there for {k} independent stages with {', '.join(str(c) for c in choices)} options?",
        trace,
        str(result),
        {"choices": choices, "difficulty": diff},
        verified=(result == math.prod(choices)),
    )


def gen_binomial_coefficient(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(4, {Difficulty.EASY: 6, Difficulty.MEDIUM: 8, Difficulty.HARD: 11}[diff])
    k = rng.randint(1, n - 1)
    result = math.comb(n, k)
    trace = [
        TraceStep(op="state_rule", text=f"In the expansion of (a + b)^{n}, the coefficient of a^{n-k}b^{k} is C({n}, {k})."),
        TraceStep(op="formula", text=f"C({n}, {k}) = {n}! / ({k}!·{n-k}!)."),
        TraceStep(op="evaluate", text=f"This equals {result}."),
        TraceStep(op="finish", text=f"So the coefficient is {result}.", after=str(result)),
    ]
    return make_sample(
        "combinatorics.binomial_coefficient",
        f"Find the coefficient of a^{n-k}b^{k} in the expansion of (a + b)^{n}.",
        trace,
        str(result),
        {"n": n, "k": k, "difficulty": diff},
        verified=(result == math.comb(n, k)),
    )


def gen_probability_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    red = rng.randint(1, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff])
    other = rng.randint(1, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff])
    total = red + other
    p = Fraction(red, total)
    ans = fmt_fraction(p)
    trace = [
        TraceStep(op="count_total", text=f"There are {red} + {other} = {total} balls in total."),
        TraceStep(op="count_favorable", text=f"The favorable outcomes (red) number {red}."),
        TraceStep(op="ratio", text=f"P(red) = favorable/total = {red}/{total} = {ans}."),
        TraceStep(op="finish", text=f"So the probability is {ans}.", after=ans),
    ]
    return make_sample(
        "combinatorics.probability_basic",
        pick_template(rng, f"A bag has {red} red and {other} other balls. What is the probability of drawing a red ball?", f"In a bag with {red} red and {other} other balls, find P(red).", f"A bag contains {red} red and {other} other balls. Find the probability of picking a red ball at random.", f"There are {red} red and {other} non-red balls. What is the probability of drawing red?"),
        trace,
        ans,
        {"red": red, "other": other, "difficulty": diff},
        verified=(p == Fraction(red, total)),
    )


def gen_conditional_probability(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    b = rng.randint(3, {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff])
    ab = rng.randint(1, b - 1)
    p = Fraction(ab, b)
    ans = fmt_fraction(p)
    trace = [
        TraceStep(op="state_formula", text="Conditional probability: P(A|B) = (number in both A and B) / (number in B)."),
        TraceStep(op="substitute", text=f"Here {ab} outcomes are in both A and B, and {b} outcomes are in B."),
        TraceStep(op="divide", text=f"P(A|B) = {ab}/{b} = {ans}."),
        TraceStep(op="finish", text=f"So P(A|B) = {ans}.", after=ans),
    ]
    return make_sample(
        "combinatorics.conditional_probability",
        f"Of {b} outcomes in event B, {ab} are also in event A. Find P(A|B).",
        trace,
        ans,
        {"b": b, "ab": ab, "difficulty": diff},
        verified=(p == Fraction(ab, b)),
    )


def gen_independent_events(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    da = rng.randint(2, 6)
    db = rng.randint(2, 6)
    na = rng.randint(1, da - 1)
    nb = rng.randint(1, db - 1)
    pa, pb = Fraction(na, da), Fraction(nb, db)
    p = pa * pb
    ans = fmt_fraction(p)
    trace = [
        TraceStep(op="state_rule", text="For independent events, P(A and B) = P(A)·P(B)."),
        TraceStep(op="probabilities", text=f"P(A) = {fmt_fraction(pa)} and P(B) = {fmt_fraction(pb)}."),
        TraceStep(op="multiply", text=f"P(A and B) = {fmt_fraction(pa)}×{fmt_fraction(pb)} = {ans}."),
        TraceStep(op="finish", text=f"So P(A and B) = {ans}.", after=ans),
    ]
    return make_sample(
        "combinatorics.independent_events",
        f"Events A and B are independent with P(A) = {fmt_fraction(pa)} and P(B) = {fmt_fraction(pb)}. Find P(A and B).",
        trace,
        ans,
        {"pa": fmt_fraction(pa), "pb": fmt_fraction(pb), "difficulty": diff},
        verified=(p == pa * pb),
    )


def gen_expectation_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    values = [rng.randint(1, 10) for _ in range(k)]
    weights = [rng.randint(1, 5) for _ in range(k)]
    D = sum(weights)
    contrib = [v * w for v, w in zip(values, weights)]
    total = sum(contrib)
    e = Fraction(total, D)
    ans = fmt_fraction(e)
    prob_text = ", ".join(f"P(X={v}) = {fmt_fraction(Fraction(w, D))}" for v, w in zip(values, weights))
    sum_terms = " + ".join(f"{v}×{w}" for v, w in zip(values, weights))
    trace = [
        TraceStep(op="state_formula", text="The expectation is E[X] = Σ value × probability."),
        TraceStep(op="list_distribution", text=f"The distribution is {prob_text} (all over {D})."),
        TraceStep(op="weighted_sum", text=f"E[X] = ({sum_terms})/{D} = {total}/{D} = {ans}."),
        TraceStep(op="finish", text=f"So E[X] = {ans}.", after=ans),
    ]
    return make_sample(
        "combinatorics.expectation_basic",
        f"A variable X takes values {values} with weights {weights} (probabilities are the weights over their sum). Find E[X].",
        trace,
        ans,
        {"values": values, "weights": weights, "difficulty": diff},
        verified=(e == Fraction(sum(v * w for v, w in zip(values, weights)), sum(weights))),
    )


def gen_mean_median_mode(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    metric = rng.choice(["mean", "median", "mode"])
    n = rng.choice([5, 7]) if diff != Difficulty.EASY else 5
    if metric == "mode":
        base = rng.randint(1, 9)
        data = [base, base, base] + [rng.randint(1, 9) for _ in range(n - 3)]
        cnt = Counter(data)
        top = cnt.most_common()
        while len([v for v, c in cnt.items() if c == top[0][1]]) != 1:
            data = [base, base, base] + [rng.randint(1, 9) for _ in range(n - 3)]
            cnt = Counter(data)
            top = cnt.most_common()
        rng.shuffle(data)
        mode = cnt.most_common(1)[0][0]
        ans = str(mode)
        trace = [
            TraceStep(op="state_def", text="The mode is the value that appears most often."),
            TraceStep(op="count", text=f"Counting occurrences in {data}: {mode} appears {cnt[mode]} times, more than any other."),
            TraceStep(op="finish", text=f"So the mode is {ans}.", after=ans),
        ]
        verified = (mode == cnt.most_common(1)[0][0])
    elif metric == "median":
        data = [rng.randint(1, 20) for _ in range(n)]
        sd = sorted(data)
        mid = sd[n // 2]
        ans = str(mid)
        trace = [
            TraceStep(op="sort", text=f"Sort the data: {sd}."),
            TraceStep(op="pick_middle", text=f"With {n} values, the median is the middle one, position {n // 2 + 1}: {mid}."),
            TraceStep(op="finish", text=f"So the median is {ans}.", after=ans),
        ]
        verified = (mid == sorted(data)[n // 2])
    else:
        data = [rng.randint(1, 20) for _ in range(n)]
        total = sum(data)
        mean = Fraction(total, n)
        ans = fmt_fraction(mean)
        trace = [
            TraceStep(op="sum", text=f"Add the values: {' + '.join(str(x) for x in data)} = {total}."),
            TraceStep(op="divide", text=f"Divide by the count {n}: {total}/{n} = {ans}."),
            TraceStep(op="finish", text=f"So the mean is {ans}.", after=ans),
        ]
        verified = (mean == Fraction(sum(data), n))
    return make_sample(
        "combinatorics.mean_median_mode",
        f"Find the {metric} of the data set {data}.",
        trace,
        ans,
        {"data": data, "metric": metric, "difficulty": diff},
        verified=verified,
    )


def gen_variance_std(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff]
    # choose data with integer mean for clean steps
    mean_int = rng.randint(3, 10)
    data = [mean_int + rng.randint(-3, 3) for _ in range(n)]
    while sum(data) % n != 0:
        data = [mean_int + rng.randint(-3, 3) for _ in range(n)]
    mu = sum(data) // n
    devs = [x - mu for x in data]
    sqdevs = [d * d for d in devs]
    var = Fraction(sum(sqdevs), n)
    ans = fmt_fraction(var)
    trace = [
        TraceStep(op="mean", text=f"Mean: ({' + '.join(str(x) for x in data)})/{n} = {sum(data)}/{n} = {mu}."),
        TraceStep(op="deviations", text=f"Deviations from the mean: {', '.join(str(d) for d in devs)}."),
        TraceStep(op="squared", text=f"Squared deviations: {', '.join(str(s) for s in sqdevs)}, summing to {sum(sqdevs)}."),
        TraceStep(op="divide", text=f"Population variance = {sum(sqdevs)}/{n} = {ans}."),
        TraceStep(op="finish", text=f"So the variance is {ans}.", after=ans),
    ]
    return make_sample(
        "combinatorics.variance_std",
        f"Find the population variance of the data set {data}.",
        trace,
        ans,
        {"data": data, "difficulty": diff},
        verified=(var == Fraction(sum((x - Fraction(sum(data), n)) ** 2 for x in data), n)),
    )


REGISTRY: Dict[str, Any] = {
    "combinatorics.permutation": gen_permutation,
    "combinatorics.combination": gen_combination,
    "combinatorics.counting_principle": gen_counting_principle,
    "combinatorics.binomial_coefficient": gen_binomial_coefficient,
    "combinatorics.probability_basic": gen_probability_basic,
    "combinatorics.conditional_probability": gen_conditional_probability,
    "combinatorics.independent_events": gen_independent_events,
    "combinatorics.expectation_basic": gen_expectation_basic,
    "combinatorics.mean_median_mode": gen_mean_median_mode,
    "combinatorics.variance_std": gen_variance_std,
}
