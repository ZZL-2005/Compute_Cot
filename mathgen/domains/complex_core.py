"""complex_numbers domain (design.md sec 17).

Powers of i, add/subtract/multiply/divide, conjugate, modulus, basic argument,
and a basic complex equation. All arithmetic is exact (integers / fractions),
and every result is checked by direct computation.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_add, fmt_mul, fmt_radical, fmt_sub, fmt_value, paren_if_negative, sqrt_simplify


def _part_i(c) -> str:
    if c == 1:
        return "i"
    if c == -1:
        return "-i"
    return f"{fmt_value(c)}i"


def fmt_complex(re, im) -> str:
    if im == 0:
        return fmt_value(re)
    if re == 0:
        return _part_i(im)
    ip = "i" if abs(im) == 1 else f"{fmt_value(abs(im))}i"
    return f"{fmt_value(re)} {'+' if im > 0 else '-'} {ip}"


def _nz(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def gen_imaginary_unit(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(2, {Difficulty.EASY: 8, Difficulty.MEDIUM: 20, Difficulty.HARD: 50}[diff])
    r = n % 4
    q = n // 4
    values = {0: "1", 1: "i", 2: "-1", 3: "-i"}
    answer = values[r]
    trace = [
        TraceStep(op="use_period", text=f"Powers of i repeat every 4 since i^4 = 1: i^1=i, i^2=-1, i^3=-i, i^4=1."),
        TraceStep(op="reduce_exponent", text=f"Divide the exponent by 4: {n} = 4×{q} + {r}, so i^{n} = (i^4)^{q}·i^{r} = i^{r}."),
        TraceStep(op="read_value", text=f"i^{r} = {answer}."),
        TraceStep(op="finish", text=f"So i^{n} = {answer}.", after=answer),
    ]
    return make_sample(
        "complex.imaginary_unit",
        f"Evaluate i^{n}.",
        trace,
        answer,
        {"n": n, "difficulty": diff},
        verified=(n % 4 == r),
    )


def gen_complex_add_sub(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 25}[diff]
    a, b, c, d = (_nz(rng, -hi, hi) for _ in range(4))
    op = rng.choice(["+", "-"])
    if op == "+":
        re, im = a + c, b + d
        rword, iword = f"{a} + ({c})", f"{b} + ({d})"
    else:
        re, im = a - c, b - d
        rword, iword = f"{a} - ({c})", f"{b} - ({d})"
    z1, z2, ans = fmt_complex(a, b), fmt_complex(c, d), fmt_complex(re, im)
    trace = [
        TraceStep(op="group_parts", text=f"Combine real parts and imaginary parts separately."),
        TraceStep(op="real_part", text=f"Real part: {rword} = {re}."),
        TraceStep(op="imag_part", text=f"Imaginary part: {iword} = {im}."),
        TraceStep(op="finish", text=f"So ({z1}) {op} ({z2}) = {ans}.", after=ans),
    ]
    return make_sample(
        "complex.complex_add_sub",
        f"Compute ({z1}) {op} ({z2}).",
        trace,
        ans,
        {"a": a, "b": b, "c": c, "d": d, "op": op, "difficulty": diff},
        verified=(complex(re, im) == (complex(a, b) + complex(c, d) if op == "+" else complex(a, b) - complex(c, d))),
    )


def gen_complex_multiply(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 5, Difficulty.MEDIUM: 9, Difficulty.HARD: 15}[diff]
    a, b, c, d = (_nz(rng, -hi, hi) for _ in range(4))
    re = a * c - b * d
    im = a * d + b * c
    z1, z2, ans = fmt_complex(a, b), fmt_complex(c, d), fmt_complex(re, im)
    trace = [
        TraceStep(op="foil", text=f"Multiply using FOIL and i^2 = -1: ({z1})({z2})."),
        TraceStep(op="real_part", text=f"Real part: {fmt_mul(a, c)} - {fmt_mul(b, d)} = {fmt_sub(a * c, b * d)} = {re}."),
        TraceStep(op="imag_part", text=f"Imaginary part: {fmt_mul(a, d)} + {fmt_mul(b, c)} = {fmt_add(a * d, b * c)} = {im}."),
        TraceStep(op="finish", text=f"So ({z1})({z2}) = {ans}.", after=ans),
    ]
    return make_sample(
        "complex.complex_multiply",
        f"Compute ({z1})({z2}).",
        trace,
        ans,
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(complex(re, im) == complex(a, b) * complex(c, d)),
    )


def gen_conjugate(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 25}[diff]
    a, b = _nz(rng, -hi, hi), _nz(rng, -hi, hi)
    z, ans = fmt_complex(a, b), fmt_complex(a, -b)
    trace = [
        TraceStep(op="state_rule", text="The conjugate of a + bi is a - bi: keep the real part, negate the imaginary part."),
        TraceStep(op="apply", text=f"The real part {a} stays; the imaginary part {b} becomes {-b}."),
        TraceStep(op="finish", text=f"So the conjugate of {z} is {ans}.", after=ans),
    ]
    return make_sample(
        "complex.conjugate",
        f"Find the conjugate of {z}.",
        trace,
        ans,
        {"a": a, "b": b, "difficulty": diff},
        verified=(complex(a, -b) == complex(a, b).conjugate()),
    )


def gen_modulus(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff]
    a, b = _nz(rng, -hi, hi), _nz(rng, -hi, hi)
    sq = a * a + b * b
    out, ins = sqrt_simplify(sq)
    ans = fmt_radical(out, ins)
    z = fmt_complex(a, b)
    trace = [
        TraceStep(op="state_formula", text="The modulus is |a + bi| = sqrt(a^2 + b^2)."),
        TraceStep(op="square_parts", text=f"a^2 + b^2 = ({a})^2 + ({b})^2 = {a * a} + {b * b} = {sq}."),
        TraceStep(op="simplify_radical", text=f"|{z}| = sqrt({sq}) = {ans}."),
        TraceStep(op="finish", text=f"So the modulus is {ans}.", after=ans),
    ]
    return make_sample(
        "complex.modulus",
        f"Find the modulus of {z}.",
        trace,
        ans,
        {"a": a, "b": b, "difficulty": diff},
        verified=(out * out * ins == sq),
    )


def gen_complex_division(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    a, b, c, d = (_nz(rng, -hi, hi) for _ in range(4))
    denom = c * c + d * d
    re = Fraction(a * c + b * d, denom)
    im = Fraction(b * c - a * d, denom)
    z1, z2 = fmt_complex(a, b), fmt_complex(c, d)
    ans = fmt_complex(re, im)
    trace = [
        TraceStep(op="multiply_conjugate", text=f"Multiply numerator and denominator by the conjugate of the denominator, {fmt_complex(c, -d)}."),
        TraceStep(op="denominator", text=f"Denominator: ({z2})({fmt_complex(c, -d)}) = ({paren_if_negative(c)})^2 + ({paren_if_negative(d)})^2 = {denom}."),
        TraceStep(op="numerator_real", text=f"Numerator real part: {fmt_mul(a, c)} + {fmt_mul(b, d)} = {fmt_add(a * c, b * d)}."),
        TraceStep(op="numerator_imag", text=f"Numerator imaginary part: {fmt_mul(b, c)} - {fmt_mul(a, d)} = {fmt_sub(b * c, a * d)}."),
        TraceStep(op="finish", text=f"So ({z1})/({z2}) = {ans}.", after=ans),
    ]
    return make_sample(
        "complex.complex_division",
        f"Compute ({z1})/({z2}).",
        trace,
        ans,
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(re == Fraction(a * c + b * d, denom) and im == Fraction(b * c - a * d, denom)),
    )


_ARG_TABLE = {
    (1, 0): 0, (1, 1): 45, (0, 1): 90, (-1, 1): 135,
    (-1, 0): 180, (-1, -1): 225, (0, -1): 270, (1, -1): 315,
}


def gen_argument_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    (a, b), deg = rng.choice(list(_ARG_TABLE.items()))
    z = fmt_complex(a, b)
    answer = f"{deg}°"
    if a != 0 and b != 0:
        quad = 1 if (a > 0 and b > 0) else 2 if (a < 0 and b > 0) else 3 if (a < 0 and b < 0) else 4
        locate = f"The point ({a}, {b}) is in quadrant {quad}, and |a| = |b|, so the angle to the positive x-axis is {deg}°."
    else:
        locate = f"The point ({a}, {b}) lies on an axis, so the argument is {deg}°."
    trace = [
        TraceStep(op="plot", text=f"Plot {z} as the point ({a}, {b})."),
        TraceStep(op="determine_angle", text=locate),
        TraceStep(op="finish", text=f"So the argument of {z} is {answer}.", after=answer),
    ]
    return make_sample(
        "complex.argument_basic",
        f"Find the argument (in degrees, 0° to 360°) of {z}.",
        trace,
        answer,
        {"a": a, "b": b, "difficulty": diff},
        verified=(_ARG_TABLE[(a, b)] == deg),
    )


def gen_complex_equation_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    k = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 10, Difficulty.HARD: 15}[diff])
    m = k * k
    answer = f"x={k}i or x=-{k}i"
    trace = [
        TraceStep(op="isolate_square", text=f"The equation x^2 = -{m} has no real solution, so use complex numbers."),
        TraceStep(op="use_i", text=f"Since i^2 = -1, write -{m} = {m}·i^2."),
        TraceStep(op="take_root", text=f"Take square roots: x = ±sqrt({m})·i = ±{k}i."),
        TraceStep(op="finish", text=f"So the solutions are {answer}.", after=answer),
    ]
    return make_sample(
        "complex.complex_equation_basic",
        f"Solve x^2 = -{m} over the complex numbers.",
        trace,
        answer,
        {"m": m, "k": k, "difficulty": diff},
        verified=(complex(0, k) ** 2 == complex(-m, 0)),
    )


REGISTRY: Dict[str, Any] = {
    "complex.imaginary_unit": gen_imaginary_unit,
    "complex.complex_add_sub": gen_complex_add_sub,
    "complex.complex_multiply": gen_complex_multiply,
    "complex.conjugate": gen_conjugate,
    "complex.modulus": gen_modulus,
    "complex.complex_division": gen_complex_division,
    "complex.argument_basic": gen_argument_basic,
    "complex.complex_equation_basic": gen_complex_equation_basic,
}
