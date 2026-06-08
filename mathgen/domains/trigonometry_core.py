"""trigonometry domain (design.md sec 6).

Special-angle values, quadrant signs, periodicity reduction, the Pythagorean
identity, identity-based simplification, and basic trig equations on [0, 360).
All exact values come from sympy, so the rendered answers are verified by
construction; each derivation gives the reference angle / quadrant reasoning.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict, List, Optional

import sympy as sp

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample

X = sp.Symbol("x")

SPECIAL = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]

_VALUE_STR = {
    sp.Integer(0): "0",
    sp.Integer(1): "1",
    sp.Integer(-1): "-1",
    sp.Rational(1, 2): "1/2",
    sp.Rational(-1, 2): "-1/2",
    sp.sqrt(2) / 2: "sqrt(2)/2",
    -sp.sqrt(2) / 2: "-sqrt(2)/2",
    sp.sqrt(3) / 2: "sqrt(3)/2",
    -sp.sqrt(3) / 2: "-sqrt(3)/2",
    sp.sqrt(3): "sqrt(3)",
    -sp.sqrt(3): "-sqrt(3)",
    sp.sqrt(3) / 3: "sqrt(3)/3",
    -sp.sqrt(3) / 3: "-sqrt(3)/3",
}


def _angle(deg: int) -> sp.Expr:
    return sp.pi * deg / 180


def exact_trig(func: str, deg: int) -> Optional[str]:
    f = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}[func]
    val = sp.simplify(f(_angle(deg)))
    if val.has(sp.zoo) or val is sp.zoo or val == sp.nan:
        return "undefined"
    for k, s in _VALUE_STR.items():
        if sp.simplify(val - k) == 0:
            return s
    return None  # not a tabulated special value


def _quadrant(deg: int) -> int:
    d = deg % 360
    if 0 < d < 90:
        return 1
    if 90 < d < 180:
        return 2
    if 180 < d < 270:
        return 3
    return 4  # 270 < d < 360


def _reference(deg: int) -> int:
    d = deg % 360
    q = _quadrant(d)
    return {1: d, 2: 180 - d, 3: d - 180, 4: 360 - d}[q]


def gen_special_angle_values(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    pool = [0, 30, 45, 60, 90] if diff == Difficulty.EASY else SPECIAL
    func = rng.choice(["sin", "cos", "tan"])
    deg = rng.choice(pool)
    value = exact_trig(func, deg)
    while value is None or value == "undefined":
        deg = rng.choice(pool)
        value = exact_trig(func, deg)

    # Teach the unit-circle derivation, not just the memorized value.
    unit_circle_explanations = {
        0: "On the unit circle, 0° is at (1, 0).",
        30: "At 30°, use the 30-60-90 triangle: sides 1, √3, 2 → point (√3/2, 1/2).",
        45: "At 45°, use the 45-45-90 triangle: sides 1, 1, √2 → point (√2/2, √2/2).",
        60: "At 60°, use the 30-60-90 triangle: sides √3, 1, 2 → point (1/2, √3/2).",
        90: "On the unit circle, 90° is at (0, 1).",
        120: "At 120° (quadrant II), the reference angle is 60°. Cosine is negative, sine is positive: point (-1/2, √3/2).",
        135: "At 135° (quadrant II), the reference angle is 45°. Both coordinates flipped in sign: point (-√2/2, √2/2).",
        150: "At 150° (quadrant II), the reference angle is 30°. Cosine is negative, sine is positive: point (-√3/2, 1/2).",
        180: "On the unit circle, 180° is at (-1, 0).",
        210: "At 210° (quadrant III), the reference angle is 30°. Both coordinates negative: point (-√3/2, -1/2).",
        225: "At 225° (quadrant III), the reference angle is 45°. Both coordinates negative: point (-√2/2, -√2/2).",
        240: "At 240° (quadrant III), the reference angle is 60°. Both coordinates negative: point (-1/2, -√3/2).",
        270: "On the unit circle, 270° is at (0, -1).",
        300: "At 300° (quadrant IV), the reference angle is 60°. Cosine positive, sine negative: point (1/2, -√3/2).",
        315: "At 315° (quadrant IV), the reference angle is 45°. Cosine positive, sine negative: point (√2/2, -√2/2).",
        330: "At 330° (quadrant IV), the reference angle is 30°. Cosine positive, sine negative: point (√3/2, -1/2).",
        360: "On the unit circle, 360° is at (1, 0), same as 0°.",
    }
    func_explanations = {
        "sin": "sin is the y-coordinate",
        "cos": "cos is the x-coordinate",
        "tan": "tan = sin/cos = y/x",
    }
    geom_hint = unit_circle_explanations.get(deg, f"On the unit circle, {deg}° has a known coordinate.")
    func_hint = func_explanations[func]

    trace = [
        TraceStep(op="unit_circle", text=geom_hint),
        TraceStep(op="coordinate", text=f"{func_hint}, so {func}({deg}°) = {value}."),
        TraceStep(op="finish", text=f"So {func}({deg}°) = {value}.", after=value),
    ]
    return make_sample(
        "trigonometry.special_angle_values",
        f"Find the exact value of {func}({deg}°).",
        trace,
        value,
        {"func": func, "deg": deg, "difficulty": diff},
        verified=(value is not None and value != "undefined"),
    )


def gen_quadrant_sign(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    func = rng.choice(["sin", "cos", "tan"])
    deg = rng.choice([d for d in SPECIAL if d % 90 != 0])
    q = _quadrant(deg)
    signs = {
        1: {"sin": "+", "cos": "+", "tan": "+"},
        2: {"sin": "+", "cos": "-", "tan": "-"},
        3: {"sin": "-", "cos": "-", "tan": "+"},
        4: {"sin": "-", "cos": "+", "tan": "-"},
    }[q]
    sign = "positive" if signs[func] == "+" else "negative"
    rule = {
        1: "all three functions are positive",
        2: "only sine is positive",
        3: "only tangent is positive",
        4: "only cosine is positive",
    }[q]
    trace = [
        TraceStep(op="locate_quadrant", text=f"{deg}° lies in quadrant {q} (between {[0,90,180,270][q-1]}° and {[90,180,270,360][q-1]}°)."),
        TraceStep(op="apply_cast", text=f"In quadrant {q}, {rule}."),
        TraceStep(op="conclude", text=f"So {func}({deg}°) is {sign}."),
        TraceStep(op="finish", text=f"So {func}({deg}°) is {sign}.", after=sign),
    ]
    val = sp.simplify({"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}[func](_angle(deg)))
    return make_sample(
        "trigonometry.quadrant_sign",
        f"Is {func}({deg}°) positive or negative?",
        trace,
        sign,
        {"func": func, "deg": deg, "quadrant": q, "difficulty": diff},
        verified=((sign == "positive") == (val > 0)),
    )


def gen_periodicity(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    func = rng.choice(["sin", "cos"])
    base = rng.choice([0, 30, 45, 60, 90, 120, 135, 150])
    k = rng.randint(1, {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}[diff])
    deg = base + 360 * k
    value = exact_trig(func, base)
    trace = [
        TraceStep(op="state_period", text=f"{func} has period 360°, so {func}(θ) = {func}(θ - 360°k)."),
        TraceStep(op="reduce", text=f"Subtract {360 * k}°: {deg}° - {360 * k}° = {base}°."),
        TraceStep(op="evaluate", text=f"{func}({base}°) = {value}."),
        TraceStep(op="finish", text=f"So {func}({deg}°) = {value}.", after=value),
    ]
    return make_sample(
        "trigonometry.periodicity",
        f"Find the exact value of {func}({deg}°).",
        trace,
        value,
        {"func": func, "deg": deg, "base": base, "difficulty": diff},
        verified=(exact_trig(func, deg) == value),
    )


_PYTHAG = [(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17)]


def gen_pythagorean_identity(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    sn, cn, h = rng.choice(_PYTHAG)
    sin_v = Fraction(sn, h)
    # quadrant decides cosine sign: II -> cos negative, I -> positive
    quad = rng.choice([1, 2])
    cos_v = Fraction(cn, h) if quad == 1 else Fraction(-cn, h)
    sin_str = f"{sn}/{h}"
    s2 = Fraction(sn * sn, h * h)
    c2 = 1 - s2
    answer = f"{cos_v.numerator}/{cos_v.denominator}"
    trace = [
        TraceStep(op="state_identity", text="Use the Pythagorean identity sin^2(x) + cos^2(x) = 1."),
        TraceStep(op="substitute", text=f"With sin(x) = {sin_str}: cos^2(x) = 1 - ({sin_str})^2 = 1 - {s2.numerator}/{s2.denominator} = {c2.numerator}/{c2.denominator}."),
        TraceStep(op="take_root", text=f"So cos(x) = ±{cn}/{h}."),
        TraceStep(op="pick_sign", text=f"Since x is in quadrant {quad}, cosine is {'positive' if quad == 1 else 'negative'}, so cos(x) = {answer}."),
        TraceStep(op="finish", text=f"So cos(x) = {answer}.", after=answer),
    ]
    return make_sample(
        "trigonometry.pythagorean_identity",
        f"Given sin(x) = {sin_str} and x in quadrant {quad}, find cos(x).",
        trace,
        answer,
        {"sin": sin_str, "quadrant": quad, "difficulty": diff},
        verified=(sin_v**2 + cos_v**2 == 1),
    )


_SIMP_TEMPLATES = [
    ("sin(x)^2 + cos(x)^2", sp.sin(X) ** 2 + sp.cos(X) ** 2, "1", sp.Integer(1),
     "By the Pythagorean identity, sin^2(x) + cos^2(x) = 1."),
    ("1 - cos(x)^2", 1 - sp.cos(X) ** 2, "sin(x)^2", sp.sin(X) ** 2,
     "Rearranging sin^2(x) + cos^2(x) = 1 gives 1 - cos^2(x) = sin^2(x)."),
    ("1 - sin(x)^2", 1 - sp.sin(X) ** 2, "cos(x)^2", sp.cos(X) ** 2,
     "Rearranging the identity gives 1 - sin^2(x) = cos^2(x)."),
    ("sin(x)/cos(x)", sp.sin(X) / sp.cos(X), "tan(x)", sp.tan(X),
     "By definition, sin(x)/cos(x) = tan(x)."),
    ("tan(x)·cos(x)", sp.tan(X) * sp.cos(X), "sin(x)", sp.sin(X),
     "Since tan(x) = sin(x)/cos(x), tan(x)·cos(x) = sin(x)."),
]


def gen_trig_simplification(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    expr_str, expr, ans_str, ans, reason = rng.choice(_SIMP_TEMPLATES)
    trace = [
        TraceStep(op="identify_identity", text=reason),
        TraceStep(op="simplify", text=f"So {expr_str} simplifies to {ans_str}."),
        TraceStep(op="finish", text=f"So {expr_str} = {ans_str}.", after=ans_str),
    ]
    return make_sample(
        "trigonometry.trig_simplification",
        f"Simplify {expr_str}.",
        trace,
        ans_str,
        {"expr": expr_str, "difficulty": diff},
        verified=(sp.simplify(expr - ans) == 0),
    )


def _solutions_in_circle(func: str, target: sp.Expr) -> List[int]:
    # Solutions to these special-value equations are themselves special angles.
    f = {"sin": sp.sin, "cos": sp.cos}[func]
    return [d for d in SPECIAL if sp.simplify(f(_angle(d)) - target) == 0]


def gen_trig_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    func = rng.choice(["sin", "cos"])
    targets = [
        ("1/2", sp.Rational(1, 2)),
        ("-1/2", sp.Rational(-1, 2)),
        ("sqrt(2)/2", sp.sqrt(2) / 2),
        ("sqrt(3)/2", sp.sqrt(3) / 2),
        ("0", sp.Integer(0)),
    ]
    tstr, tval = rng.choice(targets)
    sols = _solutions_in_circle(func, tval)
    while not sols:
        tstr, tval = rng.choice(targets)
        sols = _solutions_in_circle(func, tval)
    answer = " or ".join(f"x={d}°" for d in sols)
    ref = min(sols) if sols else 0
    trace = [
        TraceStep(op="reference_angle", text=f"Find where {func}(x) = {tstr} on [0°, 360°). The reference angle is {ref}°."),
        TraceStep(op="list_quadrants", text=f"Including every quadrant where {func} equals {tstr}, the solutions are {', '.join(f'{d}°' for d in sols)}."),
        TraceStep(op="finish", text=f"So {answer}.", after=answer),
    ]
    return make_sample(
        "trigonometry.trig_equation",
        f"Solve {func}(x) = {tstr} for x in [0°, 360°).",
        trace,
        answer,
        {"func": func, "target": tstr, "solutions": sols, "difficulty": diff},
        verified=all(sp.simplify({"sin": sp.sin, "cos": sp.cos}[func](_angle(d)) - tval) == 0 for d in sols) and len(sols) > 0,
    )


REGISTRY: Dict[str, Any] = {
    "trigonometry.special_angle_values": gen_special_angle_values,
    "trigonometry.quadrant_sign": gen_quadrant_sign,
    "trigonometry.periodicity": gen_periodicity,
    "trigonometry.pythagorean_identity": gen_pythagorean_identity,
    "trigonometry.trig_simplification": gen_trig_simplification,
    "trigonometry.trig_equation": gen_trig_equation,
}
