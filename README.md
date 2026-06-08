# Compute_Cot — 可验证、可控难度的数学推理数据生成器

`Compute_Cot` 程序化地生成**高质量、自动校验、难度可控**的数学训练数据，专门用于
教一个**较弱的 base 模型**掌握基础算术与符号演绎能力。它不是"看起来像数学题的文本
生成器"——每一条样本都带有：

- 一段**逐步推演**的 `<think>` 过程（每行对应一个有意义的符号操作，不跳步）；
- 一个**机器可读、可校验**的最终答案；
- 一份**结构化 trace**（每步的算子、文本、元信息），便于统计、调试、做课程学习；
- 一个**自动校验位** `verified=true`（用 `int`/`Fraction`/`Decimal`/`sympy` 精确验证，
  未通过的样本在落盘前就被丢弃）。

> 设计规格见 [`docs/des_instruct.md`](docs/des_instruct.md)（数据契约与丢弃规则）与
> [`docs/design.md`](docs/design.md)（符号原语分类）。实现进度见 [`docs/PROGRESS.md`](docs/PROGRESS.md)。

---

## 快速上手

环境（uv，安装在本目录、缓存也在本目录，见 `AGENTS.md`）：

```bash
export UV_CACHE_DIR="$PWD/.uv_cache"
export UV_PROJECT_ENVIRONMENT="$PWD/.venv"
uv sync
```

常用命令：

```bash
# 列出全部可用 source
uv run python -m mathgen.cli --list-sources

# 验证每个生成器都能产出合规样本（验收用）
uv run python -m mathgen.cli --self-test --self-test-per-source 100

# 生成一个数据集（固定 --seed 可复现）
uv run python -m mathgen.cli --n 1000 --seed 7 --out data/train.jsonl

# 同时导出 Markdown 供人工抽查
uv run python -m mathgen.cli --n 20 --seed 7 --out data/review.jsonl --markdown-out data/review.md

# 只生成指定 source / 固定难度
uv run python -m mathgen.cli --n 200 --difficulty hard \
    --sources quadratic.inequality_two_roots,inequality.linear_inequality
```

CLI 主要参数：`--n`（条数）、`--seed`（复现）、`--sources`（逗号分隔白名单）、
`--difficulty {easy,medium,hard,mixed}`、`--cycle`（轮询而非加权采样）、
`--list-sources`、`--self-test`、`--trace <file>`（看数据血缘）。

---

## 输出格式

每行一个 JSON 样本，字段固定如下：

```json
{
  "source": "arithmetic.integer_addition_carry",
  "messages": [
    {"role": "user", "content": "Compute 2824+859."},
    {"role": "assistant", "content": "<think>\n...逐步推演...\n</think>\n#### \\boxed{3683}"}
  ],
  "answer": "3683",
  "trace": [{"op": "add_digit", "text": "...", "before": null, "after": null, "meta": {...}}],
  "metadata": {"difficulty": "easy", ...},
  "verified": true
}
```

assistant 内容**全数据集统一**一种格式，不混用：

```
<think>
逐步推演，每行一个有意义的符号操作；无编号列表；无跳步
</think>
#### \boxed{answer}
```

硬约束：`<think>`/`</think>` 单独成行；`####` 后只放最终答案（不带解释）；boxed 答案
必须等于 `answer` 字段，且必须在 `<think>` 中被真正推导出来（"无跳步"守卫）。

---

## 完整数据流水线

`scripts/generate_data.sh` 给出一套现成的 5 阶段课程 + 故意构造的 OOD 测试集
（约 575k 样本）：

```bash
bash scripts/generate_data.sh all     # 全部
bash scripts/generate_data.sh train   # 仅训练集（5 阶段）
bash scripts/generate_data.sh val     # 验证集
bash scripts/generate_data.sh test    # 测试集（ID + OOD）
```

| split | 规模 | 说明 |
|-------|------|------|
| `train/s1_arithmetic` | 150k | 整数四则、乘方、根式、运算顺序 |
| `train/s2_fractions` | 120k | 分数小数、化简、换算、百分比 |
| `train/s3_algebra` | 100k | 表达式变形、指对律 |
| `train/s4_equations` | 100k | 一/二次方程与不等式 |
| `train/s5_broad` | 30k | 全部 source 低比例混入（防遗忘） |
| `val/val` | 25k | 同源不同 seed |
| `test/id_test` | 10k | 分布内泛化 |
| `test/extrap_ood` | 8k | 数值范围外推（更大位数） |
| `test/template_ood` | 7k | 训练未见过的问法模板 |

