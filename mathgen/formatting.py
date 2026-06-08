"""Unified expression formatter.

Every domain must render numbers/expressions through these helpers instead of
hand-concatenating strings, so the dataset never contains dirty fragments like
``+-``, ``+ -``, ``-12--7`` or unsimplified fractions (des_instruct.md sec 5).
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction
from typing import List, Sequence, Tuple


PLACES = [
    "ones",
    "tens",
    "hundreds",
    "thousands",
    "ten-thousands",
    "hundred-thousands",
    "millions",
    "ten-millions",
]


def place_name(i: int) -> str:
    if i < len(PLACES):
        return PLACES[i]
    return f"10^{i} place"


def paren_if_negative(n) -> str:
    s = str(n)
    if s.startswith("-"):
        return f"({s})"
    return s


def fmt_int(n: int) -> str:
    return str(n)


def fmt_signed_term(coef: int, var: str = "x", first: bool = False) -> str:
    """Format terms like -3x, + 5x, - 2, without ugly '+-'."""
    if var:
        if coef == 1:
            body = var
        elif coef == -1:
            body = var
        else:
            body = f"{abs(coef)}{var}"
    else:
        body = str(abs(coef))

    if first:
        if coef < 0:
            return f"-{body}"
        return body
    if coef < 0:
        return f" - {body}"
    return f" + {body}"


def fmt_linear(a: int, b: int, var: str = "x") -> str:
    parts: List[str] = []
    if a != 0:
        parts.append(fmt_signed_term(a, var, first=True))
    if b != 0 or not parts:
        parts.append(fmt_signed_term(b, "", first=not parts))
    return "".join(parts)


def fmt_sub(a, b) -> str:
    if isinstance(b, int) and b < 0:
        return f"{a} - ({b})"
    s = str(b)
    if s.startswith("-"):
        return f"{a} - ({s})"
    return f"{a} - {b}"


def fmt_add(a, b) -> str:
    if isinstance(b, int) and b < 0:
        return f"{a} - {abs(b)}"
    s = str(b)
    if s.startswith("-"):
        return f"{a} - {s[1:]}"
    return f"{a} + {b}"


def fmt_mul(a, b) -> str:
    return f"{paren_if_negative(a)}×{paren_if_negative(b)}"


def fmt_term(coef: int, power: int, var: str = "x", first: bool = False) -> str:
    """Render one polynomial term with its connecting sign (' + ' / ' - ')."""
    a = abs(coef)
    if power == 0:
        body = str(a)
    elif power == 1:
        body = var if a == 1 else f"{a}{var}"
    else:
        body = f"{var}^{power}" if a == 1 else f"{a}{var}^{power}"
    if first:
        return f"-{body}" if coef < 0 else body
    return f" - {body}" if coef < 0 else f" + {body}"


def fmt_poly(terms, var: str = "x") -> str:
    """Render a polynomial from (coef, power) pairs given high power to low."""
    out: List[str] = []
    for coef, power in terms:
        if coef == 0:
            continue
        out.append(fmt_term(coef, power, var, first=not out))
    if not out:
        return "0"
    return "".join(out)


def fmt_factor(p: int, var: str = "x") -> str:
    """Render a linear factor (x - r) given the root r = -p... actually given offset p in (x + p)."""
    if p == 0:
        return f"{var}"
    if p < 0:
        return f"({var} - {abs(p)})"
    return f"({var} + {p})"


def fmt_fraction(fr: Fraction) -> str:
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"


def fmt_raw_fraction(num: int, den: int) -> str:
    if den < 0:
        num, den = -num, -den
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def fmt_decimal_from_scaled(value: int, places: int) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    if places == 0:
        return f"{sign}{value}"
    s = str(value).rjust(places + 1, "0")
    whole = s[:-places]
    frac = s[-places:]
    frac = frac.rstrip("0")
    if not frac:
        return f"{sign}{whole}"
    return f"{sign}{whole}.{frac}"


def parse_decimal_string(s: str) -> Tuple[int, int]:
    """Return scaled integer and decimal places for a finite decimal string."""
    if "." not in s:
        return int(s), 0
    sign = -1 if s.startswith("-") else 1
    t = s[1:] if sign == -1 else s
    whole, frac = t.split(".")
    return sign * int(whole + frac), len(frac)


def decimal_string_from_int(rng: random.Random, min_int: int, max_int: int, places: int) -> str:
    scale = 10**places
    low = min_int * scale
    high = max_int * scale
    value = rng.randint(low, high)
    return fmt_decimal_from_scaled(value, places)


def sqrt_simplify(n: int) -> Tuple[int, int]:
    """Return (outside, inside) where sqrt(n)=outside*sqrt(inside), inside squarefree-ish."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0, 1
    outside = 1
    inside = n
    p = 2
    while p * p <= inside:
        while inside % (p * p) == 0:
            outside *= p
            inside //= p * p
        p += 1
    return outside, inside


