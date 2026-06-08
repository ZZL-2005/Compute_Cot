"""trigonometric_schema domain (design.md sec 29)."""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample

_REF = {120: 60, 135: 45, 150: 30, 210: 30, 225: 45, 240: 60, 300: 60, 315: 45, 330: 30}
_SIGNS = {
    1: {"sin": "positive", "cos": "positive", "tan": "positive"},
    2: {"sin": "positive", "cos": "negative", "tan": "negative"},
    3: {"sin": "negative", "cos": "negative", "tan": "positive"},
    4: {"sin": "negative", "cos": "positive", "tan": "negative"},
}
_SIN_BASIC = {"0": "x=0° or x=180°", "1": "x=90°", "-1": "x=270°"}


def gen_reference_angle_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    angle = rng.choice(list(_REF))
    ref = _REF[angle]
    q = 2 if angle < 180 else 3 if angle < 270 else 4
    trace = [
        TraceStep(op="locate_quadrant", text=f"The angle {angle}° lies in quadrant {q}."),
        TraceStep(op="compute_reference", text=f"The acute angle to the x-axis is {ref}°."),
        TraceStep(op="finish", text=f"So the reference angle is {ref}°.", after=f"{ref}°"),
    ]
    return make_sample(
        "trigonometric_schema.reference_angle_schema",
        f"Find the reference angle for {angle}°.",
        trace,
        f"{ref}°",
        {"angle": angle, "difficulty": diff},
        verified=(_REF[angle] == ref),
    )


def gen_quadrant_sign_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    q = rng.randint(1, 4)
    fn = rng.choice(["sin", "cos", "tan"])
    ans = _SIGNS[q][fn]
    trace = [
        TraceStep(op="quadrant_rule", text=f"In quadrant {q}, the sign pattern gives {fn} as {ans}."),
        TraceStep(op="finish", text=f"So {fn} is {ans} in quadrant {q}.", after=ans),
    ]
    return make_sample(
        "trigonometric_schema.quadrant_sign_schema",
        f"What is the sign of {fn}(x) in quadrant {q}?",
        trace,
        ans,
        {"quadrant": q, "function": fn, "difficulty": diff},
        verified=(_SIGNS[q][fn] == ans),
    )


def gen_trig_identity_simplification(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    trace = [
        TraceStep(op="identity", text="Use the Pythagorean identity sin^2(x) + cos^2(x) = 1."),
        TraceStep(op="finish", text="So sin^2(x) + cos^2(x) simplifies to 1.", after="1"),
    ]
    return make_sample(
        "trigonometric_schema.trig_identity_simplification",
        "Simplify sin^2(x) + cos^2(x).",
        trace,
        "1",
        {"difficulty": diff},
        verified=True,
    )


def gen_trig_equation_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    value = rng.choice(list(_SIN_BASIC))
    answer = _SIN_BASIC[value]
    trace = [
        TraceStep(op="unit_circle", text=f"On 0° ≤ x < 360°, sin(x) = {value} at the listed unit-circle angles."),
        TraceStep(op="select", text=f"Those angles give {answer}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "trigonometric_schema.trig_equation_basic",
        f"Solve sin(x) = {value} for 0° ≤ x < 360°.",
        trace,
        answer,
        {"value": value, "difficulty": diff},
        verified=(answer == _SIN_BASIC[value]),
    )


def gen_trig_equation_general_solution(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    answer = "x=180°k"
    trace = [
        TraceStep(op="base_solutions", text="sin(x) = 0 at x = 0°, 180°, 360°, and so on."),
        TraceStep(op="periodic_form", text="These are exactly the integer multiples of 180°."),
        TraceStep(op="finish", text=f"So the general solution is {answer}.", after=answer),
    ]
    return make_sample(
        "trigonometric_schema.trig_equation_general_solution",
        "Give the general solution of sin(x)=0 in degrees.",
        trace,
        answer,
        {"difficulty": diff},
        verified=True,
    )


def gen_trig_periodicity_solution_set(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.choice([30, 45, 60, 90])
    period = rng.choice([180, 360])
    answer = f"x={base}° + {period}°k"
    trace = [
        TraceStep(op="state_period", text=f"If one solution is {base}° and the period is {period}°, then adding {period}° preserves the value."),
        TraceStep(op="integer_shifts", text=f"All repeated solutions have the form {base}° + {period}°k for integer k."),
        TraceStep(op="finish", text=f"So the solution set is {answer}.", after=answer),
    ]
    return make_sample(
        "trigonometric_schema.trig_periodicity_solution_set",
        f"A trigonometric equation has solution {base}° and period {period}°. Write the periodic solution set.",
        trace,
        answer,
        {"base": base, "period": period, "difficulty": diff},
        verified=True,
    )


REGISTRY: Dict[str, Any] = {
    "trigonometric_schema.reference_angle_schema": gen_reference_angle_schema,
    "trigonometric_schema.quadrant_sign_schema": gen_quadrant_sign_schema,
    "trigonometric_schema.trig_identity_simplification": gen_trig_identity_simplification,
    "trigonometric_schema.trig_equation_basic": gen_trig_equation_basic,
    "trigonometric_schema.trig_equation_general_solution": gen_trig_equation_general_solution,
    "trigonometric_schema.trig_periodicity_solution_set": gen_trig_periodicity_solution_set,
}
