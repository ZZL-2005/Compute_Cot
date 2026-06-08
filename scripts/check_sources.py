"""Acceptance probe: verify + validate every source (optionally filtered by prefix).

Usage:
  uv run python scripts/check_sources.py            # all sources
  uv run python scripts/check_sources.py exp_log.    # only sources starting with prefix(es)
"""

from __future__ import annotations

import sys
import collections

from mathgen.config import GenConfig
from mathgen.registry import GENERATORS, generate_samples
from mathgen.validate import validate_sample

PREFIXES = sys.argv[1:]
SCAN = ["+-", "+ -", "--", "×-", "÷-", "*-", "/-", "- -"]


def selected(name: str) -> bool:
    return not PREFIXES or any(name.startswith(p) for p in PREFIXES)


def main() -> int:
    names = [n for n in GENERATORS if selected(n)]
    print(f"checking {len(names)} sources (prefixes={PREFIXES or 'ALL'})")
    cfg = GenConfig(difficulty="mixed")
    vfail = collections.Counter()
    verr = collections.Counter()
    blem = collections.Counter()
    ex = {}
    for src in names:
        for seed in (1, 2, 3, 4, 5):
            for s in generate_samples(40, seed, cfg, sources=[src]):
                if not s.verified:
                    verr[src] += 1
                ok, probs = validate_sample(s)
                if not ok:
                    vfail[src] += 1
                    ex.setdefault(src, (probs, s.messages[0]["content"], s.messages[1]["content"]))
                full = s.messages[0]["content"] + " || " + s.messages[1]["content"]
                for p in SCAN:
                    if p in full:
                        blem[(src, p)] += 1
                        ex.setdefault((src, p), full)
    print("verification failures:", sum(verr.values()), dict(verr))
    print("validator failures:", sum(vfail.values()))
    for src, c in vfail.most_common():
        probs, q, a = ex[src]
        print(f"\n### {src} x{c} {probs}\n  Q: {q}\n  {a[:400]}")
    print("blemish hits:", sum(blem.values()))
    for (src, p), c in blem.most_common(10):
        print(f"  {src} {p!r} x{c}: {ex[(src,p)][:160]}")
    ok = not (sum(verr.values()) or sum(vfail.values()) or sum(blem.values()))
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
