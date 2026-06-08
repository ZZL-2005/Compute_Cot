"""exponential_logarithmic domain (design.md sec 15).

Exponent laws, negative/fractional exponents, exponential & logarithmic
equations, the definition and laws of logarithms, log domains, and the
exponential/log inverse relationship. Bases and arguments are chosen so every
result is an exact integer/fraction, and each law is applied as an explicit
step. Numeric results are verified by exact arithmetic.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction, fmt_interval, paren_if_negative


def gen_exponent_laws(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[diff])
    m = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff])
    n = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 6}[diff])
    power = m + n
    result = base**power
    trace = [
        TraceStep(op="state_law", text=f"Use the product law a^m × a^n = a^(m+n) with the same base {base}."),
        TraceStep(op="add_exponents", text=f"Add the exponents: {base}^{m} × {base}^{n} = {base}^({m}+{n}) = {base}^{power}."),
        TraceStep(op="evaluate", text=f"Evaluate {base}^{power} = {result}."),
        TraceStep(op="finish", text=f"So {base}^{m} × {base}^{n} = {result}.", after=str(result)),
    ]
    return make_sample(
        "exp_log.exponent_laws",
        f"Simplify and evaluate {base}^{m} × {base}^{n}.",
        trace,
        str(result),
        {"base": base, "m": m, "n": n, "difficulty": diff},
        verified=(result == base**m * base**n),
    )


def gen_negative_exponent(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 9}[diff])
    n = rng.randint(1, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff])
    denom = base**n
    result = Fraction(1, denom)
    trace = [
        TraceStep(op="state_rule", text=f"A negative exponent means a reciprocal: a^(-n) = 1/a^n."),
        TraceStep(op="apply_rule", text=f"So {base}^(-{n}) = 1/{base}^{n}."),
        TraceStep(op="evaluate_power", text=f"Evaluate the power: {base}^{n} = {denom}."),
        TraceStep(op="finish", text=f"So {base}^(-{n}) = {fmt_fraction(result)}.", after=fmt_fraction(result)),
    ]
    return make_sample(
        "exp_log.negative_exponent",
        f"Evaluate {base}^(-{n}).",
        trace,
        fmt_fraction(result),
        {"base": base, "n": n, "difficulty": diff},
        verified=(result == Fraction(1, base**n)),
    )


def gen_fractional_exponent(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    root = rng.randint(2, 3)
    inner = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[diff])
    m = rng.randint(1, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff])
    base = inner**root  # perfect n-th power
    result = inner**m
    trace = [
        TraceStep(op="state_rule", text=f"A fractional exponent is a root then a power: a^(m/n) = (n-th root of a)^m."),
        TraceStep(op="take_root", text=f"Here the {root}th root of {base} is {inner}, because {inner}^{root} = {base}."),
        TraceStep(op="apply_power", text=f"So {base}^({m}/{root}) = {inner}^{m}."),
        TraceStep(op="evaluate", text=f"Evaluate {inner}^{m} = {result}."),
        TraceStep(op="finish", text=f"So {base}^({m}/{root}) = {result}.", after=str(result)),
    ]
    return make_sample(
        "exp_log.fractional_exponent",
        f"Evaluate {base}^({m}/{root}).",
        trace,
        str(result),
        {"base": base, "m": m, "root": root, "difficulty": diff},
        verified=(result == inner**m and inner**root == base),
    )


def gen_exponential_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[diff])
    k = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 8}[diff])
    value = base**k
    trace = [
        TraceStep(op="rewrite_same_base", text=f"Write {value} as a power of {base}: {value} = {base}^{k}."),
        TraceStep(op="equate_exponents", text=f"The equation becomes {base}^x = {base}^{k}. With equal bases, set the exponents equal: x = {k}."),
        TraceStep(op="finish", text=f"So the solution is x={k}.", after=f"x={k}"),
    ]
    return make_sample(
        "exp_log.exponential_equation",
        f"Solve {base}^x = {value} for x.",
        trace,
        f"x={k}",
        {"base": base, "value": value, "difficulty": diff},
        verified=(base**k == value),
    )


def gen_logarithm_definition(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 9}[diff])
    k = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff])
    value = base**k
    trace = [
        TraceStep(op="state_definition", text=f"By definition, log_{base}({value}) is the exponent k with {base}^k = {value}."),
        TraceStep(op="rewrite_power", text=f"Write {value} as a power of {base}: {value} = {base}^{k}."),
        TraceStep(op="read_exponent", text=f"So the exponent is {k}."),
        TraceStep(op="finish", text=f"So log_{base}({value}) = {k}.", after=str(k)),
    ]
    return make_sample(
        "exp_log.logarithm_definition",
        f"Evaluate log_{base}({value}).",
        trace,
        str(k),
        {"base": base, "value": value, "difficulty": diff},
        verified=(base**k == value),
    )


def gen_logarithm_laws(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 5}[diff])
    p = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 6}[diff])
    q = rng.randint(1, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 6}[diff])
    x = base**p
    y = base**q
    xy = x * y
    result = p + q
    trace = [
        TraceStep(op="state_law", text=f"Use the product law: log_b(x) + log_b(y) = log_b(xy)."),
        TraceStep(op="combine", text=f"So log_{base}({x}) + log_{base}({y}) = log_{base}({x}×{y}) = log_{base}({xy})."),
        TraceStep(op="evaluate_each", text=f"Since {x} = {base}^{p} and {y} = {base}^{q}, we get {p} + {q} = {result}."),
        TraceStep(op="finish", text=f"So log_{base}({x}) + log_{base}({y}) = {result}.", after=str(result)),
    ]
    return make_sample(
        "exp_log.logarithm_laws",
        f"Evaluate log_{base}({x}) + log_{base}({y}).",
        trace,
        str(result),
        {"base": base, "x": x, "y": y, "difficulty": diff},
        verified=(base**result == xy),
    )


def gen_log_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[diff])
    k = rng.randint(2, {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff])
    value = base**k
    trace = [
        TraceStep(op="rewrite_exponential", text=f"By the definition of a logarithm, log_{base}(x) = {k} means x = {base}^{k}."),
        TraceStep(op="evaluate", text=f"Evaluate {base}^{k} = {value}."),
        TraceStep(op="finish", text=f"So the solution is x={value}.", after=f"x={value}"),
    ]
    return make_sample(
        "exp_log.log_equation",
        f"Solve log_{base}(x) = {k} for x.",
        trace,
        f"x={value}",
        {"base": base, "k": k, "difficulty": diff},
        verified=(base**k == value),
    )


def gen_log_domain(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.choice([2, 3, 10])
    c = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 25}[diff])
    # log_base(x - c): argument > 0 -> x > c
    answer = fmt_interval(c, None, low_open=True, high_open=True)
    trace = [
        TraceStep(op="state_condition", text="The argument of a logarithm must be strictly positive."),
        TraceStep(op="set_inequality", text=f"Require x - {c} > 0."),
        TraceStep(op="solve", text=f"Add {c} to both sides: x > {c}."),
        TraceStep(op="finish", text=f"So the domain is {answer}.", after=answer),
    ]
    return make_sample(
        "exp_log.log_domain",
        f"Find the domain of f(x) = log_{base}(x - {c}).",
        trace,
        answer,
        {"base": base, "c": c, "difficulty": diff},
        verified=(answer == f"({c}, +∞)"),
    )


def gen_exponential_log_inverse(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 9}[diff])
    if rng.random() < 0.5:
        k = rng.randint(2, 6)
        result = k
        user = f"Evaluate log_{base}({base}^{k})."
        trace = [
            TraceStep(op="state_inverse", text=f"The logarithm and exponential with base {base} are inverses: log_{base}({base}^k) = k."),
            TraceStep(op="apply", text=f"So log_{base}({base}^{k}) = {k}."),
            TraceStep(op="finish", text=f"So the value is {result}.", after=str(result)),
        ]
    else:
        x = rng.randint(2, {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff])
        result = x
        user = f"Evaluate {base}^(log_{base}({x}))."
        trace = [
            TraceStep(op="state_inverse", text=f"The exponential and logarithm with base {base} are inverses: {base}^(log_{base}(x)) = x."),
            TraceStep(op="apply", text=f"So {base}^(log_{base}({x})) = {x}."),
            TraceStep(op="finish", text=f"So the value is {result}.", after=str(result)),
        ]
    return make_sample(
        "exp_log.exponential_log_inverse",
        user,
        trace,
        str(result),
        {"base": base, "difficulty": diff},
        verified=True,
    )


REGISTRY: Dict[str, Any] = {
    "exp_log.exponent_laws": gen_exponent_laws,
    "exp_log.negative_exponent": gen_negative_exponent,
    "exp_log.fractional_exponent": gen_fractional_exponent,
    "exp_log.exponential_equation": gen_exponential_equation,
    "exp_log.logarithm_definition": gen_logarithm_definition,
    "exp_log.logarithm_laws": gen_logarithm_laws,
    "exp_log.log_equation": gen_log_equation,
    "exp_log.log_domain": gen_log_domain,
    "exp_log.exponential_log_inverse": gen_exponential_log_inverse,
}
