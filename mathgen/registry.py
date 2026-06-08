"""Central registry: merges every domain's generators and drives sampling."""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Optional, Sequence

from mathgen.config import GenConfig
from mathgen.core import Sample
from mathgen.domains import (
    arithmetic_core,
    comparison_core,
    equation_inequality_core,
    exp_log_core,
    expression_rewrite_core,
    functions_core,
    number_theory_core,
    quadratic_schema,
    sequences_core,
    set_logic_core,
)

Generator = Callable[[random.Random, GenConfig], Sample]

# Domain module -> source prefix map, used for lineage (which code module produced a source).
DOMAIN_MODULES = [
    arithmetic_core,
    expression_rewrite_core,
    equation_inequality_core,
    quadratic_schema,
    functions_core,
    sequences_core,
    exp_log_core,
    number_theory_core,
    comparison_core,
    set_logic_core,
]


def _build_registry() -> Dict[str, Generator]:
    merged: Dict[str, Generator] = {}
    for mod in DOMAIN_MODULES:
        for name, fn in mod.REGISTRY.items():
            if name in merged:
                raise RuntimeError(f"Duplicate source name across domains: {name}")
            merged[name] = fn
    return merged


GENERATORS: Dict[str, Generator] = _build_registry()


# Heavier weight on the core algorithmic skills (des_instruct.md sec 8.1).
DEFAULT_WEIGHTS: Dict[str, float] = {
    "arithmetic.integer_addition_carry": 1.3,
    "arithmetic.integer_subtraction_borrow": 1.3,
    "arithmetic.long_multiplication": 1.5,
    "arithmetic.long_division_exact": 1.5,
    "arithmetic.long_division_remainder": 1.2,
    "arithmetic.long_division_zero_in_quotient": 1.2,
    "arithmetic.fraction_simplification": 1.2,
    "arithmetic.fraction_addition": 1.2,
    "arithmetic.fraction_subtraction": 1.2,
}


def module_for_source(source: str):
    for mod in DOMAIN_MODULES:
        if source in mod.REGISTRY:
            return mod
    return None


def choose_generator_name(rng: random.Random, names: Sequence[str]) -> str:
    weights = [DEFAULT_WEIGHTS.get(name, 1.0) for name in names]
    return rng.choices(list(names), weights=weights, k=1)[0]


def generate_samples(
    n: int,
    seed: int,
    cfg: GenConfig,
    sources: Optional[List[str]] = None,
    cycle: bool = False,
) -> List[Sample]:
    rng = random.Random(seed)
    names = sources or list(GENERATORS.keys())
    unknown = [s for s in names if s not in GENERATORS]
    if unknown:
        raise ValueError(f"Unknown source(s): {unknown}")
    samples: List[Sample] = []
    for i in range(n):
        name = names[i % len(names)] if cycle else choose_generator_name(rng, names)
        sample = GENERATORS[name](rng, cfg)
        if sample.source != name:
            raise RuntimeError(f"Generator registered as {name} returned source {sample.source}")
        samples.append(sample)
    return samples


def self_test(seed: int, cfg: GenConfig, per_source: int = 20) -> List[str]:
    """Generate per_source samples for every source; return list of failure strings."""
    failures: List[str] = []
    for source in GENERATORS:
        samples = generate_samples(per_source, seed + (hash(source) % 10_000), cfg, sources=[source])
        for idx, sample in enumerate(samples):
            if not sample.verified:
                failures.append(f"{source}[{idx}] failed verification")
            if not sample.trace:
                failures.append(f"{source}[{idx}] has empty trace")
            if not sample.answer:
                failures.append(f"{source}[{idx}] has empty answer")
    return failures
