"""number_theory_core domain (design.md sec 9, the parts not in arithmetic_core).

parity, divisibility rules, basic modular arithmetic and integer factor pairs.
gcd/lcm/prime_factorization already live in arithmetic_core. Every answer is
checked by direct computation.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample


def gen_parity_odd_even(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 99, Difficulty.MEDIUM: 9999, Difficulty.HARD: 999999}[diff]
    n = rng.randint(10, hi)
    last = n % 10
    parity = "even" if n % 2 == 0 else "odd"
    trace = [
        TraceStep(op="state_rule", text="An integer is even when its last digit is one of 0, 2, 4, 6, 8; otherwise it is odd."),
        TraceStep(op="read_last_digit", text=f"The last digit of {n} is {last}."),
        TraceStep(op="classify", text=f"Since {last} is {'even' if last % 2 == 0 else 'odd'}, the number is {parity}."),
        TraceStep(op="finish", text=f"So {n} is {parity}.", after=parity),
    ]
    return make_sample(
        "number_theory.parity_odd_even",
        f"Is {n} even or odd?",
        trace,
        parity,
        {"n": n, "difficulty": diff},
        verified=((parity == "even") == (n % 2 == 0)),
    )


def gen_divisibility_rules(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    d = rng.choice([2, 3, 4, 5, 9])
    hi = {Difficulty.EASY: 999, Difficulty.MEDIUM: 99999, Difficulty.HARD: 9999999}[diff]
    n = rng.randint(100, hi)
    divisible = (n % d == 0)
    yn = "Yes" if divisible else "No"

    if d in (3, 9):
        ds = sum(int(c) for c in str(n))
        rule = f"A number is divisible by {d} exactly when its digit sum is divisible by {d}."
        evidence = f"The digit sum of {n} is {ds}, and {ds} is {'divisible' if ds % d == 0 else 'not divisible'} by {d}."
    elif d == 4:
        last2 = n % 100
        rule = "A number is divisible by 4 exactly when its last two digits form a number divisible by 4."
        evidence = f"The last two digits of {n} form {last2:02d}, and {last2} is {'divisible' if last2 % 4 == 0 else 'not divisible'} by 4."
    elif d == 5:
        last = n % 10
        rule = "A number is divisible by 5 exactly when its last digit is 0 or 5."
        evidence = f"The last digit of {n} is {last}, which is {'0 or 5' if last in (0, 5) else 'neither 0 nor 5'}."
    else:  # d == 2
        last = n % 10
        rule = "A number is divisible by 2 exactly when its last digit is even."
        evidence = f"The last digit of {n} is {last}, which is {'even' if last % 2 == 0 else 'odd'}."

    trace = [
        TraceStep(op="state_rule", text=rule),
        TraceStep(op="apply_rule", text=evidence),
        TraceStep(op="conclude", text=f"Therefore {n} is {'divisible' if divisible else 'not divisible'} by {d}."),
        TraceStep(op="finish", text=f"So the answer is {yn}.", after=yn),
    ]
    return make_sample(
        "number_theory.divisibility_rules",
        f"Is {n} divisible by {d}?",
        trace,
        yn,
        {"n": n, "d": d, "difficulty": diff},
        verified=((yn == "Yes") == divisible),
    )


def gen_modular_arithmetic_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    m = rng.randint(3, {Difficulty.EASY: 7, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    a = rng.randint(m + 1, {Difficulty.EASY: 60, Difficulty.MEDIUM: 300, Difficulty.HARD: 2000}[diff])
    b = rng.randint(m + 1, {Difficulty.EASY: 60, Difficulty.MEDIUM: 300, Difficulty.HARD: 2000}[diff])
    ra, rb = a % m, b % m
    result = (ra * rb) % m
    trace = [
        TraceStep(op="reduce_first", text=f"Reduce each factor mod {m}: {a} = {a // m}×{m} + {ra}, so {a} ≡ {ra} (mod {m})."),
        TraceStep(op="reduce_second", text=f"And {b} = {b // m}×{m} + {rb}, so {b} ≡ {rb} (mod {m})."),
        TraceStep(op="multiply_residues", text=f"Multiply the residues: {ra}×{rb} = {ra * rb}."),
        TraceStep(op="reduce_product", text=f"Reduce mod {m}: {ra * rb} = {(ra * rb) // m}×{m} + {result}, so the result is {result}."),
        TraceStep(op="finish", text=f"So {a}×{b} ≡ {result} (mod {m}).", after=str(result)),
    ]
    return make_sample(
        "number_theory.modular_arithmetic_basic",
        f"Compute ({a} × {b}) mod {m}.",
        trace,
        str(result),
        {"a": a, "b": b, "m": m, "difficulty": diff},
        verified=(result == (a * b) % m),
    )


def gen_integer_factor_pairs(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(8, {Difficulty.EASY: 40, Difficulty.MEDIUM: 100, Difficulty.HARD: 240}[diff])
    pairs: List[Tuple[int, int]] = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            pairs.append((d, n // d))
        d += 1
    pairs_text = ", ".join(f"{x}×{y}" for x, y in pairs)
    trace: List[TraceStep] = [
        TraceStep(op="state_method", text=f"Find every divisor d of {n} with d ≤ sqrt({n}); each gives a pair (d, {n}/d)."),
    ]
    for x, y in pairs:
        trace.append(TraceStep(op="test_divisor", text=f"{n} = {x}×{y}, so {x} and {y} form a factor pair."))
    trace.append(TraceStep(op="finish", text=f"So the factor pairs are {pairs_text}.", after=pairs_text))
    return make_sample(
        "number_theory.integer_factor_pairs",
        f"List all positive factor pairs of {n}.",
        trace,
        pairs_text,
        {"n": n, "pairs": pairs, "difficulty": diff},
        verified=all(x * y == n for x, y in pairs),
    )


REGISTRY: Dict[str, Any] = {
    "number_theory.parity_odd_even": gen_parity_odd_even,
    "number_theory.divisibility_rules": gen_divisibility_rules,
    "number_theory.modular_arithmetic_basic": gen_modular_arithmetic_basic,
    "number_theory.integer_factor_pairs": gen_integer_factor_pairs,
}
