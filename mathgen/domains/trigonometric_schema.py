"""trigonometric_schema domain (design.md sec 29)."""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import pick_template

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
        pick_template(rng, f"Find the reference angle for {angle}°.", f"Determine the reference angle of {angle}°.", f"What is the reference angle for {angle}°?", f"Calculate the acute reference angle for {angle}°."),
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
    cast = {1: "All (sin, cos, tan are all positive)",
            2: "Sin only (only sine is positive)",
            3: "Tan only (only tangent is positive)",
            4: "Cos only (only cosine is positive)"}
    trace = [
        TraceStep(op="recall_cast", text=f"Recall the CAST rule: in quadrant {q}, {cast[q]}."),
        TraceStep(op="apply", text=f"Therefore {fn} is {ans} in quadrant {q}."),
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
    # Vary the identity instead of always using sin²+cos²=1.
    identities = [
        ("sin^2(x) + cos^2(x)", "1", "Use the Pythagorean identity sin^2(x) + cos^2(x) = 1."),
        ("1 - sin^2(x)", "cos^2(x)", "Use the Pythagorean identity: sin^2(x) + cos^2(x) = 1, so 1 - sin^2(x) = cos^2(x)."),
        ("1 - cos^2(x)", "sin^2(x)", "Use the Pythagorean identity: sin^2(x) + cos^2(x) = 1, so 1 - cos^2(x) = sin^2(x)."),
        ("sin(x)/cos(x)", "tan(x)", "By definition, tan(x) = sin(x)/cos(x)."),
        ("tan(x) * cos(x)", "sin(x)", "Since tan(x) = sin(x)/cos(x), multiplying by cos(x) gives sin(x)."),
    ]
    expr, answer, explanation = rng.choice(identities)
    trace = [
        TraceStep(op="identity", text=explanation),
        TraceStep(op="finish", text=f"So {expr} simplifies to {answer}.", after=answer),
    ]
    return make_sample(
        "trigonometric_schema.trig_identity_simplification",
        f"Simplify {expr}.",
        trace,
        answer,
        {"difficulty": diff},
        verified=True,
    )


def gen_trig_equation_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    # Include cos and tan variants for diversity.
    equations = [
        ("sin(x)", "0", "0°, 180°", "sin(x)=0 at x=0° and x=180° on [0°,360°)"),
        ("sin(x)", "1", "90°", "sin(x)=1 at x=90° on [0°,360°)"),
        ("sin(x)", "-1", "270°", "sin(x)=-1 at x=270° on [0°,360°)"),
        ("cos(x)", "0", "90°, 270°", "cos(x)=0 at x=90° and x=270° on [0°,360°)"),
        ("cos(x)", "1", "0°", "cos(x)=1 at x=0° on [0°,360°)"),
        ("cos(x)", "-1", "180°", "cos(x)=-1 at x=180° on [0°,360°)"),
    ]
    func_expr, val, ans, hint = rng.choice(equations)
    trace = [
        TraceStep(op="unit_circle", text=f"On the unit circle, {hint}."),
        TraceStep(op="select", text=f"Those angles give {ans}."),
        TraceStep(op="finish", text=f"So the solution is {ans}.", after=ans),
    ]
    return make_sample(
        "trigonometric_schema.trig_equation_basic",
        f"Solve {func_expr} = {val} for 0° ≤ x < 360°.",
        trace,
        ans,
        {"func": func_expr, "value": val, "difficulty": diff},
        verified=True,
    )


def gen_trig_equation_general_solution(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    # Vary the equation instead of always sin(x)=0.
    cases = [
        ("sin(x)=0", "0°, 180°, 360°, ...", "180°k", "integer multiples of 180°"),
        ("cos(x)=0", "90°, 270°, 450°, ...", "90° + 180°k", "90° plus integer multiples of 180°"),
        ("sin(x)=1", "90°, 450°, 810°, ...", "90° + 360°k", "90° plus integer multiples of 360°"),
    ]
    eq, bases, answer, explanation = rng.choice(cases)
    trace = [
        TraceStep(op="base_solutions", text=f"{eq} at x = {bases}."),
        TraceStep(op="periodic_form", text=f"These are exactly the {explanation}."),
        TraceStep(op="finish", text=f"So the general solution is x={answer}.", after=f"x={answer}"),
    ]
    return make_sample(
        "trigonometric_schema.trig_equation_general_solution",
        f"Give the general solution of {eq} in degrees.",
        trace,
        f"x={answer}",
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
        pick_template(rng, f"A trigonometric equation has solution {base}° and period {period}°. Write the periodic solution set.", f"Given a base solution {base}° and period {period}°, express all solutions.", f"Write the general solution given one solution {base}° and period {period}°."),
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
