#!/bin/bash
# ============================================================================
# MathGen 训练/测试数据生成脚本
#
# 用法:
#   bash scripts/generate_data.sh          # 生成全部数据
#   bash scripts/generate_data.sh train     # 只生成训练集
#   bash scripts/generate_data.sh test      # 只生成测试集
#
# 输出目录: data/train/, data/val/, data/test/
# 格式: JSONL (每行一个样本，结构见 docs/des_instruct.md sec 10)
# ============================================================================
set -euo pipefail

DATA_DIR="data"
TRAIN_DIR="$DATA_DIR/train"
VAL_DIR="$DATA_DIR/val"
TEST_DIR="$DATA_DIR/test"

mkdir -p "$TRAIN_DIR" "$VAL_DIR" "$TEST_DIR"

# ------------------------------------------------------------------
# 阶段 1: 算术原语 (150k)
#   整数四则运算, 符号规则, 运算顺序, 乘方, 根式
# ------------------------------------------------------------------
gen_s1() {
    echo "=== 阶段 1: 算术原语 (150k) ==="
    local sources=(
        arithmetic.integer_addition_carry
        arithmetic.integer_subtraction_borrow
        arithmetic.integer_add_many
        arithmetic.integer_mixed_add_sub
        arithmetic.long_multiplication
        arithmetic.long_division_exact
        arithmetic.long_division_remainder
        arithmetic.long_division_zero_in_quotient
        arithmetic.sign_rules_multiplication
        arithmetic.powers
        arithmetic.radical_simplification
        arithmetic.order_of_operations_basic
        arithmetic.order_of_operations_parentheses
        arithmetic.order_of_operations_nested
    )
    uv run python -m mathgen.cli \
        --n 150000 --seed 42 --out "$TRAIN_DIR/s1_arithmetic.jsonl" \
        --sources "$(IFS=,; echo "${sources[*]}")" --cycle
}

# ------------------------------------------------------------------
# 阶段 2: 分数小数 (120k)
#   分数四则运算, 小数四则运算, 化简, 换算, 近似, 科学记数法
# ------------------------------------------------------------------
gen_s2() {
    echo "=== 阶段 2: 分数小数 (120k) ==="
    local sources=(
        arithmetic.fraction_addition
        arithmetic.fraction_subtraction
        arithmetic.fraction_multiplication
        arithmetic.fraction_division
        arithmetic.fraction_simplification
        arithmetic.mixed_number_to_improper
        arithmetic.improper_to_mixed_number
        arithmetic.decimal_addition
        arithmetic.decimal_subtraction
        arithmetic.decimal_multiplication
        arithmetic.decimal_division_by_integer
        arithmetic.decimal_division_by_decimal
        arithmetic.rounding_to_place_value
        arithmetic.scientific_notation_convert
        ratio_percent.percent_to_fraction_decimal
        ratio_percent.percent_change
        ratio_percent.percent_find_part_or_whole
        ratio_percent.proportion_solve
    )
    uv run python -m mathgen.cli \
        --n 120000 --seed 43 --out "$TRAIN_DIR/s2_fractions.jsonl" \
        --sources "$(IFS=,; echo "${sources[*]}")" --cycle
}

# ------------------------------------------------------------------
# 阶段 3: 代数变形 (100k)
#   合并同类项, 分配律, 展开, 因式分解, 有理/根式/指对化简
# ------------------------------------------------------------------
gen_s3() {
    echo "=== 阶段 3: 代数变形 (100k) ==="
    local sources=(
        expression_rewrite.collect_like_terms
        expression_rewrite.distribute
        expression_rewrite.expand_binomial_product
        expression_rewrite.expand_perfect_square
        expression_rewrite.factor_trinomial
        expression_rewrite.factor_trinomial_a_not_1
        expression_rewrite.factor_difference_of_squares
        expression_rewrite.exponent_product
        expression_rewrite.rational_simplify
        expression_rewrite.radical_simplify
        expression_rewrite.absolute_value_simplify
        expression_rewrite.collect_like_terms
        exp_log.exponent_laws
        exp_log.negative_exponent
        exp_log.fractional_exponent
        exp_log.logarithm_laws
        comparison.radical_compare
        comparison.power_compare
    )
    uv run python -m mathgen.cli \
        --n 100000 --seed 44 --out "$TRAIN_DIR/s3_algebra.jsonl" \
        --sources "$(IFS=,; echo "${sources[*]}")" --cycle
}

