#!/usr/bin/env python3
"""Review CoT completeness across all mathgen sources.

Generates samples from every source, checks for common issues, and produces
a structured report with per-source PASS/MINOR/FAIL ratings.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

from mathgen.config import GenConfig, Difficulty
from mathgen.registry import GENERATORS, generate_samples
from mathgen.domains import arithmetic_core

# Dirty patterns from des_instruct.md sec 5 / sec 9.
DIRTY_PATTERNS = ["+-", "+ -", "--", "/-", "×-", "÷-", "*-", "zero(s)"]
NUMBERED_LINE = re.compile(r"(?m)^\s*\d+\.\s")
ORDINAL_BAD = re.compile(r"\b(\d+)(th|st|nd|rd)\b")


def check_ordinal_typos(text: str) -> List[str]:
    """Catch '3th', '2th' etc."""
    issues = []
    for m in ORDINAL_BAD.finditer(text):
        n = int(m.group(1))
        suffix = m.group(2)
        expected = _expected_ordinal(n)
        if suffix != expected:
            issues.append(f"ordinal typo: {n}{suffix} should be {n}{expected}")
    return issues


def _expected_ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        return "th"
    last = n % 10
    if last == 1:
        return "st"
    if last == 2:
        return "nd"
    if last == 3:
        return "rd"
    return "th"


def _issue(severity: str, detail: str) -> str:
    return f"[{severity}] {detail}"


def review_source(src: str) -> Tuple[str, List[str], Dict]:
    """Return (rating, issues_list, stats_dict) for one source."""
    import random
    rng = random.Random(99 + hash(src) % 10000)
    issues: List[str] = []
    stats = {"samples": 0, "verified": 0, "avg_steps": 0, "max_steps": 0, "min_steps": float("inf")}

    # Test with mixed difficulty
    samples = generate_samples(15, rng.randint(0, 100_000), GenConfig(difficulty=Difficulty.MIXED), sources=[src])

    stats["samples"] = len(samples)
    total_steps = 0
    for s in samples:
        n_steps = len(s.trace)
        total_steps += n_steps
        stats["max_steps"] = max(stats["max_steps"], n_steps)
        stats["min_steps"] = min(stats["min_steps"], n_steps)
        if s.verified:
            stats["verified"] += 1

        # Check dirty patterns
        content = s.messages[1]["content"] if len(s.messages) > 1 else ""
        think_body = content.split("</think>")[0] if "</think>" in content else content
        for pat in DIRTY_PATTERNS:
            if pat in content:
                issues.append(_issue("DIRTY", f"pattern '{pat}' found in assistant content"))

        # Check numbered list
        if NUMBERED_LINE.search(think_body):
            issues.append(_issue("DIRTY", "numbered list in reasoning"))

        # Check ordinal typos
        for m in ORDINAL_BAD.finditer(content):
            n = int(m.group(1))
            suffix = m.group(2)
            expected = _expected_ordinal(n)
            if suffix != expected:
                issues.append(_issue("TYPO", f"ordinal: {n}{suffix} → {n}{expected}"))

        # Check boxed answer consistency
        answer = s.answer
        if answer and f"\\boxed{{{answer}}}" not in content:
            issues.append(_issue("FORMAT", f"boxed answer mismatch: '{answer}' not boxed"))

        # Check minimum steps for algorithmic sources
        # Arithmetic operations should have at least 3 steps
        if n_steps <= 1:
            issues.append(_issue("SKIP", f"only {n_steps} trace step(s)"))

    stats["avg_steps"] = total_steps / len(samples) if samples else 0

    # Determine rating
    if stats["verified"] < len(samples):
        rating = "FAIL"
        issues.append(_issue("FAIL", f"only {stats['verified']}/{stats['samples']} verified"))
    elif any("SKIP" in i or "FAIL" in i for i in issues):
        rating = "FAIL"
    elif any("DIRTY" in i for i in issues):
        rating = "MINOR"
    elif stats["avg_steps"] < 2 and "flashcard" not in str(issues):
        # Sources with very few steps might be formula-application, flag as MINOR
        rating = "MINOR"
        issues.append(_issue("MINOR", f"avg only {stats['avg_steps']:.1f} steps — flashcard-like"))
    else:
        rating = "PASS"

    return rating, issues, stats


def main():
    all_sources = sorted(GENERATORS.keys())
    print(f"Reviewing {len(all_sources)} sources...\n")

    ratings: Dict[str, List[str]] = defaultdict(list)
    all_issues: List[Tuple[str, str, str]] = []  # (source, rating, issue)

    for i, src in enumerate(all_sources):
        rating, issues, stats = review_source(src)
        ratings[rating].append(src)
        for issue in issues:
            all_issues.append((src, rating, issue))

        # Progress indicator
        if (i + 1) % 25 == 0:
            print(f"  ... {i+1}/{len(all_sources)}", file=sys.stderr)

    # Report
    print("=" * 80)
    print("COT REVIEW REPORT")
    print("=" * 80)

    print(f"\n## Summary")
    print(f"Total sources: {len(all_sources)}")
    for rating in ["PASS", "MINOR", "FAIL"]:
        print(f"  {rating}: {len(ratings[rating])}")

    if ratings["FAIL"]:
        print(f"\n## FAIL ({len(ratings['FAIL'])} sources)")
        for src in sorted(ratings["FAIL"]):
            src_issues = [iss for s, r, iss in all_issues if s == src and r == "FAIL"]
            print(f"  {src}")
            for iss in src_issues[:3]:
                print(f"    {iss}")

    if ratings["MINOR"]:
        print(f"\n## MINOR ({len(ratings['MINOR'])} sources)")
        for src in sorted(ratings["MINOR"]):
            src_issues = [iss for s, r, iss in all_issues if s == src and r == "MINOR"]
            print(f"  {src}")
            for iss in src_issues[:2]:
                print(f"    {iss}")

    # Category breakdown
    print(f"\n## By Domain")
    domains = defaultdict(list)
    for src in sorted(all_sources):
        domain = src.split(".")[0]
        domains[domain].append(src)

    for domain in sorted(domains):
        srcs = domains[domain]
        passes = sum(1 for s in srcs if s in ratings["PASS"])
        minors = sum(1 for s in srcs if s in ratings["MINOR"])
        fails = sum(1 for s in srcs if s in ratings["FAIL"])
        print(f"  {domain}: {len(srcs)} sources — PASS={passes} MINOR={minors} FAIL={fails}")

    # Top issues summary
    print(f"\n## All Issues ({len(all_issues)} total)")
    issue_types = defaultdict(list)
    for src, rating, issue in all_issues:
        issue_types[issue[:60]].append(src)
    for issue_text, srcs in sorted(issue_types.items(), key=lambda x: -len(x[1])):
        print(f"  [{len(srcs)}x] {issue_text}")

    return 0 if not ratings["FAIL"] else 1


if __name__ == "__main__":
    sys.exit(main())
