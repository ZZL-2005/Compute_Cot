"""Sample validation: enforce the discard rules from des_instruct.md sec 9.

A sample is only allowed into the dataset if it is verified, has a non-empty
trace and answer, uses the exact assistant format, contains no numbered list,
no dirty renderer fragments, its boxed answer matches the answer field, and the
boxed answer is actually reached in the reasoning (the "no skipped steps" guard).
"""

from __future__ import annotations

import re
from typing import List, Tuple

from mathgen.core import Sample

# Dirty renderer fragments (des_instruct.md sec 5 / sec 9.7).
DIRTY_PATTERNS = ["+-", "+ -", "--", "/-", "×-", "÷-", "*-"]

# Leading "1. " "2. " style numbered list (des_instruct.md sec 9.6).
NUMBERED_LINE = re.compile(r"(?m)^\s*\d+\.\s")

BOXED = re.compile(r"#### \\boxed\{(?P<ans>.*)\}\s*$", re.DOTALL)

_WS = re.compile(r"\s+")


def _strip_ws(s: str) -> str:
    return _WS.sub("", s)


def _reasoning_of(sample: Sample) -> str:
    content = sample.messages[1]["content"]
    return content


def validate_sample(sample: Sample) -> Tuple[bool, List[str]]:
    problems: List[str] = []
    if not sample.verified:
        problems.append("not verified")
    if not sample.trace:
        problems.append("empty trace")
    if not sample.answer:
        problems.append("empty answer")

    content = _reasoning_of(sample)
    if not content.startswith("<think>\n"):
        problems.append("assistant does not start with <think>")
    if "\n</think>\n#### \\boxed{" not in content:
        problems.append("assistant missing </think> / boxed answer line")

    m = BOXED.search(content)
    if not m:
        problems.append("could not parse boxed answer")
    else:
        boxed = m.group("ans")
        if boxed != sample.answer:
            problems.append(f"boxed answer {boxed!r} != answer field {sample.answer!r}")

    # Only inspect the reasoning body for numbered lists / dirty fragments.
    think_body = content.split("</think>")[0]
    if NUMBERED_LINE.search(think_body):
        problems.append("reasoning contains a numbered list")
    for pat in DIRTY_PATTERNS:
        if pat in content:
            problems.append(f"dirty fragment {pat!r}")

    # "no skipped steps": the final boxed answer must actually be reached in the
    # reasoning, not produced out of nowhere. Compare whitespace-insensitively so
    # cosmetic gaps ("x = 10" vs "x=10") do not count as a mismatch.
    if sample.answer:
        norm_answer = _strip_ws(sample.answer)
        if norm_answer and norm_answer not in _strip_ws(think_body):
            problems.append("boxed answer is not derived in the reasoning (possible skipped step)")

    return (not problems), problems