# ------------------------------------------------------------------
# 阶段 4: 方程不等式 (100k)
#   一次方程, 二次方程, 不等式, 方程组, 配方, 判别式
# ------------------------------------------------------------------
gen_s4() {
    echo "=== 阶段 4: 方程不等式 (100k) ==="
    local sources=(
        equation.one_step_linear
        equation.multi_step_linear
        equation.equation_with_parentheses
        equation.variable_on_both_sides
        equation.linear_equation_fraction_coeff
        equation.systems_linear_2x2
        equation.system_substitution_method
        equation.quadratic_formula
        equation.completing_the_square
        equation.rational_equation
        equation.radical_equation
        equation.absolute_value_equation
        inequality.linear_inequality
        inequality.compound_inequality
        inequality.rational_inequality
        inequality.absolute_value_inequality
        quadratic.equation_factor
        quadratic.inequality_two_roots
        quadratic.inequality_double_root
        quadratic.inequality_no_real_root
        quadratic.discriminant_classification
        quadratic.quadratic_vertex_axis_range
        quadratic.quadratic_sign_chart
        quadratic.quadratic_function_positive_negative_interval
        quadratic.quadratic_parameter_discriminant_basic
    )
    uv run python -m mathgen.cli \
        --n 100000 --seed 45 --out "$TRAIN_DIR/s4_equations.jsonl" \
        --sources "$(IFS=,; echo "${sources[*]}")" --cycle
}

# ------------------------------------------------------------------
# 阶段 5: 广域回放 (30k)
#   所有 source 的低比例混入，防止遗忘，保持格式多样性
# ------------------------------------------------------------------
gen_s5() {
    echo "=== 阶段 5: 广域回放 (30k) ==="
    uv run python -m mathgen.cli \
        --n 30000 --seed 46 --out "$TRAIN_DIR/s5_broad.jsonl" \
        --difficulty mixed
}

# ------------------------------------------------------------------
# 验证集 (25k)
#   同源不同 seed，用于调参和 early stopping
# ------------------------------------------------------------------
gen_val() {
    echo "=== 验证集 (25k) ==="
    uv run python -m mathgen.cli \
        --n 25000 --seed 99 --out "$VAL_DIR/val.jsonl" \
        --difficulty mixed
}

# ------------------------------------------------------------------
# ID 测试集 (10k)
#   同源不同 seed+template，验证分布内泛化
# ------------------------------------------------------------------
gen_test_id() {
    echo "=== ID 测试集 (10k) ==="
    uv run python -m mathgen.cli \
        --n 10000 --seed 999 --out "$TEST_DIR/id_test.jsonl" \
        --difficulty mixed
}

# ------------------------------------------------------------------
# OOD 外推测试 (8k)
#   数值范围超出训练分布 (更大位数/更复杂数字)
#   由独立脚本生成，修改 GenConfig 的参数范围
# ------------------------------------------------------------------
gen_test_extrap() {
    echo "=== OOD 外推测试 (8k) ==="
    uv run python scripts/generate_ood.py \
        --n 8000 --seed 777 --out "$TEST_DIR/extrap_ood.jsonl" \
        --mode extrap
}

# ------------------------------------------------------------------
# OOD 模板测试 (7k)
#   使用训练中未出现的问法模板
# ------------------------------------------------------------------
gen_test_template() {
    echo "=== OOD 模板测试 (7k) ==="
    uv run python scripts/generate_ood.py \
        --n 7000 --seed 888 --out "$TEST_DIR/template_ood.jsonl" \
        --mode template
}

# ==================================================================
# 主流程
# ==================================================================
case "${1:-all}" in
    train)
        gen_s1 && gen_s2 && gen_s3 && gen_s4 && gen_s5
        ;;
    test)
        gen_test_id && gen_test_extrap && gen_test_template
        ;;
    val)
        gen_val
        ;;
    all)
        gen_s1 && gen_s2 && gen_s3 && gen_s4 && gen_s5
        gen_val
        gen_test_id && gen_test_extrap && gen_test_template
        ;;
    *)
        echo "用法: $0 {train|test|val|all}"
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "生成完毕。数据分布:"
echo "============================================"
echo "训练集:"
wc -l "$TRAIN_DIR"/*.jsonl 2>/dev/null | tail -1
echo "验证集:"
wc -l "$VAL_DIR"/*.jsonl 2>/dev/null | tail -1
echo "测试集:"
wc -l "$TEST_DIR"/*.jsonl 2>/dev/null | tail -1
