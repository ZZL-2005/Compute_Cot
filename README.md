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

## Generating training data

The full pipeline produces ~575k samples across train/val/test splits with a
5-stage curriculum and deliberate OOD (out-of-distribution) test sets.

```bash
# One command to generate everything (~30 min on a modern CPU):
bash scripts/generate_data.sh all

# Or generate individual splits:
bash scripts/generate_data.sh train   # 500k training samples (5 stages)
bash scripts/generate_data.sh val     # 25k validation samples
bash scripts/generate_data.sh test    # 25k test samples (ID + OOD)
```

### Data split design

| Split | Size | Description |
|-------|------|-------------|
| `data/train/s1_arithmetic.jsonl` | 150k | Integer ops, powers, radicals, order-of-ops |
| `data/train/s2_fractions.jsonl` | 120k | Fractions, decimals, rounding, percentages |
| `data/train/s3_algebra.jsonl` | 100k | Expression rewrite, exponent/log laws |
| `data/train/s4_equations.jsonl` | 100k | Linear/quadratic equations & inequalities |
| `data/train/s5_broad.jsonl` | 30k | All 260+ sources at low ratio (anti-forgetting) |
| `data/val/val.jsonl` | 25k | Same sources, different seed |
| `data/test/id_test.jsonl` | 10k | In-distribution test (different seed+template) |
| `data/test/extrap_ood.jsonl` | 8k | OOD: larger digit ranges than training |
| `data/test/template_ood.jsonl` | 7k | OOD: unseen question phrasings |

### Curriculum rationale

Stage order is deliberate: the model first masters single-digit arithmetic
algorithms, then fractions/decimals, then symbolic manipulation, and finally
full equation solving. Each stage builds on the operations learned in previous
stages. Difficulty ramps within each stage (easy-heavy early, hard-heavy late).

### OOD design

- **Extrapolation**: arithmetic sources use `difficulty=hard` (5-6 digit operands)
  vs the predominantly easy/medium training distribution.
- **Template OOD**: questions are rephrased with templates never used in training
  (e.g. "Work out X", "Tell me the result of X") to test template-level
  generalisation rather than memorisation of specific prefixes.

## Implemented domains (268 sources, 199 design.md spec items)

| domain | sources | coverage |
|--------|---------|----------|
| `arithmetic` | 28 | integer ops (carry/borrow), long mult/div, fractions, decimals, powers, radicals, order-of-ops, rounding, scientific notation |
| `expression_rewrite` | 11 | collect like terms, distribute, expand (binomial + perfect square), factor (monic, a≠1, difference-of-squares), exponent/rational/radical/absolute-value simplify |
| `equation` | 12 | one-/multi-step linear, parentheses, variable-on-both-sides, fraction-coeff, 2×2 systems (elimination + substitution), quadratic formula, completing the square, rational/radical/absolute-value equations |
| `inequality` | 6 | linear (sign-flip), compound, rational, absolute-value, exponential, logarithmic |
| `quadratic` | 9 | equation-factor, inequalities (two-roots, double-root, no-root), discriminant classification, vertex/axis/range, sign-chart, positive/negative intervals, parameter-discriminant |
| `function` | 9 | evaluation, composite, piecewise, domain, range, inverse, zero, sign, transformation |
| `trigonometry` + `trigonometric_schema` | 12 | special-angle-values (unit-circle derivation), quadrant-sign (CAST), periodicity, Pythagorean identity, simplification, equations, general solutions |
| `exp_log` | 9 | exponent laws, negative/fractional exponents, exponential/log equations, log definition/laws/domain, inverse |
| `sequences` + `sequence_schema` | 13 | arithmetic/geometric nth-term and series-sum, recurrence, sigma-notation, telescoping |
| `number_theory` | 7 | parity, divisibility-rules, prime-factorization, gcd/lcm, Euclidean algorithm, modular-arithmetic, integer-factor-pairs |
| `comparison` | 8 | integer/fraction/decimal/radical/power comparison, sign-of-expression, approximate-value, bound-reasoning |
| `set_logic` | 9 | membership, subset, union/intersection, complement, interval-ops, logic connectives, implication, quantifiers |
| `domain_assumption` | 7 | denominator, radical, log, tangent, square-both-sides, multiply-by-expression, solution-verification |
| `case_split` | 6 | sign, zero-points, absolute-value, piecewise-condition, parameter, merge-results |
| `combinatorics` | 10 | permutation, combination, counting-principle, binomial-coefficient, probability, conditional, independent-events, expectation, mean/median/mode, variance |
| `complex` | 8 | imaginary-unit, add/sub, multiply, division, conjugate, modulus, argument, equation |
| `vectors` | 8 | add/sub, scalar-mult, dot-product, norm, angle, projection, parallel/perpendicular, linear-combination |
| `matrices` | 7 | add/sub, scalar-mult, matrix-mult, det-2×2, det-3×3, inverse-2×2, Cramer's-rule |
| `polynomial` | 7 | degree, synthetic-division, remainder-theorem, factor-theorem, Vieta, rational-root-test, higher-degree-factor |
| `analytic_geometry` + schema | 16 | distance, midpoint, slope, line-equation, point-line-distance, circle-equation, line-circle-intersection, conic-classification, tangent-line |
| `differentiation` + `derivative_schema` | 14 | power-rule, sum/product/quotient/chain-rule, derivative-simplification, tangent-line, monotonicity, critical-points, local/closed-interval extrema |
| `limits` | 2 | direct-substitution, factor-cancel |
| `integration` | 2 | power-integral, definite-integral |
| `plane_geometry` | 8 | triangle/rectangle/circle area/perimeter, Pythagorean, similar-triangles, angle-sum, polygon-angle-sum, sector |
| `word_problem` | 14 | part-whole, state-change, comparison, multiplicative, sum-difference, price-quantity, rate-time-distance, work-rate, percent, average, age, mixture, geometry, two-variable-linear |
| `ratio_percent` | 8 | ratio-simplify, proportion, percent-to-fraction/decimal, percent-change, direct/inverse-proportion, rate-unit-conversion |

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
