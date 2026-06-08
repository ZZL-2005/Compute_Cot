"""matrices_linear_algebra_basic domain (design.md sec 19).

2x2 (and 3x3 determinant) operations: add/subtract, scalar multiply, multiply,
2x2 and 3x3 determinants, 2x2 inverse, and solving a 2x2 system by Cramer's
rule. Exact integer/fraction arithmetic, each entry computed explicitly and
verified by direct computation.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Dict, List

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import fmt_add, fmt_mul, fmt_signed_term, fmt_sub, fmt_value, paren_if_negative


def _nz(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def fmt_mat(rows) -> str:
    return "[" + ", ".join("[" + ", ".join(fmt_value(x) for x in r) + "]" for r in rows) + "]"


def _mat(rng: random.Random, n: int, hi: int) -> List[List[int]]:
    return [[rng.randint(-hi, hi) for _ in range(n)] for _ in range(n)]


def gen_matrix_add_sub(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 8, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff]
    A, B = _mat(rng, 2, hi), _mat(rng, 2, hi)
    op = rng.choice(["+", "-"])
    C = [[A[i][j] + B[i][j] if op == "+" else A[i][j] - B[i][j] for j in range(2)] for i in range(2)]
    cells = ", ".join(
        f"{(fmt_add if op == '+' else fmt_sub)(A[i][j], B[i][j])} = {C[i][j]}"
        for i in range(2) for j in range(2)
    )
    ans = fmt_mat(C)
    trace = [
        TraceStep(op="state_rule", text=f"{'Add' if op == '+' else 'Subtract'} the matrices entry by entry."),
        TraceStep(op="entries", text=f"Entries: {cells}."),
        TraceStep(op="finish", text=f"So the result is {ans}.", after=ans),
    ]
    return make_sample(
        "matrices.matrix_add_sub",
        f"Compute {fmt_mat(A)} {op} {fmt_mat(B)}.",
        trace,
        ans,
        {"A": A, "B": B, "op": op, "difficulty": diff},
        verified=(C == [[A[i][j] + B[i][j] if op == "+" else A[i][j] - B[i][j] for j in range(2)] for i in range(2)]),
    )


def gen_scalar_matrix_multiply(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    k = rng.randint(-6, 6)
    while k in (0, 1):
        k = rng.randint(-6, 6)
    A = _mat(rng, 2, hi)
    C = [[k * A[i][j] for j in range(2)] for i in range(2)]
    cells = ", ".join(f"{fmt_mul(k, A[i][j])} = {C[i][j]}" for i in range(2) for j in range(2))
    ans = fmt_mat(C)
    trace = [
        TraceStep(op="state_rule", text=f"Multiply every entry by the scalar {k}."),
        TraceStep(op="entries", text=f"Entries: {cells}."),
        TraceStep(op="finish", text=f"So {k}·{fmt_mat(A)} = {ans}.", after=ans),
    ]
    return make_sample(
        "matrices.scalar_matrix_multiply",
        f"Compute {k}·{fmt_mat(A)}.",
        trace,
        ans,
        {"k": k, "A": A, "difficulty": diff},
        verified=(C == [[k * A[i][j] for j in range(2)] for i in range(2)]),
    )


def gen_matrix_multiply(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    A, B = _mat(rng, 2, hi), _mat(rng, 2, hi)
    C = [[A[i][0] * B[0][j] + A[i][1] * B[1][j] for j in range(2)] for i in range(2)]
    trace = [
        TraceStep(op="state_rule", text=f"Multiply {fmt_mat(A)} × {fmt_mat(B)}. Each entry c[ij] is the dot product of row i of A with column j of B."),
    ]
    for i in range(2):
        for j in range(2):
            p1, p2 = A[i][0] * B[0][j], A[i][1] * B[1][j]
            trace.append(TraceStep(
                op="compute_entry",
                text=f"c[{i+1}{j+1}] = row{i+1}·col{j+1} = {fmt_mul(A[i][0], B[0][j])} + {fmt_mul(A[i][1], B[1][j])} = {fmt_add(p1, p2)} = {C[i][j]}.",
                meta={"row": i, "col": j, "entry": C[i][j]},
            ))
    ans = fmt_mat(C)
    trace.append(TraceStep(op="finish", text=f"So the product is {ans}.", after=ans))
    return make_sample(
        "matrices.matrix_multiply",
        f"Compute {fmt_mat(A)} × {fmt_mat(B)}.",
        trace,
        ans,
        {"A": A, "B": B, "difficulty": diff},
        verified=(C == [[A[i][0] * B[0][j] + A[i][1] * B[1][j] for j in range(2)] for i in range(2)]),
    )


def gen_determinant_2x2(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff]
    A = _mat(rng, 2, hi)
    (a, b), (c, d) = A
    det = a * d - b * c
    trace = [
        TraceStep(op="state_rule", text="For a 2x2 matrix [[a, b], [c, d]] the determinant is ad - bc."),
        TraceStep(op="compute", text=f"det = {fmt_mul(a, d)} - {fmt_mul(b, c)} = {fmt_sub(a * d, b * c)} = {det}."),
        TraceStep(op="finish", text=f"So the determinant is {det}.", after=str(det)),
    ]
    return make_sample(
        "matrices.determinant_2x2",
        f"Find the determinant of {fmt_mat(A)}.",
        trace,
        str(det),
        {"A": A, "difficulty": diff},
        verified=(det == a * d - b * c),
    )


def gen_determinant_3x3(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 3, Difficulty.MEDIUM: 6, Difficulty.HARD: 9}[diff]
    A = _mat(rng, 3, hi)
    (a, b, c), (d, e, f), (g, h, i) = A
    m1 = e * i - f * h
    m2 = d * i - f * g
    m3 = d * h - e * g
    det = a * m1 - b * m2 + c * m3
    trace = [
        TraceStep(op="state_rule", text="Expand along the first row: det = a(ei - fh) - b(di - fg) + c(dh - eg)."),
        TraceStep(op="minor1", text=f"ei - fh = {fmt_mul(e, i)} - {fmt_mul(f, h)} = {m1}."),
        TraceStep(op="minor2", text=f"di - fg = {fmt_mul(d, i)} - {fmt_mul(f, g)} = {m2}."),
        TraceStep(op="minor3", text=f"dh - eg = {fmt_mul(d, h)} - {fmt_mul(e, g)} = {m3}."),
        TraceStep(op="combine", text=f"det = {fmt_mul(a, m1)} - {fmt_mul(b, m2)} + {fmt_mul(c, m3)} = {det}."),
        TraceStep(op="finish", text=f"So the determinant is {det}.", after=str(det)),
    ]
    return make_sample(
        "matrices.determinant_3x3_basic",
        f"Find the determinant of {fmt_mat(A)}.",
        trace,
        str(det),
        {"A": A, "difficulty": diff},
        verified=(det == a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)),
    )


def gen_inverse_2x2(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    A = _mat(rng, 2, hi)
    (a, b), (c, d) = A
    det = a * d - b * c
    while det == 0:
        A = _mat(rng, 2, hi)
        (a, b), (c, d) = A
        det = a * d - b * c
    inv = [[Fraction(d, det), Fraction(-b, det)], [Fraction(-c, det), Fraction(a, det)]]
    ans = fmt_mat(inv)
    trace = [
        TraceStep(op="determinant", text=f"First the determinant: det = {fmt_mul(a, d)} - {fmt_mul(b, c)} = {det}."),
        TraceStep(op="state_formula", text="The inverse is (1/det)·[[d, -b], [-c, a]]."),
        TraceStep(op="swap_negate", text=f"Swap a and d and negate b and c: [[{d}, {-b}], [{-c}, {a}]]."),
        TraceStep(op="scale", text=f"Divide each entry by {det}: {ans}."),
        TraceStep(op="finish", text=f"So the inverse is {ans}.", after=ans),
    ]
    return make_sample(
        "matrices.inverse_2x2",
        f"Find the inverse of {fmt_mat(A)}.",
        trace,
        ans,
        {"A": A, "det": det, "difficulty": diff},
        verified=(det != 0 and inv == [[Fraction(d, det), Fraction(-b, det)], [Fraction(-c, det), Fraction(a, det)]]),
    )


def gen_solve_linear_system_matrix(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    hi = {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 10}[diff]
    a1, b1, a2, b2 = (_nz(rng, -hi, hi) for _ in range(4))
    D = a1 * b2 - a2 * b1
    while D == 0:
        a1, b1, a2, b2 = (_nz(rng, -hi, hi) for _ in range(4))
        D = a1 * b2 - a2 * b1
    x0, y0 = rng.randint(-6, 6), rng.randint(-6, 6)
    c1, c2 = a1 * x0 + b1 * y0, a2 * x0 + b2 * y0
    row1 = f"{fmt_signed_term(a1, 'x', first=True)}{fmt_signed_term(b1, 'y', first=False)} = {c1}"
    row2 = f"{fmt_signed_term(a2, 'x', first=True)}{fmt_signed_term(b2, 'y', first=False)} = {c2}"
    Dx = c1 * b2 - c2 * b1
    Dy = a1 * c2 - a2 * c1
    x = Fraction(Dx, D)
    y = Fraction(Dy, D)
    answer = f"x={fmt_value(x)}, y={fmt_value(y)}"
    trace = [
        TraceStep(op="state_method", text="Use Cramer's rule: x = Dx/D, y = Dy/D, where D is the coefficient determinant."),
        TraceStep(op="main_det", text=f"D = {fmt_mul(a1, b2)} - {fmt_mul(a2, b1)} = {D}."),
        TraceStep(op="dx", text=f"Dx (replace the x-column with constants) = {fmt_mul(c1, b2)} - {fmt_mul(c2, b1)} = {Dx}."),
        TraceStep(op="dy", text=f"Dy (replace the y-column with constants) = {fmt_mul(a1, c2)} - {fmt_mul(a2, c1)} = {Dy}."),
        TraceStep(op="divide", text=f"x = {Dx}/{paren_if_negative(D)} = {fmt_value(x)} and y = {Dy}/{paren_if_negative(D)} = {fmt_value(y)}."),
        TraceStep(op="finish", text=f"So the solution is {answer}.", after=answer),
    ]
    return make_sample(
        "matrices.solve_linear_system_matrix",
        f"Solve the system {row1}; {row2} using Cramer's rule.",
        trace,
        answer,
        {"a1": a1, "b1": b1, "c1": c1, "a2": a2, "b2": b2, "c2": c2, "difficulty": diff},
        verified=(a1 * x + b1 * y == c1 and a2 * x + b2 * y == c2),
    )


REGISTRY: Dict[str, Any] = {
    "matrices.matrix_add_sub": gen_matrix_add_sub,
    "matrices.scalar_matrix_multiply": gen_scalar_matrix_multiply,
    "matrices.matrix_multiply": gen_matrix_multiply,
    "matrices.determinant_2x2": gen_determinant_2x2,
    "matrices.determinant_3x3_basic": gen_determinant_3x3,
    "matrices.inverse_2x2": gen_inverse_2x2,
    "matrices.solve_linear_system_matrix": gen_solve_linear_system_matrix,
}
