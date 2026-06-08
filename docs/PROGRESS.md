# mathgen 实现进度

> 目标(2026-06-08 起):把 `docs/design.md` 全部领域**详细、全面**实现;积分(24)、极限(23)只做最简版即可。
> 每个生成器硬性要求:① sympy/精确验证 `verified=True` ② 无跳步(末步落在 box 答案上,且 `validate.py` 校验答案出现在 `<think>`) ③ 渲染只走 `formatting.py` 助手,无脏片段。
>
> 验收脚本:`self_test`(验证)+ 全 source 跑 `validate_sample`(丢弃规则)。两者都过才算完成。

## 总览状态

| design.md 领域 | 状态 | 模块 | 备注 |
|---|---|---|---|
| 0 symbol_parsing | 隐式 | formatting.py | 通过统一渲染体现,不单独出题 |
| 1 arithmetic | ✅ 完成 | arithmetic_core | |
| 2 expression_rewrite | ✅ 完成 | expression_rewrite_core | 8 source(含 rational/radical/abs) |
| 3 equations | ✅ 完成 | equation_inequality_core + equations_advanced_core | 线性/二次/系统/公式 + rational/radical/abs(exp/log 在 exp_log) |
| 4 inequalities | ✅ 完成 | equation_inequality_core + inequalities_advanced_core | linear/compound/abs/rational/exp/log;区间运算在 set_logic |
| 5 functions | ✅ 完成 | functions_core | 9 source(eval/composite/piecewise/domain/range/inverse/zero/sign/transform) |
| 6 trigonometry | ✅ 完成 | trigonometry_core | 6 source(sympy 精确值) |
| 7 analytic_geometry | ✅ 完成 | analytic_geometry_core | 8 source |
| 8 differentiation | ✅ 完成 | calculus_core | 8 source(全套求导) |
| 9 number_theory | ✅ 完成 | arithmetic_core + number_theory_core | gcd/lcm/质因数 + parity/divisibility/mod/factor_pairs |
| 10 ratio_percent | 🟡 部分 | arithmetic_core(+ ratio_core) | 补 ratio_simplify/direct/inverse/unit_rate |
| 11 comparison | ✅ 完成 | comparison_core | 8 source |
| 12 domain_assumption | ⬜ 待做 | domain_assumption_core | |
| 13 case_split | ⬜ 待做 | case_split_core | |
| 14 set_logic | ✅ 完成 | set_logic_core | 9 source |
| 15 exp_log | ✅ 完成 | exp_log_core | 9 source |
| 16 sequences | ✅ 完成 | sequences_core | 7 source(含 geom_sum/recurrence/sigma/telescoping) |
| 17 complex | ✅ 完成 | complex_core | 8 source |
| 18 vectors | ✅ 完成 | vectors_core | 8 source |
| 19 matrices | ✅ 完成 | matrices_core | 7 source |
| 20 combinatorics/prob/stats | ✅ 完成 | combinatorics_core | 10 source |
| 21 plane_geometry | ✅ 完成 | geometry_formula_core | 8 source |
| 22 polynomial_advanced | ✅ 完成 | polynomial_advanced_core | 7 source |
| 23 limits | ✅ 最简完成 | calculus_core | direct_substitution + factor_cancel |
| 24 integration | ✅ 最简完成 | calculus_core | power_integral + definite_basic |
| 25 quadratic schema | ✅ 完成 | quadratic_schema | |
| 26 rational_inequality_schema | ⬜ 待做 | inequalities 扩展 | |
| 27 absolute_value_schema | ⬜ 待做 | abs/inequalities | |
| 28 function_property_schema | ⬜ 待做 | functions_core 扩展 | |
| 29 trigonometric_schema | ⬜ 待做 | trigonometry_core | |
| 30 sequence_schema | ⬜ 待做 | sequences_core | |
| 31 analytic_geometry_schema | ⬜ 待做 | analytic_geometry_core | |
| 32 derivative_schema | ⬜ 待做 | calculus_core | |
| 33 word_problem_bridge | ⬜ 待做 | word_problem_core | |

图例:✅ 完成并通过验收 / 🟡 进行中或部分 / ⬜ 待做

## 基线(本目标开始前)
50 sources,全过 self-test + validate_sample,可复现。commit `3067410`。

## 变更日志
- 2026-06-08: 建立本进度文档。
- 2026-06-08 批次1(commit 见下): exp_log(9) + sequences补全(+4) + number_theory_core(4) +
  comparison(8) + set_logic(9)。新增 `scripts/check_sources.py` 验收脚本。
  全部 PASS(verify + validate + 脏片段扫描)。sources: 50 → 84。
- 2026-06-08 批次2: trigonometry(6) + analytic_geometry(8) + calculus_core(微分8 + 极限2 + 积分2)。
  全部 PASS。sources: 84 → 110。
- 2026-06-08 批次3: complex(8) + vectors(8) + matrices(7)。全部 PASS。sources: 110 → 133。
- 2026-06-08 批次4: combinatorics(10) + plane_geometry(8) + polynomial_advanced(7)。全部 PASS。sources: 133 → 158。
- 2026-06-08 批次5: functions补全(+7) + expression_rewrite补全(+3) + equations_advanced(3) + inequalities_advanced(5)。全部 PASS。sources: 158 → 176。
