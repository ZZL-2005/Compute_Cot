"""Command-line entry point for mathgen.

Generates verified, validated JSONL datasets and records data lineage
(producer + inputs one level up; consumers one level down) for every file.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from mathgen.config import Difficulty, GenConfig
from mathgen.core import Sample, json_default
from mathgen.lineage import ProducedBy, record_consumption, record_production, trace as lineage_trace
from mathgen.registry import GENERATORS, choose_generator_name, generate_samples, module_for_source, self_test
from mathgen.validate import validate_sample

# Specs this generator is derived from (the "up one level" inputs for raw data).
SPEC_INPUTS = [
    {"type": "spec", "ref": "docs/design.md"},
    {"type": "spec", "ref": "docs/des_instruct.md"},
]


def generate_clean(
    n: int,
    seed: int,
    cfg: GenConfig,
    sources: Optional[List[str]] = None,
    cycle: bool = False,
    max_attempts_factor: int = 50,
) -> List[Sample]:
    """Collect n samples that pass validation, resampling on rejection (sec 9)."""
    rng = random.Random(seed)
    names = sources or list(GENERATORS.keys())
    unknown = [s for s in names if s not in GENERATORS]
    if unknown:
        raise ValueError(f"Unknown source(s): {unknown}")

    collected: List[Sample] = []
    attempts = 0
    cap = max(1000, n * max_attempts_factor)
    i = 0
    while len(collected) < n and attempts < cap:
        attempts += 1
        name = names[i % len(names)] if cycle else choose_generator_name(rng, names)
        i += 1
        sample = GENERATORS[name](rng, cfg)
        ok, _ = validate_sample(sample)
        if ok:
            collected.append(sample)
    if len(collected) < n:
        raise RuntimeError(f"Only collected {len(collected)}/{n} valid samples after {attempts} attempts.")
    return collected


def write_jsonl(samples: Sequence[Sample], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s.to_json_obj(), ensure_ascii=False, default=json_default) + "\n")


def print_pretty(samples: Sequence[Sample], k: int) -> None:
    for i, s in enumerate(samples[:k]):
        print("=" * 80)
        print(f"[{i}] {s.source} | verified={s.verified}")
        print("USER:", s.messages[0]["content"])
        print("ASSISTANT:")
        print(s.messages[1]["content"])


def parse_sources_arg(s: str) -> List[str]:
    return [x.strip() for x in s.split(",") if x.strip()] if s else []


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Generate verified math SFT data with data lineage.")
    parser.add_argument("--n", type=int, default=50, help="Number of samples to generate.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed (same seed -> reproducible output).")
    parser.add_argument("--out", type=str, default="data/mathgen_samples.jsonl", help="Output JSONL path.")
    parser.add_argument("--pretty", type=int, default=3, help="Print the first K examples.")
    parser.add_argument("--difficulty", choices=[Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD, Difficulty.MIXED], default=Difficulty.MIXED)
    parser.add_argument("--sources", type=str, default="", help="Comma-separated source names to sample from.")
    parser.add_argument("--cycle", action="store_true", help="Cycle through sources instead of weighted sampling.")
    parser.add_argument("--list-sources", action="store_true", help="List available source names and exit.")
    parser.add_argument("--self-test", action="store_true", help="Verify every source and exit.")
    parser.add_argument("--self-test-per-source", type=int, default=20)
    parser.add_argument("--no-lineage", action="store_true", help="Do not write lineage sidecar/manifest.")
    parser.add_argument("--trace", type=str, default="", help="Print the lineage (up/down) of a data file and exit.")
    parser.add_argument("--consumed-by", type=str, default="", help="Record that this consumer used --out, then exit.")
    args = parser.parse_args(argv)

    if args.list_sources:
        for name in GENERATORS:
            print(name)
        return

    if args.trace:
        print(json.dumps(lineage_trace(Path(args.trace)), ensure_ascii=False, indent=2))
        return

    if args.consumed_by:
        record_consumption(Path(args.out), args.consumed_by, note="recorded via --consumed-by")
        print(f"Recorded consumption of {args.out} by {args.consumed_by}")
        return

    cfg = GenConfig(difficulty=args.difficulty)

    if args.self_test:
        failures = self_test(args.seed, cfg, per_source=args.self_test_per_source)
        if failures:
            print("SELF-TEST FAILED")
            for f in failures[:50]:
                print(" ", f)
            sys.exit(1)
        print(f"SELF-TEST PASSED: {len(GENERATORS)} sources × {args.self_test_per_source} samples/source")
        return

    sources = parse_sources_arg(args.sources) or None
    samples = generate_clean(args.n, args.seed, cfg, sources=sources, cycle=args.cycle)
    out_path = Path(args.out)
    write_jsonl(samples, out_path)
    print(f"Wrote {len(samples)} samples to {out_path}")

    if not args.no_lineage:
        used_sources = sorted({s.source for s in samples})
        code_modules = sorted({module_for_source(src).__name__ for src in used_sources if module_for_source(src)})
        produced_by = ProducedBy(
            command=["mathgen"] + (argv if argv is not None else sys.argv[1:]),
            seed=args.seed,
            config={"difficulty": args.difficulty, "n": args.n, "cycle": args.cycle},
            sources=used_sources,
            code_modules=code_modules,
            inputs=SPEC_INPUTS,
        )
        sc = record_production(out_path, produced_by, records=len(samples))
        print(f"Wrote lineage sidecar to {sc}")

    if args.pretty:
        print_pretty(samples, args.pretty)


if __name__ == "__main__":
    main()