> 注：`generate_data.sh` 默认配比是手工硬编码的"按主题分桶"，并**不含跨 split 去重**；
> 不同 split 仅靠不同 seed 区分，小空间题目可能产生重合。若用于严格评测，请在生成后
> 自行做全局去重与无泄漏切分。下游若需"难度爬升 / 动态配比"，应在训练采样侧实现——
> 生成器只负责提供打好标签、可寻址（按 `source`/`difficulty`/`trace`）的素材池。

---

## 已实现领域（268 sources）

涵盖 arithmetic / expression_rewrite / equation / inequality / quadratic / function /
trigonometry / exp_log / sequences / number_theory / comparison / set_logic /
domain_assumption / case_split / combinatorics / complex / vectors / matrices /
polynomial / analytic_geometry / differentiation / limits / integration /
plane_geometry / word_problem / ratio_percent，以及若干 `*_schema`（结构化题型）。
完整 source 名用 `--list-sources` 查看，逐领域覆盖见 `docs/PROGRESS.md`。

---

## 代码结构

```
mathgen/
  cli.py           # 命令行入口：采样 → 校验 → 写 JSONL + 血缘
  registry.py      # 合并各领域 REGISTRY，驱动采样、self-test
  config.py        # 难度档位、GenConfig
  core.py          # TraceStep / Sample / make_sample，JSON 编码
  formatting.py    # 唯一的表达式渲染助手（禁止到处手写字符串拼接）
  verify.py        # sympy / 精确算术的校验工具
  validate.py      # des_instruct.md 第 9 节的丢弃规则
  lineage.py       # 数据血缘（上下各一层可追溯）
  domains/         # 每个领域一个模块，各自暴露 REGISTRY
scripts/
  generate_data.sh # 全流水线生成脚本
  check_sources.py # 验收：全 source 跑 verify + validate + 脏片段扫描
  generate_ood.py  # OOD 测试集生成
  apply_templates.py / review_*.py # 模板与人工复查辅助
```

### 新增一个 source

1. 在 `mathgen/domains/<领域>.py` 写一个 `gen_xxx(rng, cfg) -> Sample`，**所有渲染走
   `formatting.py` 的助手**（不要手写字符串拼接），推演要逐步、可被 `verify.py` 校验；
2. 注册进该模块的 `REGISTRY`（并确保 `registry.py` 引入了该模块）；
3. 跑验收，必须全 PASS：
   ```bash
   uv run python scripts/check_sources.py        # verify=0 / validate=0 / blemish=0
   ```

---

## 质量保证

- **逐样本自动校验**：算术用 `int`/`Fraction`/`Decimal` 精确计算，符号/方程/不等式/
  导数用 `sympy`；校验失败、空 trace/答案、脏片段、跳步、答案与 boxed 不一致等一律丢弃
  （规则见 `docs/des_instruct.md` 第 9 节）。
- **验收脚本** `scripts/check_sources.py` 对全部 268 source 跑 verify + validate +
  脏片段扫描，三项全 0 才算通过。
- **已知局限**：答案级 verify 不保证 `<think>` 中途每一步都对——历史上出现过"答案对、
  过程错"的渲染缺陷（如 decimal 除法的假整数商、分数除法负号断层、分段函数 `+ -` 脏片段，
  均已修复）。建议下游对生成器再补一层**步级数值核算**与**符号/边界定向探测**，因为随机
  抽样会漏掉只在特定符号/边界触发的缺陷。

---

## 数据血缘

每个产出文件都可上下各追溯一层：`<file>.jsonl.lineage.json` 记录生产者（工具、版本、
git commit、命令、seed、配置、source、代码模块）与上游 `inputs`、下游 `consumed_by`；
`data/lineage/manifest.jsonl` 是 append-only 的全量产/用事件日志。

```bash
uv run python -m mathgen.cli --trace data/train.jsonl              # 看某文件的血缘
uv run python -m mathgen.cli --out data/train.jsonl --consumed-by train_sft.py  # 记录下游消费
```
