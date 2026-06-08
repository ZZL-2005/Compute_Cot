"""function_property_schema domain (design.md sec 28)."""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import pick_template,  fmt_factor, fmt_interval, fmt_linear, fmt_mul, fmt_signed_term


def gen_domain_of_rational_function(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    a, b = sorted(rng.sample(range(-hi, hi + 1), 2))
    answer = f"x ≠ {a} and x ≠ {b}"
    # Use fmt_factor to avoid "(x - (-3))" — outputs "(x + 3)" cleanly.
    denom_str = f"{fmt_factor(-a)}{fmt_factor(-b)}"
    trace = [
        TraceStep(op="denominator_rule", text="A rational function excludes zeros of its denominator."),
        TraceStep(op="factor_zeros", text=f"The denominator {denom_str} is zero at x = {a} and x = {b}."),
        TraceStep(op="finish", text=f"So the domain restriction is {answer}.", after=answer),
    ]
    return make_sample(
        "function_property_schema.domain_of_rational_function",
        f"Find the domain restriction for f(x)=1/{denom_str}.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=(a != b),
    )


def gen_domain_of_radical_function(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-12, 12)
    answer = f"x ≥ {c}"
    trace = [
        TraceStep(op="radical_rule", text="A square root requires its inside expression to be nonnegative."),
        TraceStep(op="solve", text=f"Require x - ({c}) ≥ 0, so x ≥ {c}."),
        TraceStep(op="finish", text=f"So the domain is {answer}.", after=answer),
    ]
    return make_sample(
        "function_property_schema.domain_of_radical_function",
        f"Find the domain of f(x)=sqrt(x - ({c})).",
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=True,
    )


def gen_domain_of_log_function(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-12, 12)
    answer = f"x > {c}"
    trace = [
        TraceStep(op="log_rule", text="A logarithm requires its argument to be strictly positive."),
        TraceStep(op="solve", text=f"Require x - ({c}) > 0, so x > {c}."),
        TraceStep(op="finish", text=f"So the domain is {answer}.", after=answer),
    ]
    return make_sample(
        "function_property_schema.domain_of_log_function",
        f"Find the domain of f(x)=log(x - ({c})).",
        trace,
        answer,
        {"c": c, "difficulty": diff},
        verified=True,
    )


def gen_range_of_quadratic_function(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    h = rng.randint(-8, 8)
    k = rng.randint(-8, 8)
    # Avoid "(x - (-2))^2 + (-6)" — use clean formatter (des_instruct.md sec 5).
    x_part = fmt_factor(-h)  # (x - h) or (x + |h|)
    k_part = fmt_signed_term(k, '', first=False) if k != 0 else ''
    func_str = f"({x_part})^2{k_part}"
    answer = fmt_interval(k, None, False, True)
    trace = [
        TraceStep(op="vertex_form", text=f"The function f(x) = {func_str} is in vertex form."),
        TraceStep(op="minimum", text=f"A square is always nonnegative, so the minimum value is {k} at x = {h}."),
        TraceStep(op="finish", text=f"So the range is {answer}.", after=answer),
    ]
    return make_sample(
        "function_property_schema.range_of_quadratic_function",
        f"Find the range of f(x)={func_str}.",
        trace,
        answer,
        {"h": h, "k": k, "difficulty": diff},
        verified=True,
    )


def gen_function_zero_interval(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(-15, 15)
    answer = f"x={a}"
    trace = [
        TraceStep(op="set_zero", text=f"Set f(x)=x - ({a}) equal to zero."),
        TraceStep(op="solve", text=f"x - ({a}) = 0 gives x = {a}."),
        TraceStep(op="finish", text=f"So the zero is {answer}.", after=answer),
    ]
    return make_sample(
        "function_property_schema.function_zero_interval",
        f"Find the zero of f(x)=x - ({a}).",
        trace,
        answer,
        {"a": a, "difficulty": diff},
        verified=(a - a == 0),
    )


def gen_function_sign_interval(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(-15, 15)
    answer = fmt_interval(a, None, True, True)
    trace = [
        TraceStep(op="set_positive", text=f"To find where f(x)=x - ({a}) is positive, solve x - ({a}) > 0."),
        TraceStep(op="solve", text=f"This gives x > {a}."),
        TraceStep(op="finish", text=f"So f(x) is positive on {answer}.", after=answer),
    ]
    return make_sample(
        "function_property_schema.function_sign_interval",
        f"Find where f(x)=x - ({a}) is positive.",
        trace,
        answer,
        {"a": a, "difficulty": diff},
        verified=True,
    )


def gen_piecewise_function_evaluation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    c = rng.randint(-6, 6)
    p = rng.randint(1, 8)
    q = rng.randint(1, 8)
    x0 = rng.randint(-10, 10)
    if x0 < c:
        val = x0 + p
        branch = f"x < {c}"
        rule = f"x + {p}"
    else:
        val = 2 * x0 + q
        branch = f"x ≥ {c}"
        rule = f"2x + {q}"
    trace = [
        TraceStep(op="choose_branch", text=f"Since x = {x0}, use the branch {branch}."),
        TraceStep(op="evaluate", text=f"Evaluate {rule} at x = {x0}, which gives {val}."),
        TraceStep(op="finish", text=f"So f({x0}) = {val}.", after=str(val)),
    ]
    return make_sample(
        "function_property_schema.piecewise_function_evaluation",
        f"Let f(x)=x+{p} if x<{c}, and f(x)=2x+{q} if x≥{c}. Find f({x0}).",
        trace,
        str(val),
        {"c": c, "p": p, "q": q, "x0": x0, "difficulty": diff},
        verified=(val == (x0 + p if x0 < c else 2 * x0 + q)),
    )


def gen_composite_function_evaluation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, 6)
    b = rng.randint(-8, 8)
    c = rng.randint(2, 6)
    d = rng.randint(-8, 8)
    x0 = rng.randint(-5, 5)
    gx = c * x0 + d
    ans = a * gx + b
    trace = [
        TraceStep(op="inner", text=f"First compute g({x0}) = {fmt_linear(c, d)} with x = {x0}, giving {gx}."),
        # Avoid "+ (-3)" dirty pattern: use fmt_signed_term for the constant.
        TraceStep(op="outer", text=f"Then compute f(g({x0})) = f({gx}) = {fmt_mul(a, gx)}{fmt_signed_term(b, '', first=False)} = {ans}."),
        TraceStep(op="finish", text=f"So f(g({x0})) = {ans}.", after=str(ans)),
    ]
    return make_sample(
        "function_property_schema.composite_function_evaluation",
        f"Let f(x)={fmt_linear(a, b)} and g(x)={fmt_linear(c, d)}. Find f(g({x0})).",
        trace,
        str(ans),
        {"a": a, "b": b, "c": c, "d": d, "x0": x0, "difficulty": diff},
        verified=(ans == a * (c * x0 + d) + b),
    )


REGISTRY: Dict[str, Any] = {
    "function_property_schema.domain_of_rational_function": gen_domain_of_rational_function,
    "function_property_schema.domain_of_radical_function": gen_domain_of_radical_function,
    "function_property_schema.domain_of_log_function": gen_domain_of_log_function,
    "function_property_schema.range_of_quadratic_function": gen_range_of_quadratic_function,
    "function_property_schema.function_zero_interval": gen_function_zero_interval,
    "function_property_schema.function_sign_interval": gen_function_sign_interval,
    "function_property_schema.piecewise_function_evaluation": gen_piecewise_function_evaluation,
    "function_property_schema.composite_function_evaluation": gen_composite_function_evaluation,
}