def fmt_radical(outside: int, inside: int) -> str:
    if outside == 0:
        return "0"
    if inside == 1:
        return str(outside)
    if outside == 1:
        return f"sqrt({inside})"
    return f"{outside}sqrt({inside})"


NEG_INF = "-∞"
POS_INF = "+∞"


def fmt_value(v) -> str:
    """Render an int or Fraction for use inside answers/intervals."""
    if isinstance(v, Fraction):
        return fmt_fraction(v)
    return str(v)


def fmt_interval(low, high, low_open: bool = True, high_open: bool = True) -> str:
    """Render a single interval. ``None`` endpoints mean ±infinity (always open)."""
    lb = "(" if (low is None or low_open) else "["
    rb = ")" if (high is None or high_open) else "]"
    ls = NEG_INF if low is None else fmt_value(low)
    hs = POS_INF if high is None else fmt_value(high)
    return f"{lb}{ls}, {hs}{rb}"


def fmt_union(parts: Sequence[str]) -> str:
    return " ∪ ".join(parts)


def fmt_point_set(value) -> str:
    return f"{{{fmt_value(value)}}}"


def ordinal(n: int) -> str:
    """Return the ordinal string for a positive integer (1st, 2nd, 3rd, ...)."""
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    last = n % 10
    if last == 1:
        return f"{n}st"
    if last == 2:
        return f"{n}nd"
    if last == 3:
        return f"{n}rd"
    return f"{n}th"


def product_text(values: Sequence[int]) -> str:
    return "×".join(paren_if_negative(v) for v in values)


# ---------------------------------------------------------------------------
# Question template rotation — prevents overfit to specific prefix phrasing.
# ---------------------------------------------------------------------------


def pick_template(rng: random.Random, *variants: str) -> str:
    """Pick one of several semantically-equivalent question templates.

    Usage in a generator::

        q = pick_template(rng,
            "Compute {a}+{b}.",
            "Find {a}+{b}.",
            "What is {a}+{b}?",
            "Evaluate the sum {a}+{b}.",
        ).format(a=a, b=b)
    """
    return rng.choice(list(variants))


# Common synonym groups for quick import by domain generators.
SYN_COMPUTE = (
    "Compute {expr}.",
    "Find {expr}.",
    "Calculate {expr}.",
    "Evaluate {expr}.",
    "What is {expr}?",
    "Determine {expr}.",
)

SYN_SOLVE = (
    "Solve {eq} for x.",
    "Find x such that {eq}.",
    "Find the value of x for which {eq}.",
    "Determine x in {eq}.",
    "What is the solution to {eq}?",
)

SYN_FACTOR = (
    "Factor {expr}.",
    "Factorise {expr}.",
    "Write {expr} as a product of binomials.",
    "Find the factorisation of {expr}.",
    "Decompose {expr} into factors.",
)

SYN_EXPAND = (
    "Expand {expr}.",
    "Multiply out {expr}.",
    "Write {expr} in expanded form.",
    "Fully expand {expr}.",
    "Distribute and simplify {expr}.",
)

SYN_SIMPLIFY = (
    "Simplify {expr}.",
    "Reduce {expr} to simplest form.",
    "Write {expr} in simplest terms.",
    "Fully simplify {expr}.",
)

SYN_EVALUATE = (
    "Evaluate {expr}.",
    "Compute {expr}.",
    "Find the value of {expr}.",
    "What is the result of {expr}?",
    "Work out {expr}.",
)

SYN_FIND_AREA = (
    "Find the area of {shape}.",
    "Calculate the area of {shape}.",
    "What is the area of {shape}?",
    "Determine the area of {shape}.",
)

SYN_FIND_DISTANCE = (
    "Find the distance between {a} and {b}.",
    "Calculate the distance from {a} to {b}.",
    "What is the distance between {a} and {b}?",
    "How far is it from {a} to {b}?",
    "Determine the distance separating {a} and {b}.",
)

SYN_DIFFERENTIATE = (
    "Differentiate f(x) = {expr}.",
    "Find f'(x) for f(x) = {expr}.",
    "Compute the derivative of f(x) = {expr}.",
    "Find the derivative of {expr}.",
    "Determine d/dx of {expr}.",
)

SYN_FIND_DOMAIN = (
    "Find the domain of {expr}.",
    "Determine the domain of {expr}.",
    "What is the domain of {expr}?",
    "State the domain of {expr}.",
)

SYN_CONVERT = (
    "Convert {a} to {b}.",
    "Write {a} as {b}.",
    "Express {a} in {b}.",
    "Change {a} into {b}.",
)


def sum_text(values: Sequence[int]) -> str:
    if not values:
        return "0"
    text = str(values[0])
    for v in values[1:]:
        text = fmt_add(text, v)
    return text
