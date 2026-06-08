"""arithmetic_core domain (design.md sec 1, 9, 10, 11).

Integer add/sub/mul/div with explicit carry/borrow/partial-product/long-division
steps, fractions, decimals, powers, radicals, order of operations, sign rules,
plus gcd/lcm/prime-factorization and percent/proportion basics.

Every generator returns a fully verified Sample with a structured trace.
"""

from __future__ import annotations

import math
import random
from decimal import Decimal
from fractions import Fraction
from typing import Any, Dict, List, Sequence, Tuple

from mathgen.config import Difficulty, GenConfig, pick_difficulty
from mathgen.core import Sample, TraceStep, make_sample
from mathgen.formatting import (
    decimal_string_from_int,
    fmt_add,
    fmt_decimal_from_scaled,
    fmt_fraction,
    fmt_mul,
    fmt_radical,
    fmt_raw_fraction,
    fmt_sub,
    ordinal,
    paren_if_negative,
    parse_decimal_string,
    place_name,
    product_text,
    sqrt_simplify,
    sum_text,
)


def simplify_step_text(raw_num: int, raw_den: int, result: Fraction) -> str:
    """Render the final 'simplify' step, avoiding the degenerate 'Simplify X to X.'

    When ``raw_num/raw_den`` is already in lowest terms the wording says so
    instead of claiming to simplify a fraction to itself.
    """
    raw_str = fmt_raw_fraction(raw_num, raw_den)
    res_str = fmt_fraction(result)
    if raw_str == res_str:
        if result.denominator == 1:
            return f"{raw_str} is already a whole number, so the result is {res_str}."
        return f"The fraction {raw_str} is already in lowest terms, so the result is {res_str}."
    return f"Simplify {raw_str} to {res_str}."


# -----------------------------------------------------------------------------
# Domain-local sampling helpers
# -----------------------------------------------------------------------------


def randint_digits(rng: random.Random, digits: int) -> int:
    if digits <= 1:
        return rng.randint(0, 9)
    return rng.randint(10 ** (digits - 1), 10**digits - 1)


def count_addition_carries(a: int, b: int) -> int:
    carry = 0
    count = 0
    aa, bb = a, b
    while aa > 0 or bb > 0:
        s = aa % 10 + bb % 10 + carry
        if s >= 10:
            count += 1
            carry = 1
        else:
            carry = 0
        aa //= 10
        bb //= 10
    return count


def count_subtraction_borrows(a: int, b: int) -> int:
    if a < b:
        a, b = b, a
    top = [int(c) for c in str(a)][::-1]
    bot = [int(c) for c in str(b)][::-1]
    bot += [0] * (len(top) - len(bot))
    count = 0
    for i in range(len(bot)):
        if top[i] < bot[i]:
            j = i + 1
            while j < len(top) and top[j] == 0:
                j += 1
            if j >= len(top):
                break
            top[j] -= 1
            for k in range(j - 1, i, -1):
                top[k] = 9
            top[i] += 10
            count += 1
        top[i] -= bot[i]
    return count


def choose_fraction(rng: random.Random, max_num: int = 12, max_den: int = 12, proper: bool = False) -> Fraction:
    den = rng.randint(2, max_den)
    if proper:
        num = rng.randint(1, den - 1)
    else:
        num = rng.randint(1, max_num)
    if rng.random() < 0.25:
        num *= -1
    return Fraction(num, den)


def raw_fraction_from_fraction(fr: Fraction, rng: random.Random, max_scale: int = 5) -> Tuple[int, int]:
    scale = rng.randint(1, max_scale)
    return fr.numerator * scale, fr.denominator * scale


def random_squarefreeish(rng: random.Random, candidates: Sequence[int] = (2, 3, 5, 6, 7, 10, 11, 13, 14, 15)) -> int:
    return rng.choice(list(candidates))


# -----------------------------------------------------------------------------
# Integer algorithms
# -----------------------------------------------------------------------------


def gen_integer_addition_carry(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    digits = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    min_carries = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1, Difficulty.HARD: 2}[diff]

    for _ in range(10_000):
        a = randint_digits(rng, digits)
        b = randint_digits(rng, rng.choice([digits - 1, digits]))
        if count_addition_carries(a, b) >= min_carries:
            break
    else:
        a, b = 478, 365

    trace: List[TraceStep] = [
        TraceStep(
            op="align_digits",
            text=f"Align {a} and {b} by place value, then add from right to left.",
            meta={"a": a, "b": b},
        )
    ]
    aa = [int(c) for c in str(a)][::-1]
    bb = [int(c) for c in str(b)][::-1]
    m = max(len(aa), len(bb))
    carry = 0
    out: List[int] = []
    carry_count = 0
    for i in range(m):
        da = aa[i] if i < len(aa) else 0
        db = bb[i] if i < len(bb) else 0
        incoming = carry
        s = da + db + incoming
        digit = s % 10
        carry = s // 10
        out.append(digit)
        parts = f"{da}+{db}" + (f"+{incoming}" if incoming else "")
        if carry:
            carry_count += 1
            text = f"At the {place_name(i)} place: {parts}={s}, so write {digit} and carry {carry} to the next place."
        else:
            text = f"At the {place_name(i)} place: {parts}={s}, so write {digit} with no carry."
        trace.append(
            TraceStep(
                op="add_digit",
                text=text,
                meta={"place": i, "a_digit": da, "b_digit": db, "incoming_carry": incoming, "sum": s, "write": digit, "carry": carry},
            )
        )
    if carry:
        out.append(carry)
        trace.append(TraceStep(op="final_carry", text=f"There is a final carry {carry}, so put it at the front.", meta={"carry": carry}))
    result = a + b
    trace.append(TraceStep(op="finish", text=f"Therefore, {a}+{b}={result}.", after=str(result)))
    return make_sample(
        "arithmetic.integer_addition_carry",
        f"Compute {a}+{b}.",
        trace,
        str(result),
        {"a": a, "b": b, "carry_count": carry_count, "difficulty": diff},
        verified=(int("".join(map(str, out[::-1]))) == result),
    )


