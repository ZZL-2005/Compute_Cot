"""analytic_geometry_schema domain (design.md sec 31)."""

from __future__ import annotations

import random
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_linear


def gen_line_from_two_points(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    m = rng.randint(1, {Difficulty.EASY: 4, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff])
    b = rng.randint(-10, 10)
    x1, x2 = sorted(rng.sample(range(-5, 6), 2))
    y1, y2 = m * x1 + b, m * x2 + b
    answer = f"y={fmt_linear(m, b)}"
    trace = [
        TraceStep(op="slope", text=f"The slope is ({y2} - ({y1}))/({x2} - ({x1})) = {m}."),
        TraceStep(op="intercept", text=f"Using y = mx + b with ({x1},{y1}) gives b = {b}."),
        TraceStep(op="finish", text=f"So the line is {answer}.", after=answer),
    ]
    return make_sample("analytic_geometry_schema.line_from_two_points", f"Find the line through ({x1},{y1}) and ({x2},{y2}).", trace, answer, {"m": m, "b": b, "difficulty": diff}, verified=(y1 == m * x1 + b and y2 == m * x2 + b))


def gen_line_intersection(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    x0 = rng.randint(-6, 6)
    y0 = rng.randint(-10, 10)
    m1, m2 = rng.sample(range(1, 8), 2)
    b1, b2 = y0 - m1 * x0, y0 - m2 * x0
    answer = f"({x0}, {y0})"
    trace = [
        TraceStep(op="set_equal", text=f"At an intersection, {fmt_linear(m1, b1)} = {fmt_linear(m2, b2)}."),
        TraceStep(op="solve_x", text=f"Solving gives x = {x0}."),
        TraceStep(op="solve_y", text=f"Substitute x = {x0} to get y = {y0}."),
        TraceStep(op="finish", text=f"So the intersection is {answer}.", after=answer),
    ]
    return make_sample("analytic_geometry_schema.line_intersection", f"Find the intersection of y={fmt_linear(m1, b1)} and y={fmt_linear(m2, b2)}.", trace, answer, {"m1": m1, "b1": b1, "m2": m2, "b2": b2, "difficulty": diff}, verified=(m1 * x0 + b1 == y0 and m2 * x0 + b2 == y0))


def gen_point_line_distance(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(-8, 8)
    px = rng.randint(-12, 12)
    py = rng.randint(-12, 12)
    dist = abs(px - a)
    trace = [
        TraceStep(op="vertical_line", text=f"The distance from ({px},{py}) to the vertical line x = {a} is the horizontal distance."),
        TraceStep(op="absolute_difference", text=f"That distance is |{px} - ({a})| = {dist}."),
        TraceStep(op="finish", text=f"So the distance is {dist}.", after=str(dist)),
    ]
    return make_sample("analytic_geometry_schema.point_line_distance", f"Find the distance from ({px},{py}) to the line x={a}.", trace, str(dist), {"a": a, "px": px, "py": py, "difficulty": diff}, verified=(dist == abs(px - a)))


def gen_circle_from_center_radius(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    h = rng.randint(1, 8)
    k = rng.randint(1, 8)
    r = rng.randint(2, 10)
    answer = f"(x - {h})^2 + (y - {k})^2 = {r * r}"
    trace = [
        TraceStep(op="circle_formula", text="A circle with center (h,k) and radius r has equation (x - h)^2 + (y - k)^2 = r^2."),
        TraceStep(op="substitute", text=f"Substitute h={h}, k={k}, and r={r}."),
        TraceStep(op="finish", text=f"So the equation is {answer}.", after=answer),
    ]
    return make_sample("analytic_geometry_schema.circle_from_center_radius", f"Write the equation of the circle with center ({h},{k}) and radius {r}.", trace, answer, {"h": h, "k": k, "r": r, "difficulty": diff}, verified=True)


def gen_circle_center_radius_by_completing_square(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    h = rng.randint(1, 8)
    k = rng.randint(1, 8)
    r = rng.randint(2, 10)
    D, E, F = -2 * h, -2 * k, h * h + k * k - r * r
    answer = f"center ({h}, {k}), radius {r}"
    trace = [
        TraceStep(op="complete_x", text=f"x^2 + ({D})x completes to (x - {h})^2 by adding {h * h}."),
        TraceStep(op="complete_y", text=f"y^2 + ({E})y completes to (y - {k})^2 by adding {k * k}."),
        TraceStep(op="read_circle", text=f"The completed form is (x - {h})^2 + (y - {k})^2 = {r * r}."),
        TraceStep(op="finish", text=f"So the circle has {answer}.", after=answer),
    ]
    return make_sample("analytic_geometry_schema.circle_center_radius_by_completing_square", f"Find the center and radius of x^2 + y^2 + ({D})x + ({E})y + ({F}) = 0.", trace, answer, {"h": h, "k": k, "r": r, "difficulty": diff}, verified=(D == -2 * h and E == -2 * k and F == h * h + k * k - r * r))


def gen_line_circle_intersection(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    r = rng.randint(2, {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff])
    answer = f"(-{r}, 0) and ({r}, 0)"
    trace = [
        TraceStep(op="substitute_line", text=f"On the line y = 0, the circle x^2 + y^2 = {r * r} becomes x^2 = {r * r}."),
        TraceStep(op="solve", text=f"Thus x = -{r} or x = {r}."),
        TraceStep(op="finish", text=f"So the intersection points are {answer}.", after=answer),
    ]
    return make_sample("analytic_geometry_schema.line_circle_intersection", f"Find where the line y=0 intersects the circle x^2+y^2={r * r}.", trace, answer, {"r": r, "difficulty": diff}, verified=True)


def gen_tangent_line_to_circle(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    r = rng.randint(2, 12)
    answer = f"x={r}"
    trace = [
        TraceStep(op="radius", text=f"The radius to ({r},0) on x^2 + y^2 = {r * r} is horizontal."),
        TraceStep(op="perpendicular", text=f"The tangent is perpendicular to that radius, so it is the vertical line through x = {r}."),
        TraceStep(op="finish", text=f"So the tangent line is {answer}.", after=answer),
    ]
    return make_sample("analytic_geometry_schema.tangent_line_to_circle", f"Find the tangent line to x^2+y^2={r * r} at ({r},0).", trace, answer, {"r": r, "difficulty": diff}, verified=True)


def gen_conic_basic_schema(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, 8)
    b = rng.randint(2, 8)
    while b == a:
        b = rng.randint(2, 8)
    answer = "ellipse"
    trace = [
        TraceStep(op="standard_form", text=f"The equation x^2/{a * a} + y^2/{b * b} = 1 has two positive squared denominators."),
        TraceStep(op="classify", text="A sum of squared terms equal to 1 is an ellipse."),
        TraceStep(op="finish", text=f"So the conic is an {answer}.", after=answer),
    ]
    return make_sample("analytic_geometry_schema.conic_basic_schema", f"Classify the conic x^2/{a * a} + y^2/{b * b} = 1.", trace, answer, {"a": a, "b": b, "difficulty": diff}, verified=True)


REGISTRY: Dict[str, Any] = {
    "analytic_geometry_schema.line_from_two_points": gen_line_from_two_points,
    "analytic_geometry_schema.line_intersection": gen_line_intersection,
    "analytic_geometry_schema.point_line_distance": gen_point_line_distance,
    "analytic_geometry_schema.circle_from_center_radius": gen_circle_from_center_radius,
    "analytic_geometry_schema.circle_center_radius_by_completing_square": gen_circle_center_radius_by_completing_square,
    "analytic_geometry_schema.line_circle_intersection": gen_line_circle_intersection,
    "analytic_geometry_schema.tangent_line_to_circle": gen_tangent_line_to_circle,
    "analytic_geometry_schema.conic_basic_schema": gen_conic_basic_schema,
}
