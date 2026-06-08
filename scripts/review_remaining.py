#!/usr/bin/env python3
"""Review remaining (non-core) domains against des_instruct.md requirements.

Core domains (arithmetic, expression_rewrite, equation, inequality) are already
thoroughly reviewed. This script checks everything else.
"""
from __future__ import annotations

import re
from collections import defaultdict

from mathgen.config import GenConfig, Difficulty
from mathgen.registry import GENERATORS, generate_samples

CORE_PREFIXES = (
    "arithmetic.", "expression_rewrite.", "equation.", "inequality.",
    "quadratic.", "rational_inequality_schema.", "absolute_value_schema.",
    "number_theory.", "ratio_percent.",
)

DIRTY_PATTERNS = ["+-", "+ -", "--", "×-", "÷-", "*-", "× -", "+ -"]
NUMBERED_LINE = re.compile(r"(?m)^\s*\d+\.\s")


def check_domain_requirements(src: str, samples: list) -> list[str]:
    """Check domain-specific requirements from des_instruct.md."""
    issues = []

    for s in samples:
        c = s.messages[1]["content"]
        think_body = c.split("</think>")[0] if "</think>" in c else c

        # --- Universal checks ---
        # Boxed answer must appear in reasoning
        if s.answer and f"\\boxed{{{s.answer}}}" not in c:
            issues.append(f"boxed answer '{s.answer}' not found in content")

        # --- Domain-specific checks ---
        prefix = src.split(".")[0]

        # Trig: must show period/quadrant/special angle values
        if prefix in ("trigonometry", "trigonometric_schema"):
            if "sin" in think_body or "cos" in think_body or "tan" in think_body:
                if "sin" in s.messages[0]["content"] and "period" not in think_body.lower():
                    # Not necessarily an issue for all trig problems, but flag simple ones
                    pass

        # Functions: domain restrictions
        if prefix == "function" and "sqrt" in s.messages[0]["content"]:
            if "≥ 0" not in think_body and "nonnegative" not in think_body.lower():
                issues.append("sqrt function missing domain restriction check")

        if prefix == "function" and "log" in s.messages[0]["content"].lower():
            if "> 0" not in think_body and "positive" not in think_body.lower():
                issues.append("log function missing domain restriction check")

        # Inequalities: sign flip when dividing by negative
        if "inequality" in src or ">" in s.messages[0]["content"] or "<" in s.messages[0]["content"]:
            if any("divide" in t.text.lower() and "negative" in t.text.lower() and "flip" in t.text.lower()
                   for t in s.trace):
                pass  # Sign flip explicitly mentioned
            # Not all inequalities divide by negative, so this is just a positive check

        # Word problems: should have real-world context
        if prefix == "word_problem":
            if len(s.trace) < 3:
                issues.append(f"word problem too few steps ({len(s.trace)})")

        # Domain_assumption: must explicitly state the restriction
        if prefix == "domain_assumption":
            if "≠" not in c and ">" not in c and "≥" not in c and "restriction" not in think_body.lower():
                issues.append("domain_assumption missing explicit restriction statement")

    return issues


def main():
    remaining = sorted(s for s in GENERATORS if not s.startswith(CORE_PREFIXES))
    print(f"Reviewing {len(remaining)} sources across non-core domains...\n")

    issues_by_domain = defaultdict(list)
    flashcard_sources = []
    excellent_sources = []

    for src in remaining:
        import random
        rng = random.Random(99 + hash(src) % 10000)
        samples = generate_samples(4, rng.randint(0, 100_000), GenConfig(), sources=[src])

        domain = src.split(".")[0]
        src_issues = []

        # Check verification
        bad = [s for s in samples if not s.verified]
        if bad:
            src_issues.append(f"FAIL: {len(bad)}/{len(samples)} not verified")

        # Check dirty patterns
        for s in samples:
            c = s.messages[1]["content"]
            for pat in DIRTY_PATTERNS:
                if pat in c:
                    src_issues.append(f"DIRTY: '{pat}' in content")
                    break
            if NUMBERED_LINE.search(c.split("</think>")[0]):
                src_issues.append("NUMLIST in reasoning")

        # Check trace quality
        steps = [len(s.trace) for s in samples]
        avg = sum(steps) / len(steps)
        if avg < 2.0:
            flashcard_sources.append((src, avg, max(steps)))
        if avg >= 4.5:
            excellent_sources.append((src, avg, max(steps)))

        # Domain-specific checks
        domain_issues = check_domain_requirements(src, samples)
        src_issues.extend(domain_issues)

        if src_issues:
            issues_by_domain[domain].append((src, src_issues))

        # Print per-source status
        status = "FAIL" if bad else ("WARN" if src_issues else "OK")
        if status != "OK" or avg < 2.0:
            print(f"[{status}] {src} | steps avg={avg:.1f} max={max(steps)} | v={len(samples)-len(bad)}/{len(samples)}")
            if src_issues:
                for iss in src_issues[:3]:
                    print(f"       {iss}")
            # Show 1 sample trace
            s = samples[0]
            print(f"       Q: {s.messages[0]['content'][:120]}")
            for t in s.trace[:3]:
                print(f"         [{t.op}] {t.text[:160]}")
            print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    # By domain
    all_srcs = defaultdict(list)
    for src in remaining:
        all_srcs[src.split(".")[0]].append(src)

    print(f"\nIssues by domain:")
    for domain in sorted(all_srcs):
        iss = issues_by_domain.get(domain, [])
        ok = len(all_srcs[domain]) - len(iss)
        print(f"  {domain}: {len(all_srcs[domain])} sources — OK={ok} WARN/FAIL={len(iss)}")

    if flashcard_sources:
        print(f"\nFlashcard sources (avg < 2.0 steps): {len(flashcard_sources)}")
        for src, avg, mx in flashcard_sources:
            print(f"  {src}: avg={avg:.1f} max={mx}")

    if excellent_sources:
        print(f"\nExcellent sources (avg >= 4.5 steps): {len(excellent_sources)}")
        for src, avg, mx in excellent_sources[:10]:
            print(f"  {src}: avg={avg:.1f} max={mx}")

    # Total counts
    total_issues = sum(len(v) for v in issues_by_domain.values())
    print(f"\nTotal non-OK issues: {total_issues} across {len(issues_by_domain)} domains")


if __name__ == "__main__":
    main()
