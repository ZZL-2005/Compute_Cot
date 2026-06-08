"""vectors domain (design.md sec 18).

Add/subtract, scalar multiply, dot product, norm, angle cosine, projection,
parallel/perpendicular test, and linear combination. 2D/3D integer vectors;
angle and projection use Pythagorean-magnitude vectors so results stay exact.
Every result is verified by direct computation.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict, List

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_add, fmt_mul, fmt_radical, fmt_sub, fmt_value, sqrt_simplify, sum_text


def fmt_vec(comps) -> str:
    return "(" + ", ".join(fmt_value(c) for c in comps) + ")"


def _vec(rng: random.Random, dim: int, hi: int) -> List[int]:
    return [rng.randint(-hi, hi) for _ in range(dim)]


def gen_vector_add_sub(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    dim = 2 if diff == Difficulty.EASY else rng.choice([2, 3])
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff]
    u, v = _vec(rng, dim, hi), _vec(rng, dim, hi)
    op = rng.choice(["+", "-"])
    res = [a + b if op == "+" else a - b for a, b in zip(u, v)]
    comp_lines = ", ".join(
        f"{fmt_add(a, b) if op == '+' else fmt_sub(a, b)} = {r}" for a, b, r in zip(u, v, res)
    )
    ans = fmt_vec(res)
    trace = [
        TraceStep(op="state_rule", text=f"{'Add' if op == '+' else 'Subtract'} the vectors component by component."),
        TraceStep(op="components", text=f"Components: {comp_lines}."),
        TraceStep(op="finish", text=f"So {fmt_vec(u)} {op} {fmt_vec(v)} = {ans}.", after=ans),
    ]
    return make_sample(
        "vectors.vector_add_sub",
        f"Compute {fmt_vec(u)} {op} {fmt_vec(v)}.",
        trace,
        ans,
        {"u": u, "v": v, "op": op, "difficulty": diff},
        verified=(res == [a + b if op == "+" else a - b for a, b in zip(u, v)]),
    )


def gen_scalar_multiplication(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    dim = rng.choice([2, 3])
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff]
    k = rng.randint(-6, 6)
    while k in (0, 1):
        k = rng.randint(-6, 6)
    u = _vec(rng, dim, hi)
    res = [k * a for a in u]
    comp_lines = ", ".join(f"{fmt_mul(k, a)} = {r}" for a, r in zip(u, res))
    ans = fmt_vec(res)
    trace = [
        TraceStep(op="state_rule", text=f"Multiply every component by the scalar {k}."),
        TraceStep(op="components", text=f"Components: {comp_lines}."),
        TraceStep(op="finish", text=f"So {k}·{fmt_vec(u)} = {ans}.", after=ans),
    ]
    return make_sample(
        "vectors.scalar_multiplication",
        f"Compute {k}·{fmt_vec(u)}.",
        trace,
        ans,
        {"k": k, "u": u, "difficulty": diff},
        verified=(res == [k * a for a in u]),
    )


def gen_dot_product(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    dim = 2 if diff == Difficulty.EASY else rng.choice([2, 3])
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    u, v = _vec(rng, dim, hi), _vec(rng, dim, hi)
    products = [a * b for a, b in zip(u, v)]
    result = sum(products)
    prod_text = " + ".join(fmt_mul(a, b) for a, b in zip(u, v))
    trace = [
        TraceStep(op="state_rule", text="The dot product multiplies matching components and sums them."),
        TraceStep(op="multiply", text=f"Products: {prod_text}."),
        TraceStep(op="sum", text=f"Sum: {sum_text(products)} = {result}."),
        TraceStep(op="finish", text=f"So {fmt_vec(u)}·{fmt_vec(v)} = {result}.", after=str(result)),
    ]
    return make_sample(
        "vectors.dot_product",
        f"Compute the dot product {fmt_vec(u)}·{fmt_vec(v)}.",
        trace,
        str(result),
        {"u": u, "v": v, "difficulty": diff},
        verified=(result == sum(a * b for a, b in zip(u, v))),
    )


def gen_norm(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    dim = 2 if diff == Difficulty.EASY else rng.choice([2, 3])
    hi = {Difficulty.EASY: 7, Difficulty.MEDIUM: 10, Difficulty.HARD: 14}[diff]
    u = _vec(rng, dim, hi)
    while all(c == 0 for c in u):
        u = _vec(rng, dim, hi)
    sq = sum(c * c for c in u)
    out, ins = sqrt_simplify(sq)
    ans = fmt_radical(out, ins)
    squares = " + ".join(f"({c})^2" for c in u)
    trace = [
        TraceStep(op="state_formula", text="The norm is the square root of the sum of squared components."),
        TraceStep(op="square_sum", text=f"{squares} = {sq}."),
        TraceStep(op="simplify_radical", text=f"|{fmt_vec(u)}| = sqrt({sq}) = {ans}."),
        TraceStep(op="finish", text=f"So the norm is {ans}.", after=ans),
    ]
    return make_sample(
        "vectors.norm",
        f"Find the norm of {fmt_vec(u)}.",
        trace,
        ans,
        {"u": u, "difficulty": diff},
        verified=(out * out * ins == sq),
    )


_PYTH_VEC = [(3, 4), (4, 3), (6, 8), (8, 6), (5, 12), (12, 5)]


def gen_vector_angle(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    u = list(rng.choice(_PYTH_VEC))
    v = list(rng.choice(_PYTH_VEC))
    for vec in (u, v):
        if rng.random() < 0.5:
            vec[0] = -vec[0]
        if rng.random() < 0.5:
            vec[1] = -vec[1]
    nu = round((u[0] ** 2 + u[1] ** 2) ** 0.5)
    nv = round((v[0] ** 2 + v[1] ** 2) ** 0.5)
    dot = u[0] * v[0] + u[1] * v[1]
    cos = Fraction(dot, nu * nv)
    ans = f"cos θ = {fmt_value(cos)}"
    trace = [
        TraceStep(op="state_formula", text="Use cos θ = (u·v)/(|u|·|v|)."),
        TraceStep(op="dot", text=f"u·v = {fmt_mul(u[0], v[0])} + {fmt_mul(u[1], v[1])} = {dot}."),
        TraceStep(op="norms", text=f"|u| = {nu} and |v| = {nv}, so |u|·|v| = {nu * nv}."),
        TraceStep(op="divide", text=f"cos θ = {dot}/{nu * nv} = {fmt_value(cos)}."),
        TraceStep(op="finish", text=f"So {ans}.", after=ans),
    ]
    return make_sample(
        "vectors.vector_angle",
        f"Find cos θ for the angle between {fmt_vec(u)} and {fmt_vec(v)}.",
        trace,
        ans,
        {"u": u, "v": v, "difficulty": diff},
        verified=(cos == Fraction(dot, nu * nv)),
    )


def gen_projection(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    u = _vec(rng, 2, hi)
    v = _vec(rng, 2, hi)
    while v[0] == 0 and v[1] == 0:
        v = _vec(rng, 2, hi)
    dot = u[0] * v[0] + u[1] * v[1]
    vv = v[0] * v[0] + v[1] * v[1]
    coef = Fraction(dot, vv)
    proj = [coef * v[0], coef * v[1]]
    ans = fmt_vec(proj)
    trace = [
        TraceStep(op="state_formula", text="The projection of u onto v is (u·v / v·v)·v."),
        TraceStep(op="dot_uv", text=f"u·v = {fmt_mul(u[0], v[0])} + {fmt_mul(u[1], v[1])} = {dot}."),
        TraceStep(op="dot_vv", text=f"v·v = {fmt_mul(v[0], v[0])} + {fmt_mul(v[1], v[1])} = {vv}."),
        TraceStep(op="scale", text=f"Scalar factor = {dot}/{vv} = {fmt_value(coef)}; multiply v by it: {ans}."),
        TraceStep(op="finish", text=f"So the projection is {ans}.", after=ans),
    ]
    return make_sample(
        "vectors.projection",
        f"Find the projection of u = {fmt_vec(u)} onto v = {fmt_vec(v)}.",
        trace,
        ans,
        {"u": u, "v": v, "difficulty": diff},
        verified=(proj == [Fraction(dot, vv) * v[0], Fraction(dot, vv) * v[1]]),
    )


def gen_parallel_perpendicular(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    u = _vec(rng, 2, hi)
    while u == [0, 0]:
        u = _vec(rng, 2, hi)
    roll = rng.random()
    if roll < 0.34:  # perpendicular: v = (-u1, u0)
        v = [-u[1], u[0]]
    elif roll < 0.67:  # parallel: v = k u
        k = rng.choice([-3, -2, 2, 3])
        v = [k * u[0], k * u[1]]
    else:
        v = _vec(rng, 2, hi)
    dot = u[0] * v[0] + u[1] * v[1]
    cross = u[0] * v[1] - u[1] * v[0]
    if dot == 0:
        word, reason = "perpendicular", f"their dot product is {dot}, so they are perpendicular"
    elif cross == 0:
        word, reason = "parallel", f"the cross-component u_x·v_y - u_y·v_x is {cross}, so they are parallel"
    else:
        word, reason = "neither", f"the dot product is {dot} (not 0) and the cross-component is {cross} (not 0)"
    trace = [
        TraceStep(op="dot", text=f"Dot product: {fmt_mul(u[0], v[0])} + {fmt_mul(u[1], v[1])} = {dot}."),
        TraceStep(op="cross", text=f"Cross-component: {fmt_mul(u[0], v[1])} - {fmt_mul(u[1], v[0])} = {cross}."),
        TraceStep(op="decide", text=f"Since {reason}."),
        TraceStep(op="finish", text=f"So the vectors are {word}.", after=word),
    ]
    return make_sample(
        "vectors.parallel_perpendicular",
        f"Are u = {fmt_vec(u)} and v = {fmt_vec(v)} parallel, perpendicular, or neither?",
        trace,
        word,
        {"u": u, "v": v, "difficulty": diff},
        verified=((word == "perpendicular") == (dot == 0) and (word == "parallel") == (dot != 0 and cross == 0)),
    )


def gen_linear_combination(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 14}[diff]
    a = rng.randint(-5, 5)
    b = rng.randint(-5, 5)
    while a == 0:
        a = rng.randint(-5, 5)
    while b == 0:
        b = rng.randint(-5, 5)
    u, v = _vec(rng, 2, hi), _vec(rng, 2, hi)
    au = [a * c for c in u]
    bv = [b * c for c in v]
    res = [au[i] + bv[i] for i in range(2)]
    ans = fmt_vec(res)
    trace = [
        TraceStep(op="scale_u", text=f"{a}·{fmt_vec(u)} = {fmt_vec(au)}."),
        TraceStep(op="scale_v", text=f"{b}·{fmt_vec(v)} = {fmt_vec(bv)}."),
        TraceStep(op="add", text=f"Add componentwise: ({fmt_add(au[0], bv[0])}, {fmt_add(au[1], bv[1])}) = {ans}."),
        TraceStep(op="finish", text=f"So {a}u + ({b})v = {ans}.", after=ans),
    ]
    return make_sample(
        "vectors.linear_combination",
        f"With u = {fmt_vec(u)} and v = {fmt_vec(v)}, compute {a}u + ({b})v.",
        trace,
        ans,
        {"a": a, "b": b, "u": u, "v": v, "difficulty": diff},
        verified=(res == [a * u[i] + b * v[i] for i in range(2)]),
    )


REGISTRY: Dict[str, Any] = {
    "vectors.vector_add_sub": gen_vector_add_sub,
    "vectors.scalar_multiplication": gen_scalar_multiplication,
    "vectors.dot_product": gen_dot_product,
    "vectors.norm": gen_norm,
    "vectors.vector_angle": gen_vector_angle,
    "vectors.projection": gen_projection,
    "vectors.parallel_perpendicular": gen_parallel_perpendicular,
    "vectors.linear_combination": gen_linear_combination,
}
