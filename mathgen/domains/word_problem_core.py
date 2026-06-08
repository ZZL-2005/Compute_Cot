"""word_problem_bridge domain (design.md sec 33).

Natural-language problems that bridge to arithmetic/equations: part-whole,
state change, additive and multiplicative comparison, sum-difference,
price-quantity-total, rate-time-distance, work rate, percent, average, age,
mixture, geometry, and a two-variable linear system. Each is built from known
quantities and verified by recomputation.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction

_NAMES = ["Tom", "Mia", "Sam", "Ana", "Leo", "Eva", "Max", "Ivy"]


def gen_part_whole(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    q = rng.choice([2, 3, 4, 5])
    p = rng.randint(1, q - 1)
    whole = q * rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff])
    part = whole * p // q
    trace = [
        TraceStep(op="set_up", text=f"The part is {p}/{q} of the whole {whole}."),
        TraceStep(op="compute", text=f"{p}/{q} × {whole} = {p}×{whole}/{q} = {p * whole}/{q} = {part}."),
        TraceStep(op="finish", text=f"So the part is {part}.", after=str(part)),
    ]
    return make_sample(
        "word_problem.part_whole",
        f"A class has {whole} students, and {p}/{q} of them passed. How many passed?",
        trace,
        str(part),
        {"whole": whole, "p": p, "q": q, "difficulty": diff},
        verified=(part == whole * p // q and whole % q == 0),
    )


def gen_state_change(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 30, Difficulty.MEDIUM: 100, Difficulty.HARD: 500}[diff]
    start = rng.randint(10, hi)
    gain = rng.randint(1, hi)
    spend = rng.randint(1, start + gain)
    end = start + gain - spend
    trace = [
        TraceStep(op="set_up", text=f"Start with {start}, add {gain}, then subtract {spend}."),
        TraceStep(op="compute", text=f"{start} + {gain} - {spend} = {start + gain} - {spend} = {end}."),
        TraceStep(op="finish", text=f"So the final amount is {end}.", after=str(end)),
    ]
    return make_sample(
        "word_problem.state_change",
        f"A shop had {start} items, received {gain} more, then sold {spend}. How many remain?",
        trace,
        str(end),
        {"start": start, "gain": gain, "spend": spend, "difficulty": diff},
        verified=(end == start + gain - spend),
    )


def gen_comparison_more_less(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 30, Difficulty.MEDIUM: 120, Difficulty.HARD: 500}[diff]
    b = rng.randint(5, hi)
    d = rng.randint(1, hi)
    a = b + d
    n1, n2 = rng.sample(_NAMES, 2)
    trace = [
        TraceStep(op="set_up", text=f"{n1} has {d} more than {n2}, who has {b}."),
        TraceStep(op="compute", text=f"{b} + {d} = {a}."),
        TraceStep(op="finish", text=f"So {n1} has {a}.", after=str(a)),
    ]
    return make_sample(
        "word_problem.comparison_more_less",
        f"{n2} has {b} marbles. {n1} has {d} more than {n2}. How many does {n1} have?",
        trace,
        str(a),
        {"b": b, "d": d, "difficulty": diff},
        verified=(a == b + d),
    )


def gen_multiplicative_comparison(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 12, Difficulty.MEDIUM: 40, Difficulty.HARD: 150}[diff]
    b = rng.randint(2, hi)
    k = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 12}[diff])
    a = k * b
    n1, n2 = rng.sample(_NAMES, 2)
    trace = [
        TraceStep(op="set_up", text=f"{n1} has {k} times as many as {n2}, who has {b}."),
        TraceStep(op="compute", text=f"{k} × {b} = {a}."),
        TraceStep(op="finish", text=f"So {n1} has {a}.", after=str(a)),
    ]
    return make_sample(
        "word_problem.multiplicative_comparison",
        f"{n2} has {b} stickers. {n1} has {k} times as many. How many does {n1} have?",
        trace,
        str(a),
        {"b": b, "k": k, "difficulty": diff},
        verified=(a == k * b),
    )


def gen_sum_difference(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 20, Difficulty.MEDIUM: 60, Difficulty.HARD: 200}[diff]
    x = rng.randint(2, hi)
    y = rng.randint(1, x - 1)
    s, d = x + y, x - y
    trace = [
        TraceStep(op="set_up", text=f"Two numbers have sum {s} and difference {d}. The larger is (sum + difference)/2."),
        TraceStep(op="larger", text=f"Larger = ({s} + {d})/2 = {s + d}/2 = {x}."),
        TraceStep(op="smaller", text=f"Smaller = ({s} - {d})/2 = {s - d}/2 = {y}."),
        TraceStep(op="finish", text=f"So the numbers are {x} and {y}.", after=f"{x} and {y}"),
    ]
    return make_sample(
        "word_problem.sum_difference",
        f"Two numbers have a sum of {s} and a difference of {d}. Find the two numbers.",
        trace,
        f"{x} and {y}",
        {"s": s, "d": d, "difficulty": diff},
        verified=(x + y == s and x - y == d),
    )


def gen_price_quantity_total(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    price = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 25, Difficulty.HARD: 80}[diff])
    qty = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 50}[diff])
    total = price * qty
    trace = [
        TraceStep(op="set_up", text=f"Total cost = price × quantity = {price} × {qty}."),
        TraceStep(op="compute", text=f"{price} × {qty} = {total}."),
        TraceStep(op="finish", text=f"So the total cost is {total}.", after=str(total)),
    ]
    return make_sample(
        "word_problem.price_quantity_total",
        f"Each notebook costs ${price}. How much do {qty} notebooks cost?",
        trace,
        str(total),
        {"price": price, "qty": qty, "difficulty": diff},
        verified=(total == price * qty),
    )


def gen_rate_time_distance(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    r = rng.randint(20, {Difficulty.EASY: 60, Difficulty.MEDIUM: 90, Difficulty.HARD: 120}[diff])
    t = rng.randint(2, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff])
    d = r * t
    trace = [
        TraceStep(op="set_up", text=f"Distance = rate × time = {r} × {t}."),
        TraceStep(op="compute", text=f"{r} × {t} = {d}."),
        TraceStep(op="finish", text=f"So the distance is {d} km.", after=str(d)),
    ]
    return make_sample(
        "word_problem.rate_time_distance",
        f"A car travels at {r} km/h for {t} hours. How far does it go?",
        trace,
        str(d),
        {"r": r, "t": t, "difficulty": diff},
        verified=(d == r * t),
    )


def gen_work_rate(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 16}[diff])
    b = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 16}[diff])
    together = Fraction(a * b, a + b)
    ans = fmt_fraction(together)
    trace = [
        TraceStep(op="rates", text=f"In one hour the first does 1/{a} of the job and the second does 1/{b}."),
        TraceStep(op="combined_rate", text=f"Together: 1/{a} + 1/{b} = {a + b}/{a * b} of the job per hour."),
        TraceStep(op="invert", text=f"Time = 1 / ({a + b}/{a * b}) = {a * b}/{a + b} = {ans} hours."),
        TraceStep(op="finish", text=f"So together they take {ans} hours.", after=ans),
    ]
    return make_sample(
        "word_problem.work_rate",
        f"One worker finishes a job in {a} hours, another in {b} hours. How long together?",
        trace,
        ans,
        {"a": a, "b": b, "difficulty": diff},
        verified=(together == Fraction(a * b, a + b)),
    )


def gen_percent_word_problem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    pct = rng.choice([10, 20, 25, 40, 50, 60, 75])
    base = rng.choice([20, 40, 60, 80, 100, 120, 200, 240, 400])
    result = base * pct // 100
    trace = [
        TraceStep(op="set_up", text=f"{pct}% of {base} = ({pct}/100) × {base}."),
        TraceStep(op="compute", text=f"({pct}×{base})/100 = {pct * base}/100 = {result}."),
        TraceStep(op="finish", text=f"So the result is {result}.", after=str(result)),
    ]
    return make_sample(
        "word_problem.percent_word_problem",
        f"A jacket costs ${base}. There is a {pct}% discount. How many dollars is the discount?",
        trace,
        str(result),
        {"pct": pct, "base": base, "difficulty": diff},
        verified=(result == base * pct // 100 and base * pct % 100 == 0),
    )


def gen_average_word_problem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.choice([3, 4, 5])
    avg = rng.randint(40, 95)
    total = avg * n
    knowns = [rng.randint(30, 99) for _ in range(n - 1)]
    missing = total - sum(knowns)
    while missing < 0 or missing > 100:
        knowns = [rng.randint(30, 99) for _ in range(n - 1)]
        missing = total - sum(knowns)
    trace = [
        TraceStep(op="total", text=f"The average of {n} scores is {avg}, so their total is {n}×{avg} = {total}."),
        TraceStep(op="subtract_known", text=f"The known scores sum to {' + '.join(str(k) for k in knowns)} = {sum(knowns)}."),
        TraceStep(op="find_missing", text=f"The missing score is {total} - {sum(knowns)} = {missing}."),
        TraceStep(op="finish", text=f"So the missing score is {missing}.", after=str(missing)),
    ]
    return make_sample(
        "word_problem.average_word_problem",
        f"The average of {n} test scores is {avg}. The known scores are {knowns}. Find the missing score.",
        trace,
        str(missing),
        {"n": n, "avg": avg, "knowns": knowns, "difficulty": diff},
        verified=(missing + sum(knowns) == total),
    )


def gen_age_problem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    b = rng.randint(5, 40)
    d = rng.randint(2, 20)
    t = rng.randint(1, 15)
    future = b + d + t
    n1, n2 = rng.sample(_NAMES, 2)
    trace = [
        TraceStep(op="now", text=f"{n2} is {b} now, and {n1} is {d} years older, so {n1} is {b} + {d} = {b + d} now."),
        TraceStep(op="future", text=f"In {t} years, {n1} will be {b + d} + {t} = {future}."),
        TraceStep(op="finish", text=f"So {n1} will be {future}.", after=str(future)),
    ]
    return make_sample(
        "word_problem.age_problem",
        f"{n2} is {b} years old. {n1} is {d} years older. How old will {n1} be in {t} years?",
        trace,
        str(future),
        {"b": b, "d": d, "t": t, "difficulty": diff},
        verified=(future == b + d + t),
    )


def gen_mixture_problem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, 10)
    b = rng.randint(2, 10)
    pa = rng.randint(2, 12)
    pb = rng.randint(2, 12)
    avg = Fraction(a * pa + b * pb, a + b)
    ans = fmt_fraction(avg)
    trace = [
        TraceStep(op="total_cost", text=f"Total cost = {a}×{pa} + {b}×{pb} = {a * pa} + {b * pb} = {a * pa + b * pb}."),
        TraceStep(op="total_weight", text=f"Total weight = {a} + {b} = {a + b} kg."),
        TraceStep(op="average", text=f"Average price = {a * pa + b * pb}/{a + b} = {ans} per kg."),
        TraceStep(op="finish", text=f"So the mixture costs {ans} per kg.", after=ans),
    ]
    return make_sample(
        "word_problem.mixture_problem",
        f"Mix {a} kg of nuts at ${pa}/kg with {b} kg at ${pb}/kg. Find the average price per kg.",
        trace,
        ans,
        {"a": a, "b": b, "pa": pa, "pb": pb, "difficulty": diff},
        verified=(avg == Fraction(a * pa + b * pb, a + b)),
    )


def gen_geometry_word_problem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    w = rng.randint(3, {Difficulty.EASY: 10, Difficulty.MEDIUM: 25, Difficulty.HARD: 60}[diff])
    extra = rng.randint(1, 15)
    length = w + extra
    perim = 2 * (length + w)
    trace = [
        TraceStep(op="set_up", text=f"The length is {extra} more than the width {w}, so length = {w} + {extra} = {length}."),
        TraceStep(op="perimeter", text=f"Perimeter = 2(length + width) = 2×({length} + {w}) = 2×{length + w} = {perim}."),
        TraceStep(op="finish", text=f"So the perimeter is {perim}.", after=str(perim)),
    ]
    return make_sample(
        "word_problem.geometry_word_problem",
        f"A rectangle has width {w} and length {extra} more than the width. Find its perimeter.",
        trace,
        str(perim),
        {"w": w, "extra": extra, "difficulty": diff},
        verified=(perim == 2 * (length + w)),
    )


def gen_two_variable_linear_word_problem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    adults = rng.randint(2, {Difficulty.EASY: 8, Difficulty.MEDIUM: 20, Difficulty.HARD: 40}[diff])
    children = rng.randint(2, {Difficulty.EASY: 8, Difficulty.MEDIUM: 20, Difficulty.HARD: 40}[diff])
    pa = rng.randint(5, 15)
    pc = rng.randint(2, pa - 1)
    n = adults + children
    total = adults * pa + children * pc
    # solve: a + c = n ; pa*a + pc*c = total -> a = (total - pc*n)/(pa - pc)
    a_solved = (total - pc * n) // (pa - pc)
    c_solved = n - a_solved
    answer = f"{a_solved} adults and {c_solved} children"
    trace = [
        TraceStep(op="define", text=f"Let a = adults, c = children. Then a + c = {n} and {pa}a + {pc}c = {total}."),
        TraceStep(op="substitute", text=f"From the first equation c = {n} - a. Substitute: {pa}a + {pc}({n} - a) = {total}."),
        TraceStep(op="simplify", text=f"{pa}a + {pc * n} - {pc}a = {total}, so {pa - pc}a = {total - pc * n}."),
        TraceStep(op="solve", text=f"a = {total - pc * n}/{pa - pc} = {a_solved}, and c = {n} - {a_solved} = {c_solved}."),
        TraceStep(op="finish", text=f"So there are {answer}.", after=answer),
    ]
    return make_sample(
        "word_problem.two_variable_linear_word_problem",
        f"Tickets cost ${pa} for adults and ${pc} for children. {n} tickets were sold for ${total} total. How many of each?",
        trace,
        answer,
        {"pa": pa, "pc": pc, "n": n, "total": total, "difficulty": diff},
        verified=(a_solved + c_solved == n and pa * a_solved + pc * c_solved == total),
    )


REGISTRY: Dict[str, Any] = {
    "word_problem.part_whole": gen_part_whole,
    "word_problem.state_change": gen_state_change,
    "word_problem.comparison_more_less": gen_comparison_more_less,
    "word_problem.multiplicative_comparison": gen_multiplicative_comparison,
    "word_problem.sum_difference": gen_sum_difference,
    "word_problem.price_quantity_total": gen_price_quantity_total,
    "word_problem.rate_time_distance": gen_rate_time_distance,
    "word_problem.work_rate": gen_work_rate,
    "word_problem.percent_word_problem": gen_percent_word_problem,
    "word_problem.average_word_problem": gen_average_word_problem,
    "word_problem.age_problem": gen_age_problem,
    "word_problem.mixture_problem": gen_mixture_problem,
    "word_problem.geometry_word_problem": gen_geometry_word_problem,
    "word_problem.two_variable_linear_word_problem": gen_two_variable_linear_word_problem,
}