def gen_integer_add_many(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    count = {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff]
    digits = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    nums = [randint_digits(rng, rng.choice([digits - 1, digits])) for _ in range(count)]
    result = sum(nums)

    running = nums[0]
    trace: List[TraceStep] = [TraceStep(op="start_running_sum", text=f"Add the numbers left to right. Start with {nums[0]}.", meta={"running": running})]
    for t in nums[1:]:
        new_running = running + t
        trace.append(
            TraceStep(
                op="add_term",
                text=f"Add {t}: {fmt_add(running, t)}={new_running}.",
                meta={"term": t, "running_before": running, "running_after": new_running},
            )
        )
        running = new_running
    trace.append(TraceStep(op="finish", text=f"Therefore, {'+'.join(map(str, nums))}={result}.", after=str(result)))
    return make_sample(
        "arithmetic.integer_add_many",
        f"Compute {'+'.join(map(str, nums))}.",
        trace,
        str(result),
        {"numbers": nums, "difficulty": diff},
        verified=(result == sum(nums)),
    )


def gen_integer_subtraction_borrow(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    digits = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    min_borrows = {Difficulty.EASY: 1, Difficulty.MEDIUM: 1, Difficulty.HARD: 2}[diff]

    for _ in range(10_000):
        a = randint_digits(rng, digits)
        b = randint_digits(rng, rng.choice([digits - 1, digits]))
        if a < b:
            a, b = b, a
        if count_subtraction_borrows(a, b) >= min_borrows:
            break
    else:
        a, b = 1000, 376

    original_a, original_b = a, b
    top = [int(c) for c in str(a)][::-1]
    bot = [int(c) for c in str(b)][::-1]
    bot += [0] * (len(top) - len(bot))
    trace: List[TraceStep] = [TraceStep(op="align_digits", text=f"Align {a} and {b} by place value, then subtract from right to left.")]
    out: List[int] = []
    borrow_count = 0
    for i in range(len(top)):
        before_digit = top[i]
        sub_digit = bot[i]
        if before_digit < sub_digit:
            j = i + 1
            while j < len(top) and top[j] == 0:
                j += 1
            if j >= len(top):
                raise RuntimeError("invalid subtraction state")
            borrow_count += 1
            if j == i + 1:
                trace.append(
                    TraceStep(
                        op="borrow",
                        text=(
                            f"At the {place_name(i)} place, {before_digit} is too small to subtract {sub_digit}. "
                            f"Borrow 1 from the {place_name(j)} place, so the current digit becomes {before_digit + 10}."
                        ),
                        meta={"place": i, "borrow_from": j},
                    )
                )
            else:
                zero_places = ", ".join(place_name(k) for k in range(i + 1, j))
                trace.append(
                    TraceStep(
                        op="borrow_chain",
                        text=(
                            f"At the {place_name(i)} place, {before_digit} is too small to subtract {sub_digit}. "
                            f"Borrow from the {place_name(j)} place through the zero place(s) {zero_places}; "
                            f"the current digit becomes {before_digit + 10}."
                        ),
                        meta={"place": i, "borrow_from": j, "through_zero_places": list(range(i + 1, j))},
                    )
                )
            top[j] -= 1
            for k in range(j - 1, i, -1):
                top[k] = 9
            top[i] += 10
        digit = top[i] - sub_digit
        out.append(digit)
        trace.append(
            TraceStep(
                op="subtract_digit",
                text=f"At the {place_name(i)} place: {top[i]}-{sub_digit}={digit}, so write {digit}.",
                meta={"place": i, "top_digit_after_borrow": top[i], "bottom_digit": sub_digit, "write": digit},
            )
        )
    result = original_a - original_b
    result_text = str(result)
    trace.append(TraceStep(op="remove_leading_zeros", text=f"Remove any leading zeros. Therefore, {original_a}-{original_b}={result}."))
    raw = int("".join(map(str, out[::-1])))
    return make_sample(
        "arithmetic.integer_subtraction_borrow",
        f"Compute {original_a}-{original_b}.",
        trace,
        result_text,
        {"a": original_a, "b": original_b, "borrow_count": borrow_count, "difficulty": diff},
        verified=(raw == result),
    )


def gen_integer_mixed_add_sub(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    count = {Difficulty.EASY: 3, Difficulty.MEDIUM: 4, Difficulty.HARD: 5}[diff]
    terms = [rng.randint(-40, 80) for _ in range(count)]
    if terms[0] == 0:
        terms[0] = rng.randint(1, 30)
    expr = sum_text(terms)
    result = sum(terms)
    running = terms[0]
    trace: List[TraceStep] = [
        TraceStep(op="rewrite_signed_sum", text=f"Read the expression as a sum of signed numbers: {', '.join(map(str, terms))}."),
        TraceStep(op="start_running_sum", text=f"Combine them left to right. Start with {terms[0]}.", meta={"running": running}),
    ]
    for t in terms[1:]:
        new_running = running + t
        verb = "Add" if t >= 0 else "Subtract"
        trace.append(
            TraceStep(
                op="combine_term",
                text=f"{verb} {abs(t)}: {fmt_add(running, t)}={new_running}.",
                meta={"term": t, "running_before": running, "running_after": new_running},
            )
        )
        running = new_running
    trace.append(TraceStep(op="finish", text=f"Therefore, {expr}={result}.", after=str(result)))
    return make_sample(
        "arithmetic.integer_mixed_add_sub",
        f"Compute {expr}.",
        trace,
        str(result),
        {"terms": terms, "difficulty": diff},
        verified=(result == sum(terms)),
    )


def multiply_by_digit_trace(a: int, digit: int) -> Tuple[int, str, List[Dict[str, Any]]]:
    carry = 0
    out: List[int] = []
    pieces: List[str] = []
    meta_steps: List[Dict[str, Any]] = []
    for i, ch in enumerate(str(a)[::-1]):
        da = int(ch)
        incoming = carry
        prod = da * digit + incoming
        write = prod % 10
        carry = prod // 10
        out.append(write)
        if carry:
            pieces.append(f"{place_name(i)}: {da}×{digit}" + (f"+{incoming}" if incoming else "") + f"={prod}, write {write}, carry {carry}")
        else:
            pieces.append(f"{place_name(i)}: {da}×{digit}" + (f"+{incoming}" if incoming else "") + f"={prod}, write {write}, carry 0")
        meta_steps.append({"place": i, "a_digit": da, "digit": digit, "incoming_carry": incoming, "product": prod, "write": write, "carry": carry})
    if carry:
        out.append(carry)
        pieces.append(f"final carry {carry} goes to the front")
    value = a * digit
    return value, "; ".join(pieces), meta_steps


def gen_long_multiplication(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a_digits = {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff]
    b_digits = {Difficulty.EASY: 2, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}[diff]
    a = randint_digits(rng, a_digits)
    b = randint_digits(rng, b_digits)
    result = a * b

    trace: List[TraceStep] = [TraceStep(op="decompose_multiplier", text=f"Break the multiplier {b} into place-value digits. Compute partial products for each digit position, then sum them.", meta={"a": a, "b": b})]
    partials: List[int] = []
    for pos, ch in enumerate(str(b)[::-1]):
        digit = int(ch)
        # Compute digit-sub-steps and emit as individual TraceSteps.
        trace.append(TraceStep(op="start_partial", text=f"Partial product for the {place_name(pos)} digit {digit}: compute {a}×{digit}.", meta={"position": pos, "digit": digit}))
        carry = 0
        partial_digits: List[int] = []
        for i, dch in enumerate(str(a)[::-1]):
            da = int(dch)
            incoming = carry
            prod = da * digit + incoming
            write = prod % 10
            carry = prod // 10
            partial_digits.append(write)
            if carry:
                text = f"  {place_name(i)}: {da}×{digit}{' + ' + str(incoming) if incoming else ''} = {prod}, write {write}, carry {carry}"
            else:
                text = f"  {place_name(i)}: {da}×{digit}{' + ' + str(incoming) if incoming else ''} = {prod}, write {write}"
            trace.append(TraceStep(op="multiply_digit", text=text, meta={"place": i, "a_digit": da, "digit": digit, "product": prod, "write": write, "carry": carry}))
        if carry:
            partial_digits.append(carry)
            trace.append(TraceStep(op="final_carry", text=f"  Final carry {carry} goes to the front."))
        partial_raw = int("".join(map(str, partial_digits[::-1])))
        shifted = partial_raw * (10**pos)
        if pos == 0:
            trace.append(TraceStep(op="partial_result", text=f"Partial product for the {place_name(pos)} digit: {partial_raw}.", meta={"raw": partial_raw}))
        else:
            zeros = "zero" if pos == 1 else "zeros"
            trace.append(TraceStep(op="shift_and_result", text=f"Because this digit is in the {place_name(pos)} place, append {pos} {zeros} to {partial_raw}, giving {shifted}.", meta={"raw": partial_raw, "shifted": shifted}))
        partials.append(shifted)
    trace.append(TraceStep(op="sum_partial_products", text=f"Sum the partial products: {' + '.join(map(str, partials))} = {result}.", meta={"partials": partials, "result": result}))
    trace.append(TraceStep(op="finish", text=f"Therefore, {a}×{b}={result}.", after=str(result)))
    return make_sample(
        "arithmetic.long_multiplication",
        f"Compute {a}×{b}.",
        trace,
        str(result),
        {"a": a, "b": b, "partials": partials, "difficulty": diff},
        verified=(sum(partials) == result),
    )


def long_division_steps(n: int, d: int) -> Tuple[int, int, List[TraceStep]]:
    trace: List[TraceStep] = [TraceStep(op="start_long_division", text=f"Use long division, processing the digits of {n} from left to right.")]
    remainder = 0
    quotient_digits: List[int] = []
    started = False
    for idx, ch in enumerate(str(n)):
        digit = int(ch)
        current = remainder * 10 + digit
        trace.append(TraceStep(op="bring_down", text=f"Bring down digit {digit}; the current value is {current}.", meta={"digit_index": idx, "digit": digit, "current": current, "previous_remainder": remainder}))
        if current < d and not started:
            remainder = current
            trace.append(TraceStep(op="skip_leading_zero", text=f"Since {current}<{d} and no quotient digit has been written yet, wait for the next digit.", meta={"current": current, "divisor": d}))
            continue
        q_digit = current // d
        product = q_digit * d
        new_remainder = current - product
        quotient_digits.append(q_digit)
        started = True
        if q_digit == 0:
            text = f"Since {current}<{d}, write 0 in the quotient for this place; 0×{d}=0, so the remainder stays {new_remainder}."
        else:
            text = f"{current}÷{d} gives quotient digit {q_digit}. Multiply back: {q_digit}×{d}={product}. Subtract: {current}-{product}={new_remainder}."
        trace.append(TraceStep(op="quotient_digit", text=text, meta={"current": current, "divisor": d, "quotient_digit": q_digit, "product": product, "new_remainder": new_remainder}))
        remainder = new_remainder
    if not quotient_digits:
        quotient_digits = [0]
    quotient = int("".join(map(str, quotient_digits)))
    return quotient, remainder, trace


def gen_long_division_exact(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    divisor = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 12, Difficulty.HARD: 25}[diff])
    quotient = randint_digits(rng, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff])
    n = divisor * quotient
    q, r, trace = long_division_steps(n, divisor)
    trace.append(TraceStep(op="finish", text=f"The final remainder is {r}, so {n}÷{divisor}={q}."))
    return make_sample(
        "arithmetic.long_division_exact",
        f"Compute {n}÷{divisor}.",
        trace,
        str(q),
        {"dividend": n, "divisor": divisor, "quotient": q, "remainder": r, "difficulty": diff},
        verified=(q == quotient and r == 0 and n // divisor == q),
    )


def gen_long_division_remainder(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    divisor = rng.randint(3, {Difficulty.EASY: 9, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff])
    quotient = randint_digits(rng, {Difficulty.EASY: 2, Difficulty.MEDIUM: 3, Difficulty.HARD: 4}[diff])
    rem = rng.randint(1, divisor - 1)
    n = divisor * quotient + rem
    q, r, trace = long_division_steps(n, divisor)
    trace.append(TraceStep(op="finish", text=f"The final remainder is {r}, so {n}÷{divisor}={q} remainder {r}."))
    answer = f"{q} remainder {r}"
    return make_sample(
        "arithmetic.long_division_remainder",
        f"Compute {n}÷{divisor}, giving quotient and remainder.",
        trace,
        answer,
        {"dividend": n, "divisor": divisor, "quotient": q, "remainder": r, "difficulty": diff},
        verified=(q == n // divisor and r == n % divisor and r > 0),
    )


def gen_long_division_zero_in_quotient(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    divisor = rng.randint(3, {Difficulty.EASY: 9, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff])
    if diff == Difficulty.EASY:
        quotient = rng.choice([101, 102, 105, 201, 204, 302])
    elif diff == Difficulty.MEDIUM:
        quotient = rng.choice([1005, 1012, 1204, 2030, 3006])
    else:
        quotient = rng.choice([10005, 10203, 12004, 20030, 30506])
    n = divisor * quotient
    q, r, trace = long_division_steps(n, divisor)
    trace.append(TraceStep(op="finish", text=f"The quotient contains a zero in the middle. The final result is {n}÷{divisor}={q}."))
    return make_sample(
        "arithmetic.long_division_zero_in_quotient",
        f"Compute {n}÷{divisor}.",
        trace,
        str(q),
        {"dividend": n, "divisor": divisor, "quotient": q, "remainder": r, "difficulty": diff},
        verified=(q == quotient and r == 0),
    )


# -----------------------------------------------------------------------------
# Fractions, decimals, powers, radicals, order of operations
# -----------------------------------------------------------------------------


def gen_fraction_simplification(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base_num = rng.randint(1, {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 50}[diff])
    base_den = rng.randint(2, {Difficulty.EASY: 10, Difficulty.MEDIUM: 30, Difficulty.HARD: 80}[diff])
    base = Fraction(base_num, base_den)
    scale = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 30}[diff])
    num = base.numerator * scale
    den = base.denominator * scale
    g = math.gcd(abs(num), abs(den))
    simplified = Fraction(num, den)
    # Show the GCD derivation, not just the result.
    a_abs, b_abs = abs(num), abs(den)
    if g == 1:
        gcd_text = f"Find gcd({a_abs},{b_abs}). Since they share no common factors, gcd = 1. The fraction is already in lowest terms."
    elif g <= 10:
        gcd_text = f"Find gcd({a_abs},{b_abs}). Both numbers are divisible by {g}, and no larger number divides both, so gcd = {g}."
    else:
        gcd_text = f"Find gcd({a_abs},{b_abs}) using the Euclidean algorithm: {a_abs}÷{b_abs} = {a_abs//b_abs} remainder {a_abs % b_abs}; ... ; so gcd = {g}."
    trace = [
        TraceStep(op="find_gcd", text=gcd_text),
        TraceStep(op="divide_by_gcd", text=f"Divide numerator and denominator by {g}: {num}/{den}=({num}÷{g})/({den}÷{g})={fmt_fraction(simplified)}."),
    ]
    return make_sample(
        "arithmetic.fraction_simplification",
        f"Simplify the fraction {num}/{den}.",
        trace,
        fmt_fraction(simplified),
        {"numerator": num, "denominator": den, "gcd": g, "difficulty": diff},
        verified=(Fraction(num, den) == simplified),
    )


def gen_fraction_add_sub(rng: random.Random, cfg: GenConfig, op: str) -> Sample:
    diff = pick_difficulty(rng, cfg)
    max_den = {Difficulty.EASY: 9, Difficulty.MEDIUM: 15, Difficulty.HARD: 30}[diff]
    f1 = choose_fraction(rng, max_num=max_den, max_den=max_den)
    f2 = choose_fraction(rng, max_num=max_den, max_den=max_den)
    n1, d1 = raw_fraction_from_fraction(f1, rng, max_scale=3)
    n2, d2 = raw_fraction_from_fraction(f2, rng, max_scale=3)
    lcm = abs(d1 * d2) // math.gcd(d1, d2)
    g = math.gcd(d1, d2)
    m1 = lcm // d1
    m2 = lcm // d2
    e1 = n1 * m1
    e2 = n2 * m2
    if op == "+":
        raw_num = e1 + e2
        result = Fraction(n1, d1) + Fraction(n2, d2)
        source = "arithmetic.fraction_addition"
        user = f"Compute {fmt_raw_fraction(n1, d1)} + {paren_if_negative(fmt_raw_fraction(n2, d2))}."
        combine_text = f"Add the numerators: {fmt_add(e1, e2)}={raw_num}, so the result before simplification is {fmt_raw_fraction(raw_num, lcm)}."
    else:
        raw_num = e1 - e2
        result = Fraction(n1, d1) - Fraction(n2, d2)
        source = "arithmetic.fraction_subtraction"
        user = f"Compute {fmt_raw_fraction(n1, d1)} - {paren_if_negative(fmt_raw_fraction(n2, d2))}."
        combine_text = f"Subtract the numerators: {fmt_sub(e1, e2)}={raw_num}, so the result before simplification is {fmt_raw_fraction(raw_num, lcm)}."
    # Build the LCM explanation depending on whether denominators share a factor.
    if g == 1:
        lcm_text = f"The denominators {d1} and {d2} are coprime, so the common denominator is their product: lcm = {d1}×{d2} = {lcm}."
    else:
        lcm_text = f"Find the common denominator: lcm({d1},{d2}) = {d1}×{d2}÷gcd({d1},{d2}) = {d1}×{d2}÷{g} = {lcm}."
    trace = [
        TraceStep(op="find_common_denominator", text=lcm_text),
        TraceStep(op="convert_first_fraction", text=f"Convert {fmt_raw_fraction(n1, d1)} to denominator {lcm}: multiply numerator and denominator by {m1}, giving {e1}/{lcm}."),
        TraceStep(op="convert_second_fraction", text=f"Convert {fmt_raw_fraction(n2, d2)} to denominator {lcm}: multiply numerator and denominator by {m2}, giving {e2}/{lcm}."),
        TraceStep(op="combine_numerators", text=combine_text),
        TraceStep(op="simplify_fraction", text=simplify_step_text(raw_num, lcm, result)),
    ]
    expected = Fraction(n1, d1) + Fraction(n2, d2) if op == "+" else Fraction(n1, d1) - Fraction(n2, d2)
    return make_sample(
        source,
        user,
        trace,
        fmt_fraction(result),
        {"n1": n1, "d1": d1, "n2": n2, "d2": d2, "lcm": lcm, "difficulty": diff},
        verified=(result == expected),
    )


def gen_fraction_addition(rng: random.Random, cfg: GenConfig) -> Sample:
    return gen_fraction_add_sub(rng, cfg, op="+")


def gen_fraction_subtraction(rng: random.Random, cfg: GenConfig) -> Sample:
    return gen_fraction_add_sub(rng, cfg, op="-")


def gen_fraction_multiplication(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    f1 = choose_fraction(rng, max_num=12, max_den=12)
    f2 = choose_fraction(rng, max_num=12, max_den=12)
    n1, d1 = raw_fraction_from_fraction(f1, rng, max_scale=3)
    n2, d2 = raw_fraction_from_fraction(f2, rng, max_scale=3)
    raw_num = n1 * n2
    raw_den = d1 * d2
    result = Fraction(raw_num, raw_den)
    trace = [
        TraceStep(op="multiply_numerators", text=f"Multiply the numerators: {fmt_mul(n1, n2)}={raw_num}."),
        TraceStep(op="multiply_denominators", text=f"Multiply the denominators: {fmt_mul(d1, d2)}={raw_den}."),
        TraceStep(op="simplify_fraction", text=simplify_step_text(raw_num, raw_den, result)),
    ]
    return make_sample(
        "arithmetic.fraction_multiplication",
        f"Compute {fmt_raw_fraction(n1, d1)} × {paren_if_negative(fmt_raw_fraction(n2, d2))}.",
        trace,
        fmt_fraction(result),
        {"n1": n1, "d1": d1, "n2": n2, "d2": d2, "difficulty": diff},
        verified=(result == Fraction(n1, d1) * Fraction(n2, d2)),
    )


def gen_fraction_division(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    f1 = choose_fraction(rng, max_num=12, max_den=12)
    f2 = choose_fraction(rng, max_num=12, max_den=12)
    if f2 == 0:
        f2 = Fraction(1, 2)
    n1, d1 = raw_fraction_from_fraction(f1, rng, max_scale=3)
    n2, d2 = raw_fraction_from_fraction(f2, rng, max_scale=3)
    raw_num = n1 * d2
    raw_den = d1 * n2
    result = Fraction(raw_num, raw_den)
    trace = [
        TraceStep(op="take_reciprocal", text=f"To divide by {fmt_raw_fraction(n2, d2)}, multiply by its reciprocal {fmt_raw_fraction(d2, n2)}."),
        TraceStep(op="multiply_numerators", text=f"Multiply the numerators: {fmt_mul(n1, d2)}={raw_num}."),
        TraceStep(op="multiply_denominators", text=f"Multiply the denominators: {fmt_mul(d1, n2)}={raw_den}."),
        TraceStep(op="simplify_fraction", text=simplify_step_text(raw_num, raw_den, result)),
    ]
    return make_sample(
        "arithmetic.fraction_division",
        f"Compute {fmt_raw_fraction(n1, d1)} ÷ {paren_if_negative(fmt_raw_fraction(n2, d2))}.",
        trace,
        fmt_fraction(result),
        {"n1": n1, "d1": d1, "n2": n2, "d2": d2, "difficulty": diff},
        verified=(result == Fraction(n1, d1) / Fraction(n2, d2)),
    )


def gen_mixed_number_to_improper(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    whole = rng.randint(1, {Difficulty.EASY: 5, Difficulty.MEDIUM: 12, Difficulty.HARD: 30}[diff])
    den = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff])
    # Keep the fractional part in lowest terms; then whole*den+num is coprime to
    # den as well, so the improper fraction needs no hidden simplification step.
    num = rng.randint(1, den - 1)
    while math.gcd(num, den) != 1:
        num = rng.randint(1, den - 1)
    improper_num = whole * den + num
    result = Fraction(improper_num, den)
    trace = [
        TraceStep(op="multiply_whole_by_denominator", text=f"Multiply the whole number by the denominator: {whole}×{den}={whole * den}."),
        TraceStep(op="add_numerator", text=f"Add the numerator: {whole * den}+{num}={improper_num}."),
        TraceStep(op="write_improper_fraction", text=f"Keep the denominator {den}, so the improper fraction is {improper_num}/{den}."),
    ]
    return make_sample(
        "arithmetic.mixed_number_to_improper",
        f"Convert {whole} {num}/{den} to an improper fraction.",
        trace,
        fmt_fraction(result),
        {"whole": whole, "numerator": num, "denominator": den, "difficulty": diff},
        verified=(result == Fraction(whole * den + num, den)),
    )


def gen_decimal_add_sub(rng: random.Random, cfg: GenConfig, op: str) -> Sample:
    diff = pick_difficulty(rng, cfg)
    max_places = {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}[diff]
    p1 = rng.randint(1, max_places)
    p2 = rng.randint(1, max_places)
    a_str = decimal_string_from_int(rng, 1, {Difficulty.EASY: 20, Difficulty.MEDIUM: 100, Difficulty.HARD: 500}[diff], p1)
    b_str = decimal_string_from_int(rng, 1, {Difficulty.EASY: 20, Difficulty.MEDIUM: 100, Difficulty.HARD: 500}[diff], p2)
    a_scaled, ap = parse_decimal_string(a_str)
    b_scaled, bp = parse_decimal_string(b_str)
    scale_places = max(ap, bp)
    a_common = a_scaled * 10 ** (scale_places - ap)
    b_common = b_scaled * 10 ** (scale_places - bp)
    if op == "+":
        res_scaled = a_common + b_common
        source = "arithmetic.decimal_addition"
        user = f"Compute {a_str} + {b_str}."
        combine = f"Add as integers at that scale: {a_common}+{b_common}={res_scaled}."
    else:
        if a_common < b_common:
            a_str, b_str = b_str, a_str
            a_scaled, ap = parse_decimal_string(a_str)
            b_scaled, bp = parse_decimal_string(b_str)
            scale_places = max(ap, bp)
            a_common = a_scaled * 10 ** (scale_places - ap)
            b_common = b_scaled * 10 ** (scale_places - bp)
        res_scaled = a_common - b_common
        source = "arithmetic.decimal_subtraction"
        user = f"Compute {a_str} - {b_str}."
        combine = f"Subtract as integers at that scale: {a_common}-{b_common}={res_scaled}."
    answer = fmt_decimal_from_scaled(res_scaled, scale_places)
    trace = [
        TraceStep(op="align_decimals", text=f"Align decimal places. Use {scale_places} decimal place(s) for both numbers."),
        TraceStep(op="scale_to_integers", text=f"At this scale, {a_str} becomes {a_common} and {b_str} becomes {b_common}."),
        TraceStep(op="compute_scaled", text=combine),
        TraceStep(op="place_decimal", text=f"Put the decimal point back {scale_places} place(s) from the right, giving {answer}."),
    ]
    expected = Decimal(a_str) + Decimal(b_str) if op == "+" else Decimal(a_str) - Decimal(b_str)
    return make_sample(
        source,
        user,
        trace,
        answer,
        {"a": a_str, "b": b_str, "decimal_places": scale_places, "difficulty": diff},
        verified=(Decimal(answer) == expected),
    )


def gen_decimal_addition(rng: random.Random, cfg: GenConfig) -> Sample:
    return gen_decimal_add_sub(rng, cfg, op="+")


def gen_decimal_subtraction(rng: random.Random, cfg: GenConfig) -> Sample:
    return gen_decimal_add_sub(rng, cfg, op="-")


def gen_decimal_multiplication(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    p1 = rng.randint(1, {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 2}[diff])
    p2 = rng.randint(1, {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}[diff])
    a_str = decimal_string_from_int(rng, 1, {Difficulty.EASY: 20, Difficulty.MEDIUM: 80, Difficulty.HARD: 200}[diff], p1)
    b_str = decimal_string_from_int(rng, 1, {Difficulty.EASY: 20, Difficulty.MEDIUM: 80, Difficulty.HARD: 200}[diff], p2)
    a_int, ap = parse_decimal_string(a_str)
    b_int, bp = parse_decimal_string(b_str)
    raw = a_int * b_int
    places = ap + bp
    answer = fmt_decimal_from_scaled(raw, places)
    trace = [
        TraceStep(op="ignore_decimal_points", text=f"Ignore the decimal points first: {a_str} becomes {abs(a_int)}, and {b_str} becomes {abs(b_int)}."),
        TraceStep(op="multiply_integers", text=f"Multiply the integers: {abs(a_int)}×{abs(b_int)}={abs(raw)}."),
        TraceStep(op="count_decimal_places", text=f"The factors have {ap}+{bp}={places} decimal place(s) total."),
        TraceStep(op="place_decimal", text=f"Place the decimal point {places} place(s) from the right, giving {answer}."),
    ]
    return make_sample(
        "arithmetic.decimal_multiplication",
        f"Compute {a_str} × {b_str}.",
        trace,
        answer,
        {"a": a_str, "b": b_str, "decimal_places_total": places, "difficulty": diff},
        verified=(Decimal(answer) == Decimal(a_str) * Decimal(b_str)),
    )


def gen_decimal_division_by_integer(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    divisor = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 15, Difficulty.HARD: 25}[diff])
    places = rng.randint(1, {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}[diff])
    quotient_scaled = rng.randint(10, {Difficulty.EASY: 200, Difficulty.MEDIUM: 2000, Difficulty.HARD: 10000}[diff])
    dividend_scaled = quotient_scaled * divisor
    dividend = fmt_decimal_from_scaled(dividend_scaled, places)
    quotient = fmt_decimal_from_scaled(quotient_scaled, places)
    trace = [
        TraceStep(op="convert_to_scaled_integer", text=f"Treat {dividend} as the integer {dividend_scaled} with {places} decimal place(s)."),
        TraceStep(op="divide_scaled_integer", text=f"Divide the scaled integer: {dividend_scaled}÷{divisor}={quotient_scaled}."),
        TraceStep(op="restore_decimal", text=f"Restore {places} decimal place(s), giving {quotient}."),
    ]
    return make_sample(
        "arithmetic.decimal_division_by_integer",
        f"Compute {dividend} ÷ {divisor}.",
        trace,
        quotient,
        {"dividend": dividend, "divisor": divisor, "decimal_places": places, "difficulty": diff},
        verified=(Decimal(quotient) == Decimal(dividend) / Decimal(divisor)),
    )


def gen_powers(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base_abs = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 9, Difficulty.HARD: 12}[diff])
    base = -base_abs if rng.random() < 0.35 else base_abs
    exponent = rng.randint(0, {Difficulty.EASY: 4, Difficulty.MEDIUM: 5, Difficulty.HARD: 6}[diff])
    result = base**exponent
    if exponent == 0:
        trace = [
            TraceStep(op="state_rule", text="Recall the zero exponent rule: any nonzero number raised to the power 0 equals 1.", meta={"rule": "a^0 = 1 for a ≠ 0"}),
            TraceStep(op="apply_rule", text=f"Here the base is {paren_if_negative(base)}, which is nonzero."),
            TraceStep(op="finish", text=f"So {paren_if_negative(base)}^0 = 1.", after="1"),
        ]
    elif exponent == 1:
        trace = [
            TraceStep(op="state_rule", text=f"Any number to the power 1 is itself: {paren_if_negative(base)}^1 = {base}."),
            TraceStep(op="finish", text=f"So {paren_if_negative(base)}^1 = {base}.", after=str(base)),
        ]
    else:
        factors = [base] * exponent
        trace = [
            TraceStep(op="expand_power", text=f"{paren_if_negative(base)}^{exponent} means multiplying {exponent} copies of {paren_if_negative(base)}: {product_text(factors)}."),
            TraceStep(op="multiply_factors", text=f"Compute the product {product_text(factors)}={result}."),
        ]
    return make_sample(
        "arithmetic.powers",
        f"Compute {paren_if_negative(base)}^{exponent}.",
        trace,
        str(result),
        {"base": base, "exponent": exponent, "difficulty": diff},
        verified=(result == base**exponent),
    )


def gen_radical_simplification(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    outside = rng.randint(2, {Difficulty.EASY: 6, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    inside = random_squarefreeish(rng)
    n = outside * outside * inside
    simp_out, simp_in = sqrt_simplify(n)
    answer = fmt_radical(simp_out, simp_in)
    trace = [
        TraceStep(op="factor_square", text=f"Factor {n} as {outside}^2×{inside}."),
        TraceStep(op="split_radical", text=f"sqrt({n})=sqrt({outside}^2×{inside})={outside}sqrt({inside})."),
        TraceStep(op="finish", text=f"Thus sqrt({n}) simplifies to {answer}."),
    ]
    return make_sample(
        "arithmetic.radical_simplification",
        f"Simplify sqrt({n}).",
        trace,
        answer,
        {"n": n, "outside": simp_out, "inside": simp_in, "difficulty": diff},
        verified=(simp_out == outside and simp_in == inside),
    )


def gen_order_of_operations_basic(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(1, 9)
    b = rng.randint(1, 9)
    c = rng.randint(2, 9)
    d = rng.randint(2, {Difficulty.EASY: 4, Difficulty.MEDIUM: 6, Difficulty.HARD: 9}[diff])
    power = d * d
    mult = b * c
    result = a + mult - power
    expr = f"{a} + {b} × {c} - {d}^2"
    trace = [
        TraceStep(op="power_first", text=f"Compute the power first: {d}^2={power}."),
        TraceStep(op="multiplication_next", text=f"Compute the multiplication: {b}×{c}={mult}."),
        TraceStep(op="add_subtract_left_to_right", text=f"Now evaluate {a}+{mult}-{power}={result}."),
    ]
    return make_sample(
        "arithmetic.order_of_operations_basic",
        f"Evaluate {expr}.",
        trace,
        str(result),
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(result == a + b * c - d**2),
    )


def gen_order_of_operations_parentheses(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(1, 12)
    b = rng.randint(1, 12)
    c = rng.randint(2, 10)
    d = rng.randint(1, 9)
    inner = a + b
    mult = inner * c
    result = mult - d
    expr = f"({a} + {b}) × {c} - {d}"
    trace = [
        TraceStep(op="parentheses_first", text=f"Compute inside the parentheses first: {a}+{b}={inner}."),
        TraceStep(op="multiply", text=f"Then multiply: {inner}×{c}={mult}."),
        TraceStep(op="subtract", text=f"Finally subtract: {mult}-{d}={result}."),
    ]
    return make_sample(
        "arithmetic.order_of_operations_parentheses",
        f"Evaluate {expr}.",
        trace,
        str(result),
        {"a": a, "b": b, "c": c, "d": d, "difficulty": diff},
        verified=(result == (a + b) * c - d),
    )


def gen_sign_rules_multiplication(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 80}[diff])
    b = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 80}[diff])
    if rng.random() < 0.5:
        a = -a
    if rng.random() < 0.5:
        b = -b
    result = a * b
    sign_text = "positive" if result > 0 else "negative"
    trace = [
        TraceStep(op="determine_sign", text=f"A product is positive if the factors have the same sign and negative if they have different signs. Here the result is {sign_text}."),
        TraceStep(op="multiply_absolute_values", text=f"Multiply the absolute values: {abs(a)}×{abs(b)}={abs(result)}."),
        TraceStep(op="apply_sign", text=f"Apply the sign, giving {result}."),
    ]
    return make_sample(
        "arithmetic.sign_rules_multiplication",
        f"Compute {fmt_mul(a, b)}.",
        trace,
        str(result),
        {"a": a, "b": b, "difficulty": diff},
        verified=(result == a * b),
    )


# -----------------------------------------------------------------------------
# Number theory and ratio/percent basics
# -----------------------------------------------------------------------------


def euclidean_trace(a: int, b: int) -> Tuple[int, List[TraceStep]]:
    aa, bb = max(abs(a), abs(b)), min(abs(a), abs(b))
    trace: List[TraceStep] = [TraceStep(op="start_euclidean_algorithm", text=f"Use the Euclidean algorithm on {aa} and {bb}.")]
    while bb:
        q, r = divmod(aa, bb)
        trace.append(TraceStep(op="euclidean_step", text=f"{aa}={bb}×{q}+{r}.", meta={"a": aa, "b": bb, "quotient": q, "remainder": r}))
        aa, bb = bb, r
    trace.append(TraceStep(op="finish_gcd", text=f"The last nonzero remainder is {aa}, so the gcd is {aa}."))
    return aa, trace


def gen_gcd_euclidean_algorithm(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    base = rng.randint(2, {Difficulty.EASY: 12, Difficulty.MEDIUM: 30, Difficulty.HARD: 80}[diff])
    m = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 60}[diff])
    n = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 20, Difficulty.HARD: 60}[diff])
    while math.gcd(m, n) != 1:
        m = rng.randint(2, 60)
        n = rng.randint(2, 60)
    a, b = base * m, base * n
    gcd_val, trace = euclidean_trace(a, b)
    return make_sample(
        "number_theory.gcd_euclidean_algorithm",
        f"Find gcd({a}, {b}) using the Euclidean algorithm.",
        trace,
        str(gcd_val),
        {"a": a, "b": b, "difficulty": diff},
        verified=(gcd_val == math.gcd(a, b)),
    )


def gen_lcm_using_gcd(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(2, {Difficulty.EASY: 30, Difficulty.MEDIUM: 80, Difficulty.HARD: 200}[diff])
    b = rng.randint(2, {Difficulty.EASY: 30, Difficulty.MEDIUM: 80, Difficulty.HARD: 200}[diff])
    gcd_val = math.gcd(a, b)
    lcm = abs(a * b) // gcd_val
    trace = [
        TraceStep(op="find_gcd", text=f"First find gcd({a},{b})={gcd_val}."),
        TraceStep(op="apply_lcm_formula", text=f"Use lcm(a,b)=|ab|/gcd(a,b): lcm({a},{b})=({a}×{b})/{gcd_val}={lcm}."),
    ]
    return make_sample(
        "number_theory.lcm_using_gcd",
        f"Find lcm({a}, {b}).",
        trace,
        str(lcm),
        {"a": a, "b": b, "gcd": gcd_val, "difficulty": diff},
        verified=(lcm == abs(a * b) // math.gcd(a, b)),
    )


def prime_factorization(n: int) -> List[Tuple[int, int]]:
    factors: List[Tuple[int, int]] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            count = 0
            while n % d == 0:
                n //= d
                count += 1
            factors.append((d, count))
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append((n, 1))
    return factors


def fmt_factorization(factors: List[Tuple[int, int]]) -> str:
    parts = []
    for p, e in factors:
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{e}")
    return " × ".join(parts)


def gen_prime_factorization(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    n = rng.randint(12, {Difficulty.EASY: 120, Difficulty.MEDIUM: 500, Difficulty.HARD: 2000}[diff])
    factors = prime_factorization(n)
    answer = fmt_factorization(factors)
    trace: List[TraceStep] = [TraceStep(op="start_factorization", text=f"Divide {n} by prime numbers from small to large.")]
    remaining = n
    for p, e in factors:
        old = remaining
        for _ in range(e):
            remaining //= p
        trace.append(TraceStep(op="extract_prime_power", text=f"{old} is divisible by {p}^{e}, leaving {remaining}."))
    trace.append(TraceStep(op="finish_factorization", text=f"Therefore, {n}={answer}."))
    prod = 1
    for p, e in factors:
        prod *= p**e
    return make_sample(
        "number_theory.prime_factorization",
        f"Find the prime factorization of {n}.",
        trace,
        answer,
        {"n": n, "factors": factors, "difficulty": diff},
        verified=(prod == n),
    )


def gen_percent_to_fraction_decimal(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    percent = rng.choice([5, 10, 12, 20, 25, 30, 40, 50, 60, 75, 80, 125, 150]) if diff != Difficulty.HARD else rng.randint(1, 250)
    frac = Fraction(percent, 100)
    dec = Decimal(percent) / Decimal(100)
    dec_str = format(dec.normalize(), "f")
    trace = [
        TraceStep(op="percent_means_per_100", text=f"{percent}% means {percent} per 100, so {percent}%={percent}/100."),
        TraceStep(op="simplify_fraction", text=f"Simplify {percent}/100 to {fmt_fraction(frac)}."),
        TraceStep(op="convert_to_decimal", text=f"Divide by 100 to move the decimal point two places left, giving {dec_str}."),
        TraceStep(op="finish", text=f"So {percent}% equals the fraction {fmt_fraction(frac)} and the decimal {dec_str}, i.e. {fmt_fraction(frac)}, {dec_str}."),
    ]
    answer = f"{fmt_fraction(frac)}, {dec_str}"
    return make_sample(
        "ratio_percent.percent_to_fraction_decimal",
        f"Convert {percent}% to a fraction and a decimal.",
        trace,
        answer,
        {"percent": percent, "difficulty": diff},
        verified=(frac == Fraction(percent, 100)),
    )


def gen_percent_change(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    original = rng.randint(20, {Difficulty.EASY: 100, Difficulty.MEDIUM: 300, Difficulty.HARD: 1000}[diff])
    percent = rng.choice([5, 10, 12, 15, 20, 25, 30, 40, 50])
    direction = rng.choice(["increase", "decrease"])
    delta = Fraction(original * percent, 100)
    if direction == "increase":
        final = Fraction(original) + delta
        trace_text = f"An increase of {percent}% means adding {percent}% of {original}."
        combine_text = f"Add the change: {original}+{fmt_fraction(delta)}={fmt_fraction(final)}."
    else:
        final = Fraction(original) - delta
        trace_text = f"A decrease of {percent}% means subtracting {percent}% of {original}."
        combine_text = f"Subtract the change: {original}-{fmt_fraction(delta)}={fmt_fraction(final)}."
    trace = [
        TraceStep(op="identify_percent_change", text=trace_text),
        TraceStep(op="compute_percent_amount", text=f"Compute {percent}% of {original}: {percent}/100×{original}={fmt_fraction(delta)}."),
        TraceStep(op="apply_change", text=combine_text),
    ]
    expected = Fraction(original) + delta if direction == "increase" else Fraction(original) - delta
    return make_sample(
        "ratio_percent.percent_change",
        f"A value of {original} is {direction}d by {percent}%. What is the new value?",
        trace,
        fmt_fraction(final),
        {"original": original, "percent": percent, "direction": direction, "difficulty": diff},
        verified=(final == expected),
    )


def gen_proportion_solve(rng: random.Random, cfg: GenConfig) -> Sample:
    diff = pick_difficulty(rng, cfg)
    a = rng.randint(1, 20)
    b = rng.randint(2, 20)
    k = rng.randint(2, 15)
    c = a * k
    x_val = b * k
    trace = [
        TraceStep(op="cross_multiply", text=f"From {a}/{b} = {c}/x, cross multiply to get {a}x={b}×{c}."),
        TraceStep(op="multiply", text=f"Compute {b}×{c}={b * c}, so {a}x={b * c}."),
        TraceStep(op="divide_both_sides", text=f"Divide both sides by {a}: x={b * c}/{a}={x_val}."),
        TraceStep(op="finish", text=f"So the solution is x={x_val}.", after=f"x={x_val}"),
    ]
    return make_sample(
        "ratio_percent.proportion_solve",
        f"Solve the proportion {a}/{b} = {c}/x.",
        trace,
        f"x={x_val}",
        {"a": a, "b": b, "c": c, "x": x_val, "difficulty": diff},
        verified=(Fraction(a, b) == Fraction(c, x_val)),
    )


# -----------------------------------------------------------------------------
# Missing arithmetic primitives (added per coverage review)
# -----------------------------------------------------------------------------


def gen_decimal_division_by_decimal(rng: random.Random, cfg: GenConfig) -> Sample:
    """Divide a decimal by a decimal (e.g. 3.45 ÷ 0.15)."""
    diff = pick_difficulty(rng, cfg)
    places_q = rng.randint(1, {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 2}[diff])
    places_d = rng.randint(1, {Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}[diff])
    divisor_scaled = rng.randint(3, {Difficulty.EASY: 20, Difficulty.MEDIUM: 80, Difficulty.HARD: 200}[diff])
    quotient_scaled = rng.randint(2, {Difficulty.EASY: 20, Difficulty.MEDIUM: 80, Difficulty.HARD: 300}[diff])
    dividend_scaled = divisor_scaled * quotient_scaled  # exact division

    divisor_str = fmt_decimal_from_scaled(divisor_scaled, places_d)
    dividend_str = fmt_decimal_from_scaled(dividend_scaled, places_q + places_d)
    quotient_str = fmt_decimal_from_scaled(quotient_scaled, places_q)

    shift = max(places_q + places_d, places_d)
    d_int = divisor_scaled * 10 ** (shift - places_d)
    n_int = dividend_scaled * 10 ** (shift - (places_q + places_d))

    trace = [
        TraceStep(op="scale_divisor", text=f"Multiply both numbers by 10^{shift} to clear the decimal from the divisor."),
        TraceStep(op="convert_to_integers", text=f"This turns {dividend_str} ÷ {divisor_str} into the equivalent integer division {n_int} ÷ {d_int}."),
        TraceStep(op="compute_quotient", text=f"Divide: {n_int} ÷ {d_int} = {quotient_scaled}."),
        TraceStep(op="place_decimal", text=f"Place the decimal point: the result is {quotient_str}."),
    ]
    return make_sample(
        "arithmetic.decimal_division_by_decimal",
        f"Compute {dividend_str} ÷ {divisor_str}.",
        trace,
        quotient_str,
        {"dividend": dividend_str, "divisor": divisor_str, "shift": shift, "difficulty": diff},
        verified=(Decimal(dividend_str) / Decimal(divisor_str) == Decimal(quotient_str)),
    )


def gen_improper_to_mixed_number(rng: random.Random, cfg: GenConfig) -> Sample:
    """Convert an improper fraction to a mixed number."""
    diff = pick_difficulty(rng, cfg)
    den = rng.randint(2, {Difficulty.EASY: 9, Difficulty.MEDIUM: 12, Difficulty.HARD: 20}[diff])
    whole = rng.randint(1, {Difficulty.EASY: 5, Difficulty.MEDIUM: 12, Difficulty.HARD: 25}[diff])
    num_frac = rng.randint(1, den - 1)
    while math.gcd(num_frac, den) != 1:
        num_frac = rng.randint(1, den - 1)
    num = whole * den + num_frac

    trace = [
        TraceStep(op="divide", text=f"Divide {num} by {den}: {num} ÷ {den} = {whole} with remainder {num_frac}."),
        TraceStep(op="form_mixed", text=f"The quotient {whole} is the whole part; the remainder {num_frac} over {den} gives the fraction {num_frac}/{den}."),
        TraceStep(op="finish", text=f"So {num}/{den} = {whole} {num_frac}/{den}."),
    ]
    return make_sample(
        "arithmetic.improper_to_mixed_number",
        f"Convert {num}/{den} to a mixed number.",
        trace,
        f"{whole} {num_frac}/{den}",
        {"num": num, "den": den, "whole": whole, "remainder": num_frac, "difficulty": diff},
        verified=(Fraction(num, den) == Fraction(whole * den + num_frac, den)),
    )


def gen_order_of_operations_nested(rng: random.Random, cfg: GenConfig) -> Sample:
    """Evaluate an expression with nested parentheses and multiple operations."""
    diff = pick_difficulty(rng, cfg)
    if diff == Difficulty.EASY:
        a, b, c, d = rng.randint(1, 8), rng.randint(1, 6), rng.randint(2, 5), rng.randint(1, 6)
        inner1 = a + b
        inner2 = c - d
        result = inner1 * inner2
        py_result = (a + b) * (c - d)
        expr = f"({a} + {b}) × ({c} - {d})"
        trace = [
            TraceStep(op="first_parens", text=f"Inside the first parentheses: {a} + {b} = {inner1}."),
            TraceStep(op="second_parens", text=f"Inside the second parentheses: {c} - {d} = {inner2}."),
            TraceStep(op="multiply", text=f"Multiply the results: {paren_if_negative(inner1)} × {paren_if_negative(inner2)} = {result}."),
        ]
    elif diff == Difficulty.MEDIUM:
        a, b, c, d = rng.randint(2, 9), rng.randint(1, 7), rng.randint(2, 6), rng.randint(2, 5)
        inner = a + b
        inner2 = inner - c
        result = inner2 * d
        py_result = ((a + b) - c) * d
        expr = f"(({a} + {b}) - {c}) × {d}"
        trace = [
            TraceStep(op="innermost_first", text=f"Inside the innermost parentheses: {a} + {b} = {inner}."),
            TraceStep(op="next_bracket", text=f"Next: ({inner} - {c}) = {inner2}."),
            TraceStep(op="multiply", text=f"Multiply by {d}: {inner2} × {d} = {result}."),
        ]
    else:
        a, b, c, d, e = rng.randint(2, 8), rng.randint(1, 6), rng.randint(2, 5), rng.randint(2, 6), rng.randint(2, 5)
        inner = a + b
        mult = inner * c
        inner2 = mult - d
        result = inner2 * e
        py_result = (((a + b) * c) - d) * e
        expr = f"(({a} + {b}) × {c} - {d}) × {e}"
        trace = [
            TraceStep(op="innermost_first", text=f"Innermost parentheses: {a} + {b} = {inner}."),
            TraceStep(op="multiply", text=f"Multiply by {c}: {inner} × {c} = {mult}."),
            TraceStep(op="inside_brackets", text=f"In the outer brackets: {mult} - {d} = {inner2}."),
            TraceStep(op="final_multiply", text=f"Multiply by {e}: {inner2} × {e} = {result}."),
        ]
    trace.append(TraceStep(op="finish", text=f"So {expr} = {result}.", after=str(result)))
    return make_sample(
        "arithmetic.order_of_operations_nested",
        f"Evaluate {expr}.",
        trace,
        str(result),
        {"a": a, "b": b, "expr": expr, "difficulty": diff},
        verified=(result == py_result),
    )


def gen_rounding_to_place_value(rng: random.Random, cfg: GenConfig) -> Sample:
    """Round a number to a specified place value (tens, hundreds, tenths, etc.)."""
    diff = pick_difficulty(rng, cfg)
    if diff == Difficulty.EASY:
        n = rng.randint(10, 999)
        place = rng.choice([("tens", 10), ("hundreds", 100)])
        name, unit = place
        rounded = round(n / unit) * unit
        trace = [
            TraceStep(op="locate_digit", text=f"Look at the digit in the {name} place of {n}."),
            TraceStep(op="check_next", text=f"The next lower place decides rounding up or down."),
            TraceStep(op="round", text=f"Round to the nearest {unit}: {rounded}."),
        ]
        trace.append(TraceStep(op="finish", text=f"So {n} rounded to the nearest {name} is {rounded}.", after=str(rounded)))
        return make_sample(
            "arithmetic.rounding_to_place_value",
            f"Round {n} to the nearest {name}.",
            trace,
            str(rounded),
            {"n": n, "place": name, "difficulty": diff},
            verified=(int(rounded) == int(round(n / unit) * unit)),
        )
    elif diff == Difficulty.MEDIUM:
        n = rng.randint(100, 99999)
        place = rng.choice([("hundreds", 100), ("thousands", 1000)])
        name, unit = place
        rounded = round(n / unit) * unit
        trace = [
            TraceStep(op="locate_digit", text=f"Look at the digit in the {name} place of {n}."),
            TraceStep(op="check_next", text=f"The digit in the next lower place is {(n % unit) // (unit // 10)}."),
            TraceStep(op="round", text=f"Round to the nearest {name}: {rounded}."),
        ]
        trace.append(TraceStep(op="finish", text=f"So {n} rounded to the nearest {name} is {rounded}.", after=str(rounded)))
        return make_sample(
            "arithmetic.rounding_to_place_value",
            f"Round {n} to the nearest {name}.",
            trace,
            str(rounded),
            {"n": n, "place": name, "difficulty": diff},
            verified=(int(rounded) == int(round(n / unit) * unit)),
        )
    else:
        # Decimal place rounding — ensure the number has more digits than the target
        # so rounding actually changes the value (non-trivial).
        places = rng.randint(1, 3)
        # Generate with extra digits beyond the rounding target.
        extra = rng.randint(1, 2)
        total_places = places + extra
        n = rng.randint(100, 99999)
        dec = Decimal(n) / Decimal(10**total_places)
        dec_str = format(dec.normalize(), "f")
        rounded = dec.quantize(Decimal(1) / Decimal(10**places))
        rounded_str = format(rounded.normalize(), "f")
        trace = [
            TraceStep(op="locate_digit", text=f"Round {dec_str} to {places} decimal place(s)."),
            TraceStep(op="check_next", text=f"Look at the digit in the {ordinal(places + 1)} decimal place."),
            TraceStep(op="round", text=f"Round, giving {rounded_str}."),
        ]
        trace.append(TraceStep(op="finish", text=f"So {dec_str} rounded to {places} decimal place(s) is {rounded_str}.", after=rounded_str))
        return make_sample(
            "arithmetic.rounding_to_place_value",
            f"Round {dec_str} to {places} decimal place(s).",
            trace,
            rounded_str,
            {"n": dec_str, "places": places, "difficulty": diff},
            verified=(rounded == round(dec, places)),
        )


def gen_scientific_notation_convert(rng: random.Random, cfg: GenConfig) -> Sample:
    """Convert between standard decimal form and scientific notation."""
    diff = pick_difficulty(rng, cfg)
    if rng.random() < 0.5:
        # Standard → scientific: build exactly using Decimal.
        exp = rng.randint({Difficulty.EASY: 2, Difficulty.MEDIUM: 4, Difficulty.HARD: 7}[diff],
                          {Difficulty.EASY: 4, Difficulty.MEDIUM: 7, Difficulty.HARD: 12}[diff])
        mantissa_int = rng.randint(10, 99)
        mantissa = Decimal(mantissa_int) / Decimal(10)
        n = mantissa * Decimal(10**exp)
        n_str = format(n.normalize(), "f")
        mantissa_str = format(mantissa.normalize(), "f").rstrip("0").rstrip(".")
        answer = f"{mantissa_str} × 10^{exp}"
        trace = [
            TraceStep(op="move_decimal", text=f"Move the decimal point in {n_str} so there is exactly one nonzero digit before it."),
            TraceStep(op="count_places", text=f"The decimal moved {exp} place(s), giving {mantissa_str} × 10^{exp}."),
            TraceStep(op="finish", text=f"So {n_str} = {answer}.", after=answer),
        ]
        return make_sample(
            "arithmetic.scientific_notation_convert",
            f"Write {n_str} in scientific notation.",
            trace,
            answer,
            {"n": n_str, "exp": exp, "mantissa": mantissa_str, "difficulty": diff},
            verified=(n == mantissa * Decimal(10**exp)),
        )
    else:
        # Scientific → standard: build exactly using Decimal.
        mantissa_int = rng.randint(10, 99)
        mantissa = Decimal(mantissa_int) / Decimal(10)
        exp = rng.randint({Difficulty.EASY: 1, Difficulty.MEDIUM: 2, Difficulty.HARD: 3}[diff],
                          {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 8}[diff])
        mantissa_str = format(mantissa.normalize(), "f").rstrip("0").rstrip(".")
        n = mantissa * Decimal(10**exp)
        n_str = format(n.normalize(), "f")
        answer = n_str
        trace = [
            TraceStep(op="multiply_by_power", text=f"Multiply {mantissa_str} by 10^{exp}: move the decimal point {exp} place(s) to the right."),
            TraceStep(op="write_standard", text=f"This gives {n_str}."),
            TraceStep(op="finish", text=f"So {mantissa_str} × 10^{exp} = {answer}.", after=answer),
        ]
        return make_sample(
            "arithmetic.scientific_notation_convert",
            f"Write {mantissa_str} × 10^{exp} in standard notation.",
            trace,
            answer,
            {"mantissa": mantissa_str, "exp": exp, "difficulty": diff},
            verified=(n == mantissa * Decimal(10**exp)),
        )


def gen_percent_find_part_or_whole(rng: random.Random, cfg: GenConfig) -> Sample:
    """Find a percentage of a number, or find the whole given a percentage part."""
    diff = pick_difficulty(rng, cfg)
    if rng.random() < 0.5:
        # "What is P% of N?"
        percent = rng.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 85, 90, 120, 150])
        base = rng.randint({Difficulty.EASY: 20, Difficulty.MEDIUM: 80, Difficulty.HARD: 450}[diff],
                          {Difficulty.EASY: 200, Difficulty.MEDIUM: 600, Difficulty.HARD: 2000}[diff])
        result = Fraction(base * percent, 100)
        answer = fmt_fraction(result) if result.denominator != 1 else str(result)
        trace = [
            TraceStep(op="percent_means", text=f"{percent}% means {percent} per 100, so as a fraction it is {percent}/100."),
            TraceStep(op="multiply", text=f"Multiply: {base} × {percent}/100 = ({base} × {percent}) / 100."),
            TraceStep(op="compute", text=f"Compute: {base * percent} ÷ 100 = {answer}."),
            TraceStep(op="finish", text=f"So {percent}% of {base} is {answer}.", after=answer),
        ]
        return make_sample(
            "ratio_percent.percent_find_part_or_whole",
            f"Find {percent}% of {base}.",
            trace,
            answer,
            {"percent": percent, "base": base, "result": answer, "difficulty": diff},
            verified=(Fraction(base * percent, 100) == Fraction(result)),
        )
    else:
        # "P is R% of what number?" → whole = P / (R/100)
        part = rng.randint({Difficulty.EASY: 5, Difficulty.MEDIUM: 20, Difficulty.HARD: 60}[diff],
                          {Difficulty.EASY: 40, Difficulty.MEDIUM: 150, Difficulty.HARD: 400}[diff])
        percent = rng.choice([5, 10, 20, 25, 30, 40, 50, 75, 125])
        whole = Fraction(part * 100, percent)
        answer = fmt_fraction(whole) if whole.denominator != 1 else str(whole)
        trace = [
            TraceStep(op="set_up_proportion", text=f"If {part} is {percent}% of the whole x, then {part} = ({percent}/100) × x."),
            TraceStep(op="write_equation", text=f"So {part} = {percent}/100 × x."),
            TraceStep(op="solve", text=f"Multiply both sides by 100/{percent}: x = {part} × 100/{percent}."),
            TraceStep(op="compute", text=f"x = {part * 100} / {percent} = {answer}."),
            TraceStep(op="finish", text=f"So {part} is {percent}% of {answer}.", after=answer),
        ]
        return make_sample(
            "ratio_percent.percent_find_part_or_whole",
            f"{part} is {percent}% of what number?",
            trace,
            answer,
            {"part": part, "percent": percent, "whole": answer, "difficulty": diff},
            verified=(Fraction(part, 1) == Fraction(percent * whole, 100)),
        )


REGISTRY: Dict[str, Any] = {
    "arithmetic.integer_addition_carry": gen_integer_addition_carry,
    "arithmetic.integer_add_many": gen_integer_add_many,
    "arithmetic.integer_subtraction_borrow": gen_integer_subtraction_borrow,
    "arithmetic.integer_mixed_add_sub": gen_integer_mixed_add_sub,
    "arithmetic.long_multiplication": gen_long_multiplication,
    "arithmetic.long_division_exact": gen_long_division_exact,
    "arithmetic.long_division_remainder": gen_long_division_remainder,
    "arithmetic.long_division_zero_in_quotient": gen_long_division_zero_in_quotient,
    "arithmetic.sign_rules_multiplication": gen_sign_rules_multiplication,
    "arithmetic.fraction_simplification": gen_fraction_simplification,
    "arithmetic.fraction_addition": gen_fraction_addition,
    "arithmetic.fraction_subtraction": gen_fraction_subtraction,
    "arithmetic.fraction_multiplication": gen_fraction_multiplication,
    "arithmetic.fraction_division": gen_fraction_division,
    "arithmetic.mixed_number_to_improper": gen_mixed_number_to_improper,
    "arithmetic.improper_to_mixed_number": gen_improper_to_mixed_number,
    "arithmetic.decimal_addition": gen_decimal_addition,
    "arithmetic.decimal_subtraction": gen_decimal_subtraction,
    "arithmetic.decimal_multiplication": gen_decimal_multiplication,
    "arithmetic.decimal_division_by_integer": gen_decimal_division_by_integer,
    "arithmetic.decimal_division_by_decimal": gen_decimal_division_by_decimal,
    "arithmetic.powers": gen_powers,
    "arithmetic.radical_simplification": gen_radical_simplification,
    "arithmetic.rounding_to_place_value": gen_rounding_to_place_value,
    "arithmetic.scientific_notation_convert": gen_scientific_notation_convert,
    "arithmetic.order_of_operations_basic": gen_order_of_operations_basic,
    "arithmetic.order_of_operations_parentheses": gen_order_of_operations_parentheses,
    "arithmetic.order_of_operations_nested": gen_order_of_operations_nested,
    "number_theory.gcd_euclidean_algorithm": gen_gcd_euclidean_algorithm,
    "number_theory.lcm_using_gcd": gen_lcm_using_gcd,
    "number_theory.prime_factorization": gen_prime_factorization,
    "ratio_percent.percent_to_fraction_decimal": gen_percent_to_fraction_decimal,
    "ratio_percent.percent_change": gen_percent_change,
    "ratio_percent.proportion_solve": gen_proportion_solve,
    "ratio_percent.percent_find_part_or_whole": gen_percent_find_part_or_whole,
}
