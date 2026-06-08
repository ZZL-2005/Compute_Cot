# Compute_Cot — verifiable math SFT data generator

`mathgen` is a programmatic generator of high-quality, **auto-verified**,
difficulty-controlled math training data. Every sample carries a step-by-step
`<think>` derivation, a structured `trace`, a machine-readable `answer`, and is
checked (`verified=true`) before it is allowed into a dataset. See
[`docs/des_instruct.md`](docs/des_instruct.md) for the full specification and
[`docs/design.md`](docs/design.md) for the symbolic-primitive taxonomy.

## Environment (uv, local to this directory)

The virtualenv and the uv cache both live inside the project (per `AGENTS.md`):

```bash
export UV_CACHE_DIR="$PWD/.uv_cache"
export UV_PROJECT_ENVIRONMENT="$PWD/.venv"
uv sync
```

## Usage

```bash
# List every available source
uv run python -m mathgen.cli --list-sources

# Verify every generator (acceptance check)
uv run python -m mathgen.cli --self-test --self-test-per-source 100

# Generate a dataset (reproducible for a fixed --seed)
uv run python -m mathgen.cli --n 1000 --seed 7 --out data/train.jsonl

# Also render the same samples as Markdown for human review
uv run python -m mathgen.cli --n 20 --seed 7 \
    --out data/review.jsonl --markdown-out data/review.md

# Generate only specific sources / a fixed difficulty
uv run python -m mathgen.cli --n 200 --difficulty hard \
    --sources quadratic.inequality_two_roots,inequality.linear_inequality
```

Each generated `*.jsonl` row:

```json
{"source": "...", "messages": [{"role":"user",...},{"role":"assistant",...}],
 "answer": "...", "trace": [{"op":"...","text":"...","meta":{...}}],
 "metadata": {"difficulty":"..."}, "verified": true}
```

The assistant content always follows the single dataset-wide format:

```
<think>
step by step derivation, no numbered list, no skipped steps
</think>
#### \boxed{answer}
```

## Implemented domains

| module | sources |
| --- | --- |
| `mathgen.domains.arithmetic_core` | integer add/sub (carry/borrow), multi-addend & signed running sums, long mult/div, fractions, decimals, powers, radicals, order of operations, sign rules, gcd/lcm, prime factorization, percent/proportion |
| `mathgen.domains.expression_rewrite_core` | collect like terms, distribute, expand, factor trinomial, exponent rules |
| `mathgen.domains.equation_inequality_core` | one-/multi-step linear, parentheses, variable-on-both-sides, linear inequality (sign-flip), **2×2 linear systems by elimination**, **quadratic formula** |
| `mathgen.domains.quadratic_schema` | quadratic factoring + inequalities: two distinct roots, double root, no real root (incl. ℝ / ∅ / single-point / open vs closed endpoints) |
| `mathgen.domains.functions_core` | function evaluation, composite function f(g(x)) |
| `mathgen.domains.sequences_core` | arithmetic nth term, arithmetic series sum, geometric nth term |

Verification (`mathgen/verify.py`) uses exact arithmetic (`int`, `Fraction`,
`Decimal`) and `sympy` for symbolic equivalence and inequality solution sets.
Sample-level discard rules (`mathgen/validate.py`) reject anything that fails
verification, has an empty trace/answer, a numbered list, a dirty renderer
fragment, a boxed answer that disagrees with the `answer` field, or a boxed
answer that is **not actually derived in the reasoning** (the "no skipped steps"
guard: the final answer must appear in the `<think>` derivation).

## Data lineage

Every produced file is traceable one level up and one level down (`AGENTS.md`):

* `<file>.jsonl.lineage.json` — sidecar: producer (tool, version, git commit,
  command, seed, config, sources, code modules), upstream `inputs` (the spec
  docs), and the growing list of downstream `consumed_by` entries.
* Markdown previews written with `--markdown-out` also receive a lineage sidecar
  and record the source JSONL as an upstream input.
* `data/lineage/manifest.jsonl` — append-only log of every produce/consume event.

```bash
# Inspect provenance of a file
uv run python -m mathgen.cli --trace data/train.jsonl

# Record that a downstream step consumed a file
uv run python -m mathgen.cli --out data/train.jsonl --consumed-by train_sft.py
```

## Project layout

```
mathgen/
  core.py          # TraceStep / Sample / make_sample, JSON encoding
  formatting.py    # the single shared expression formatter (no ad-hoc strings)
  config.py        # Difficulty levels, GenConfig
  verify.py        # sympy-backed verification helpers
  validate.py      # des_instruct.md sec 9 discard rules
  lineage.py       # data provenance (up/down one level)
  registry.py      # merges domain registries, sampling, self-test
  cli.py           # command-line entry point
  domains/         # one module per domain, each exposing REGISTRY
```
