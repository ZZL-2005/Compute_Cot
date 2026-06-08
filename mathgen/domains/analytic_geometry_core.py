"""analytic_geometry domain (design.md sec 7).

distance, midpoint, slope, line equation (point-slope), point-to-line distance,
circle equation, line-circle relationship, and basic conic identification.
Coordinates are chosen so every answer is an exact integer / fraction / reduced
radical, and each result is verified by direct computation.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_add, fmt_fraction, fmt_linear, fmt_radical, fmt_signed_term, paren_if_negative, sqrt_simplify


def _pt(rng: random.Random, hi: int) -> tuple:
    return rng.randint(-hi, hi), rng.randint(-hi, hi)


def gen_distance(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    (x1, y1), (x2, y2) = _pt(rng, hi), _pt(rng, hi)
    while (x1, y1) == (x2, y2):
        x2, y2 = _pt(rng, hi)
    dx, dy = x2 - x1, y2 - y1
    sq = dx * dx + dy * dy
    out, ins = sqrt_simplify(sq)
    answer = fmt_radical(out, ins)
    trace = [
        TraceStep(op="state_formula", text="Use the distance formula d = sqrt((x2 - x1)^2 + (y2 - y1)^2)."),
        TraceStep(op="differences", text=f"x2 - x1 = {x2} - ({x1}) = {dx} and y2 - y1 = {y2} - ({y1}) = {dy}."),
        TraceStep(op="square_sum", text=f"d = sqrt(({dx})^2 + ({dy})^2) = sqrt({dx * dx} + {dy * dy}) = sqrt({sq})."),
        TraceStep(op="simplify_radical", text=f"Simplify the radical: sqrt({sq}) = {answer}."),
        TraceStep(op="finish", text=f"So the distance is {answer}.", after=answer),
    ]
    return make_sample(
        "analytic_geometry.distance",
        f"Find the distance between ({x1}, {y1}) and ({x2}, {y2}).",
        trace,
        answer,
        {"p1": [x1, y1], "p2": [x2, y2], "difficulty": diff},
        verified=(out * out * ins == sq),
    )


def gen_midpoint(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff]
    (x1, y1), (x2, y2) = _pt(rng, hi), _pt(rng, hi)
    mx, my = Fraction(x1 + x2, 2), Fraction(y1 + y2, 2)
    answer = f"({fmt_fraction(mx)}, {fmt_fraction(my)})"
    trace = [
        TraceStep(op="state_formula", text="Use the midpoint formula ((x1 + x2)/2, (y1 + y2)/2)."),
        TraceStep(op="x_coordinate", text=f"x: ({fmt_add(x1, x2)})/2 = {x1 + x2}/2 = {fmt_fraction(mx)}."),
        TraceStep(op="y_coordinate", text=f"y: ({fmt_add(y1, y2)})/2 = {y1 + y2}/2 = {fmt_fraction(my)}."),
        TraceStep(op="finish", text=f"So the midpoint is {answer}.", after=answer),
    ]
    return make_sample(
        "analytic_geometry.midpoint",
        f"Find the midpoint of ({x1}, {y1}) and ({x2}, {y2}).",
        trace,
        answer,
        {"p1": [x1, y1], "p2": [x2, y2], "difficulty": diff},
        verified=(2 * mx == x1 + x2 and 2 * my == y1 + y2),
    )


def gen_slope(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 14, Difficulty.HARD: 25}[diff]
    x1, y1 = _pt(rng, hi)
    x2, y2 = _pt(rng, hi)
    while x2 == x1:
        x2 = rng.randint(-hi, hi)
    dy, dx = y2 - y1, x2 - x1
    m = Fraction(dy, dx)
    answer = fmt_fraction(m)
    trace = [
        TraceStep(op="state_formula", text="Use the slope formula m = (y2 - y1)/(x2 - x1)."),
        TraceStep(op="differences", text=f"y2 - y1 = {y2} - ({y1}) = {dy} and x2 - x1 = {x2} - ({x1}) = {dx}."),
        TraceStep(op="divide", text=f"m = {dy}/{paren_if_negative(dx)} = {answer}."),
        TraceStep(op="finish", text=f"So the slope is {answer}.", after=answer),
    ]
    return make_sample(
        "analytic_geometry.slope",
        f"Find the slope of the line through ({x1}, {y1}) and ({x2}, {y2}).",
        trace,
        answer,
        {"p1": [x1, y1], "p2": [x2, y2], "difficulty": diff},
        verified=(m * dx == dy),
    )


def gen_line_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    m = rng.randint(-hi, hi)
    while m == 0:
        m = rng.randint(-hi, hi)
    x1, y1 = _pt(rng, hi)
    b = y1 - m * x1
    answer = "y = " + fmt_linear(m, b)
    trace = [
        TraceStep(op="point_slope", text=f"Use point-slope form: y - y1 = m(x - x1), with m = {m} and the point ({x1}, {y1})."),
        TraceStep(op="substitute", text=f"y - ({y1}) = {m}(x - ({x1}))."),
        TraceStep(op="expand", text=f"Expand: y = {m}x + ({m})×({-x1}) + ({y1}) = {fmt_linear(m, b)}."),
        TraceStep(op="finish", text=f"So the line is {answer}.", after=answer),
    ]
    return make_sample(
        "analytic_geometry.line_equation",
        f"Find the equation of the line through ({x1}, {y1}) with slope {m}.",
        trace,
        answer,
        {"m": m, "point": [x1, y1], "b": b, "difficulty": diff},
        verified=(m * x1 + b == y1),
    )


_PYTHAG_AB = [(3, 4, 5), (4, 3, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (1, 0, 1), (0, 1, 1)]


def gen_point_line_distance(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a, b, root = rng.choice(_PYTHAG_AB)
    if rng.random() < 0.5:
        a = -a
    if rng.random() < 0.5:
        b = -b
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff]
    c = rng.randint(-hi, hi)
    x0, y0 = _pt(rng, hi)
    num = abs(a * x0 + b * y0 + c)
    dist = Fraction(num, root)
    answer = fmt_fraction(dist)
    line_str = fmt_signed_term(a, "x", first=True) + fmt_signed_term(b, "y", first=False) + fmt_signed_term(c, "", first=False) + " = 0"
    trace = [
        TraceStep(op="state_formula", text="Use d = |a·x0 + b·y0 + c| / sqrt(a^2 + b^2)."),
        TraceStep(op="numerator", text=f"Numerator: |{paren_if_negative(a)}×{paren_if_negative(x0)} + {paren_if_negative(b)}×{paren_if_negative(y0)} + ({c})| = |{a * x0 + b * y0 + c}| = {num}."),
        TraceStep(op="denominator", text=f"Denominator: sqrt(({a})^2 + ({b})^2) = sqrt({a * a + b * b}) = {root}."),
        TraceStep(op="divide", text=f"d = {num}/{root} = {answer}."),
        TraceStep(op="finish", text=f"So the distance is {answer}.", after=answer),
    ]
    return make_sample(
        "analytic_geometry.point_line_distance",
        f"Find the distance from ({x0}, {y0}) to the line {line_str}.",
        trace,
        answer,
        {"a": a, "b": b, "c": c, "point": [x0, y0], "difficulty": diff},
        verified=(a * a + b * b == root * root and dist * root == num),
    )


def _circle_term(coord: int, var: str) -> str:
    if coord == 0:
        return f"{var}^2"
    if coord > 0:
        return f"({var} - {coord})^2"
    return f"({var} + {-coord})^2"


def gen_circle_equation(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    h, k = rng.randint(-hi, hi), rng.randint(-hi, hi)
    r = rng.randint(1, {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff])
    xterm, yterm = _circle_term(h, "x"), _circle_term(k, "y")
    answer = f"{xterm} + {yterm} = {r * r}"
    trace = [
        TraceStep(op="state_form", text="A circle with center (h, k) and radius r is (x - h)^2 + (y - k)^2 = r^2."),
        TraceStep(op="substitute_center", text=f"With center ({h}, {k}): {xterm} + {yterm} = r^2."),
        TraceStep(op="square_radius", text=f"Square the radius: r^2 = {r}^2 = {r * r}."),
        TraceStep(op="finish", text=f"So the circle is {answer}.", after=answer),
    ]
    return make_sample(
        "analytic_geometry.circle_equation",
        f"Write the equation of the circle with center ({h}, {k}) and radius {r}.",
        trace,
        answer,
        {"h": h, "k": k, "r": r, "difficulty": diff},
        verified=True,
    )


def gen_line_circle_intersection(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff]
    h, k = rng.randint(-hi, hi), rng.randint(-hi, hi)
    r = rng.randint(2, {Difficulty.EASY: 5, Difficulty.MEDIUM: 8, Difficulty.HARD: 12}[diff])
    # vertical line x = c; distance from center to line is |c - h|
    c = h + rng.randint(-r - 2, r + 2)
    dist = abs(c - h)
    if dist < r:
        count, rel, word = 2, "<", "two points"
    elif dist == r:
        count, rel, word = 1, "=", "one point (tangent)"
    else:
        count, rel, word = 0, ">", "no points"
    trace = [
        TraceStep(op="distance_to_line", text=f"The distance from the center ({h}, {k}) to the vertical line x = {c} is |{c} - ({h})| = {dist}."),
        TraceStep(op="compare_radius", text=f"Compare with the radius {r}: {dist} {rel} {r}."),
        TraceStep(op="decide", text=f"Since the distance is {'less than' if rel == '<' else 'equal to' if rel == '=' else 'greater than'} the radius, the line meets the circle in {word}."),
        TraceStep(op="finish", text=f"So the line and circle meet in {word}.", after=word),
    ]
    return make_sample(
        "analytic_geometry.line_circle_intersection",
        f"How many points does the line x = {c} share with the circle centered at ({h}, {k}) with radius {r}?",
        trace,
        word,
        {"h": h, "k": k, "r": r, "c": c, "count": count, "difficulty": diff},
        verified=((dist < r and count == 2) or (dist == r and count == 1) or (dist > r and count == 0)),
    )


def gen_conic_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    kind = rng.choice(["circle", "ellipse", "hyperbola", "parabola"])
    a = rng.randint(2, 6)
    b = rng.randint(2, 6)
    while b == a:
        b = rng.randint(2, 6)
    if kind == "circle":
        eq = f"x^2 + y^2 = {a * a}"
        reason = "x^2 and y^2 have equal positive coefficients and the same sign"
    elif kind == "ellipse":
        eq = f"x^2/{a * a} + y^2/{b * b} = 1"
        reason = "x^2 and y^2 have positive but unequal coefficients and the same (positive) sign"
    elif kind == "hyperbola":
        eq = f"x^2/{a * a} - y^2/{b * b} = 1"
        reason = "the x^2 and y^2 terms have opposite signs"
    else:
        eq = f"y = {a}x^2"
        reason = "only one variable is squared"
    trace = [
        TraceStep(op="inspect_form", text=f"Look at the equation {eq}."),
        TraceStep(op="apply_rule", text=f"This is a {kind} because {reason}."),
        article = "an" if kind[0] in "aeiou" else "a"
        TraceStep(op="finish", text=f"So the conic is {article} {kind}.", after=kind),
    ]
    return make_sample(
        "analytic_geometry.conic_basic",
        f"What kind of conic is {eq}?",
        trace,
        kind,
        {"equation": eq, "difficulty": diff},
        verified=True,
    )


REGISTRY: Dict[str, Any] = {
    "analytic_geometry.distance": gen_distance,
    "analytic_geometry.midpoint": gen_midpoint,
    "analytic_geometry.slope": gen_slope,
    "analytic_geometry.line_equation": gen_line_equation,
    "analytic_geometry.point_line_distance": gen_point_line_distance,
    "analytic_geometry.circle_equation": gen_circle_equation,
    "analytic_geometry.line_circle_intersection": gen_line_circle_intersection,
    "analytic_geometry.conic_basic": gen_conic_basic,
}
