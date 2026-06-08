"""plane_geometry_formula domain (design.md sec 21).

Triangle area, rectangle area/perimeter, circle area/circumference (in terms of
pi), the Pythagorean theorem, similar-triangle proportions, triangle angle sum,
polygon angle sum, and sector area/arc length. Exact answers, verified directly.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_fraction, fmt_radical, fmt_value, sqrt_simplify


def _pi_term(coef) -> str:
    if coef == 1:
        return "π"
    return f"{fmt_value(coef)}π"


def gen_triangle_area(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 10, Difficulty.MEDIUM: 20, Difficulty.HARD: 40}[diff]
    b = rng.randint(2, hi)
    h = rng.randint(2, hi)
    area = Fraction(b * h, 2)
    ans = fmt_fraction(area)
    trace = [
        TraceStep(op="state_formula", text="The area of a triangle is (1/2)·base·height."),
        TraceStep(op="substitute", text=f"Area = (1/2)×{b}×{h} = {b * h}/2."),
        TraceStep(op="simplify", text=f"{b * h}/2 = {ans}."),
        TraceStep(op="finish", text=f"So the area is {ans}.", after=ans),
    ]
    return make_sample(
        "plane_geometry.triangle_area",
        f"Find the area of a triangle with base {b} and height {h}.",
        trace,
        ans,
        {"base": b, "height": h, "difficulty": diff},
        verified=(area == Fraction(b * h, 2)),
    )


def gen_rectangle_area_perimeter(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 12, Difficulty.MEDIUM: 25, Difficulty.HARD: 50}[diff]
    l = rng.randint(2, hi)
    w = rng.randint(2, hi)
    area = l * w
    perim = 2 * (l + w)
    ans = f"area = {area}, perimeter = {perim}"
    trace = [
        TraceStep(op="area", text=f"Area = length×width = {l}×{w} = {area}."),
        TraceStep(op="perimeter", text=f"Perimeter = 2(length + width) = 2×({l} + {w}) = 2×{l + w} = {perim}."),
        TraceStep(op="finish", text=f"So {ans}.", after=ans),
    ]
    return make_sample(
        "plane_geometry.rectangle_area_perimeter",
        f"Find the area and perimeter of a rectangle with length {l} and width {w}.",
        trace,
        ans,
        {"l": l, "w": w, "difficulty": diff},
        verified=(area == l * w and perim == 2 * (l + w)),
    )


def gen_circle_area_circumference(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    r = rng.randint(2, {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff])
    area = _pi_term(r * r)
    circ = _pi_term(2 * r)
    ans = f"area = {area}, circumference = {circ}"
    trace = [
        TraceStep(op="area", text=f"Area = πr^2 = π×{r}^2 = {area}."),
        TraceStep(op="circumference", text=f"Circumference = 2πr = 2π×{r} = {circ}."),
        TraceStep(op="finish", text=f"So {ans}.", after=ans),
    ]
    return make_sample(
        "plane_geometry.circle_area_circumference",
        f"Find the area and circumference of a circle with radius {r} (in terms of π).",
        trace,
        ans,
        {"r": r, "difficulty": diff},
        verified=(r * r > 0),
    )


def gen_pythagorean_theorem(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 16}[diff]
    a = rng.randint(2, hi)
    b = rng.randint(2, hi)
    sq = a * a + b * b
    out, ins = sqrt_simplify(sq)
    ans = fmt_radical(out, ins)
    trace = [
        TraceStep(op="state_theorem", text="By the Pythagorean theorem, hypotenuse = sqrt(a^2 + b^2)."),
        TraceStep(op="square_legs", text=f"a^2 + b^2 = {a}^2 + {b}^2 = {a * a} + {b * b} = {sq}."),
        TraceStep(op="simplify_radical", text=f"hypotenuse = sqrt({sq}) = {ans}."),
        TraceStep(op="finish", text=f"So the hypotenuse is {ans}.", after=ans),
    ]
    return make_sample(
        "plane_geometry.pythagorean_theorem",
        f"A right triangle has legs {a} and {b}. Find the hypotenuse.",
        trace,
        ans,
        {"a": a, "b": b, "difficulty": diff},
        verified=(out * out * ins == sq),
    )


def gen_similar_triangles(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 16}[diff]
    a = rng.randint(2, hi)
    b = rng.randint(2, hi)
    k = rng.randint(2, 5)
    a2 = k * a
    x = Fraction(a2 * b, a)
    ans = fmt_fraction(x)
    trace = [
        TraceStep(op="state_ratio", text="Similar triangles have proportional corresponding sides: a/a' = b/x."),
        TraceStep(op="set_up", text=f"So {a}/{a2} = {b}/x."),
        TraceStep(op="cross_multiply", text=f"Cross-multiply: {a}·x = {a2}×{b} = {a2 * b}."),
        TraceStep(op="solve", text=f"x = {a2 * b}/{a} = {ans}."),
        TraceStep(op="finish", text=f"So x = {ans}.", after=f"x={ans}"),
    ]
    return make_sample(
        "plane_geometry.similar_triangles",
        f"Two triangles are similar. Sides {a} and {b} correspond to {a2} and x. Find x.",
        trace,
        f"x={ans}",
        {"a": a, "b": b, "a2": a2, "difficulty": diff},
        verified=(Fraction(a, a2) == Fraction(b, x)),
    )


def gen_angle_sum_triangle(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(20, 120)
    b = rng.randint(20, 150 - a) if 150 - a > 20 else 30
    while a + b >= 175:
        b = rng.randint(20, 100)
    c = 180 - a - b
    ans = f"{c}°"
    trace = [
        TraceStep(op="state_rule", text="The interior angles of a triangle sum to 180°."),
        TraceStep(op="subtract", text=f"Third angle = 180° - {a}° - {b}° = {c}°."),
        TraceStep(op="finish", text=f"So the third angle is {ans}.", after=ans),
    ]
    return make_sample(
        "plane_geometry.angle_sum_triangle",
        f"Two angles of a triangle are {a}° and {b}°. Find the third angle.",
        trace,
        ans,
        {"a": a, "b": b, "difficulty": diff},
        verified=(a + b + c == 180 and c > 0),
    )


def gen_polygon_angle_sum(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(3, {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff])
    s = (n - 2) * 180
    ans = f"{s}°"
    trace = [
        TraceStep(op="state_formula", text="The interior angles of an n-gon sum to (n - 2)×180°."),
        TraceStep(op="substitute", text=f"Sum = ({n} - 2)×180° = {n - 2}×180° = {s}°."),
        TraceStep(op="finish", text=f"So the interior angle sum is {ans}.", after=ans),
    ]
    return make_sample(
        "plane_geometry.polygon_angle_sum",
        f"Find the sum of the interior angles of a {n}-sided polygon.",
        trace,
        ans,
        {"n": n, "difficulty": diff},
        verified=(s == (n - 2) * 180),
    )


def gen_sector_area_arc_length(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    r = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 18}[diff])
    theta = rng.choice([30, 45, 60, 90, 120, 135, 150, 180, 270])
    arc_coef = Fraction(theta * r, 180)
    area_coef = Fraction(theta * r * r, 360)
    arc = _pi_term(arc_coef)
    area = _pi_term(area_coef)
    ans = f"arc length = {arc}, area = {area}"
    trace = [
        TraceStep(op="arc_formula", text=f"Arc length = (θ/360)·2πr = ({theta}/360)·2π×{r} = {arc}."),
        TraceStep(op="area_formula", text=f"Sector area = (θ/360)·πr^2 = ({theta}/360)·π×{r}^2 = {area}."),
        TraceStep(op="finish", text=f"So {ans}.", after=ans),
    ]
    return make_sample(
        "plane_geometry.sector_area_arc_length",
        f"A sector has radius {r} and central angle {theta}°. Find its arc length and area (in terms of π).",
        trace,
        ans,
        {"r": r, "theta": theta, "difficulty": diff},
        verified=(arc_coef == Fraction(theta * r, 180) and area_coef == Fraction(theta * r * r, 360)),
    )


REGISTRY: Dict[str, Any] = {
    "plane_geometry.triangle_area": gen_triangle_area,
    "plane_geometry.rectangle_area_perimeter": gen_rectangle_area_perimeter,
    "plane_geometry.circle_area_circumference": gen_circle_area_circumference,
    "plane_geometry.pythagorean_theorem": gen_pythagorean_theorem,
    "plane_geometry.similar_triangles": gen_similar_triangles,
    "plane_geometry.angle_sum_triangle": gen_angle_sum_triangle,
    "plane_geometry.polygon_angle_sum": gen_polygon_angle_sum,
    "plane_geometry.sector_area_arc_length": gen_sector_area_arc_length,
}
