"""derivative_schema domain (design.md sec 32)."""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import pick_template,  fmt_factor, fmt_interval, fmt_linear, fmt_signed_term, fmt_union


def gen_derivative_computation_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, 8)
    n = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 8}[diff])
    b = rng.randint(1, 12)
    coef = a * n
    answer = f"{coef}x^{n - 1} + {b}"
    trace = [
        TraceStep(op="power_rule", text=f"Differentiate {a}x^{n}: {a}×{n}x^{n - 1} = {coef}x^{n - 1}."),
        TraceStep(op="linear_rule", text=f"Differentiate {b}x to get {b}."),
        TraceStep(op="finish", text=f"So f'(x) = {answer}.", after=answer),
    ]
    return make_sample("derivative_schema.derivative_computation_schema", f"Find the derivative of f(x)={a}x^{n}+{b}x.", trace, answer, {"a": a, "n": n, "b": b, "difficulty": diff}, verified=True)


def gen_tangent_line_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    x0 = rng.randint(1, 8)
    y0 = x0 * x0
    m = 2 * x0
    b = y0 - m * x0
    answer = f"y={fmt_linear(m, b)}"
    trace = [
        TraceStep(op="differentiate", text="For f(x)=x^2, the derivative is f'(x)=2x."),
        TraceStep(op="slope", text=f"At x={x0}, the slope is 2×{x0} = {m}."),
        TraceStep(op="point_slope", text=f"Using point ({x0},{y0}), the tangent line simplifies to {answer}."),
        TraceStep(op="finish", text=f"So the tangent line is {answer}.", after=answer),
    ]
    return make_sample("derivative_schema.tangent_line_schema", f"Find the tangent line to f(x)=x^2 at x={x0}.", trace, answer, {"x0": x0, "difficulty": diff}, verified=(m == 2 * x0 and b == -x0 * x0))


def gen_derivative_sign_monotonicity(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    answer = f"decreasing on {fmt_interval(None, 0)}, increasing on {fmt_interval(0, None)}"
    trace = [
        TraceStep(op="differentiate", text="For f(x)=x^2, f'(x)=2x."),
        TraceStep(op="sign", text="The derivative is negative for x < 0 and positive for x > 0."),
        TraceStep(op="monotonicity", text=f"Therefore f is {answer}."),
        TraceStep(op="finish", text=f"So f is {answer}.", after=answer),
    ]
    return make_sample("derivative_schema.derivative_sign_monotonicity", "Use derivative signs to state where f(x)=x^2 decreases and increases.", trace, answer, {"difficulty": diff}, verified=True)


def gen_critical_points_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    h = rng.randint(-8, 8)
    c = rng.randint(-10, 10)
    b = -2 * h
    answer = f"x={h}"
    trace = [
        TraceStep(op="differentiate", text=f"For f(x)=x^2 + ({b})x + ({c}), f'(x)=2x + ({b})."),
        TraceStep(op="set_zero", text=f"Set 2x + ({b}) = 0, giving x = {h}."),
        TraceStep(op="finish", text=f"So the critical point occurs at {answer}.", after=answer),
    ]
    return make_sample("derivative_schema.critical_points_schema", f"Find the critical x-value of f(x)=x^2+({b})x+({c}).", trace, answer, {"h": h, "b": b, "c": c, "difficulty": diff}, verified=(2 * h + b == 0))


def gen_local_extrema_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    h = rng.randint(-8, 8)
    k = rng.randint(-10, 10)
    # Avoid "(x - (-2))^2 + (-6)" — use clean formatter (des_instruct.md sec 5).
    x_part = fmt_factor(-h)  # (x - h) or (x + |h|)
    k_part = fmt_signed_term(k, '', first=False) if k != 0 else ''
    func_str = f"({x_part})^2{k_part}"
    answer = f"minimum {k} at x={h}"
    trace = [
        TraceStep(op="vertex_form", text=f"f(x)={func_str} is a square{k_part}."),
        TraceStep(op="nonnegative_square", text=f"The square is minimized at x={h}, where its value is 0."),
        TraceStep(op="finish", text=f"So the local extremum is {answer}.", after=answer),
    ]
    return make_sample("derivative_schema.local_extrema_schema", f"Find the local extremum of f(x)={func_str}.", trace, answer, {"h": h, "k": k, "difficulty": diff}, verified=True)


def gen_closed_interval_extreme_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    left = -rng.randint(1, 8)
    right = rng.randint(1, 8)
    max_x = left if abs(left) >= abs(right) else right
    max_val = max_x * max_x
    answer = f"minimum 0 at x=0; maximum {max_val} at x={max_x}"
    trace = [
        TraceStep(op="critical_point", text="For f(x)=x^2, f'(x)=2x, so the critical point is x=0."),
        TraceStep(op="evaluate", text=f"Evaluate f at {left}, 0, and {right}: {left * left}, 0, and {right * right}."),
        TraceStep(op="compare", text=f"The smallest value is 0 and the largest value is {max_val}."),
        TraceStep(op="finish", text=f"So the closed-interval extremes are {answer}.", after=answer),
    ]
    return make_sample("derivative_schema.closed_interval_extreme_schema", f"Find the absolute extrema of f(x)=x^2 on [{left}, {right}].", trace, answer, {"left": left, "right": right, "difficulty": diff}, verified=(left < 0 < right and max_val == max(left * left, right * right)))


REGISTRY: Dict[str, Any] = {
    "derivative_schema.derivative_computation_schema": gen_derivative_computation_schema,
    "derivative_schema.tangent_line_schema": gen_tangent_line_schema,
    "derivative_schema.derivative_sign_monotonicity": gen_derivative_sign_monotonicity,
    "derivative_schema.critical_points_schema": gen_critical_points_schema,
    "derivative_schema.local_extrema_schema": gen_local_extrema_schema,
    "derivative_schema.closed_interval_extreme_schema": gen_closed_interval_extreme_schema,
}
