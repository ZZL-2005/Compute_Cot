你是一个 coding agent。你的任务不是随便生成数学题，而是实现一个高质量、可验证、可控难度的数学训练数据生成器。数据用于训练弱 base model 的基础数学符号演绎能力，因此每条样本都必须具备清晰的逐步推演过程、稳定的答案格式和可自动校验的 ground truth。
题目/data/zilu/Compute_Cot/docs/design.md
## 1. 核心目标

请实现程序化数学题生成器，要求每条样本都包含：

1. 题目 `user.content`
2. 标准解答 `assistant.content`
3. 结构化推演轨迹 `trace`
4. 最终答案 `answer`
5. 元信息 `metadata`
6. 自动校验结果 `verified=true`

最重要的是：
**assistant 的 `<think>` 字段必须是逐步推演，而不是一句话跳到答案。**

推荐 assistant 格式：

```text
<think>
Step-by-step derivation in English.
Each line should correspond to a meaningful symbolic operation.
No numbered list such as 1. 2. 3.
No hidden leaps.
No unsupported conclusion.
</think>
#### \boxed{answer}
```

如果 evaluator 不适合 `\boxed{}`，可以改成：

```text
<think>
...
</think>
#### answer
```

但同一个数据集内必须保持一种格式，不允许混用。

---

## 2. 每条样本的质量要求

每条样本必须满足以下条件。

### 2.1 题目必须明确

题目不能有歧义。所有变量、条件、目标都必须清楚。

好例子：

```text
Solve x^2 - 5x + 6 > 0.
```

坏例子：

```text
Solve the quadratic.
```

坏例子缺少具体表达式，不能生成。

---

### 2.2 必须有唯一、可验证的标准答案

每条题目必须有确定答案。答案可以是数字、表达式、方程解、区间、集合、导数、坐标等，但必须能由程序校验。

允许：

```text
#### \boxed{7459}
#### \boxed{x=2}
#### \boxed{(-∞, 2) ∪ (3, +∞)}
#### \boxed{6x^2 - 4}
```

不允许：

```text
#### \boxed{It depends}
#### \boxed{many answers}
```

除非题型本身明确允许参数化答案，例如三角方程通解。

---

### 2.3 `<think>` 必须逐步推演

`<think>` 不是装饰字段。它必须展示从题目到答案的中间步骤。

例如多位加法不能只写：

```text
Compute directly: 6568+891=7459.
```

必须写出按位加法和进位：

```text
Align 6568 and 891 by place value, then add from right to left.
At the ones place: 8+1=9, so write 9 with no carry.
At the tens place: 6+9=15, so write 5 and carry 1 to the next place.
At the hundreds place: 5+8+1=14, so write 4 and carry 1 to the next place.
At the thousands place: 6+0+1=7, so write 7 with no carry.
Therefore, 6568+891=7459.
```

例如二次不等式不能只写：

```text
The solution is outside the roots.
```

必须写清：

```text
Factor the quadratic: x^2 - 5x + 6 = (x - 2)(x - 3).
The zeros are x=2 and x=3.
These zeros split the number line into (-∞, 2), (2, 3), and (3, +∞).
The leading coefficient is positive, so the parabola opens upward.
Therefore, the quadratic is positive outside the two roots and negative between them.
Because the inequality is strict, the roots are not included.
Thus the solution set is (-∞, 2) ∪ (3, +∞).
```

---

## 3. 推演步骤的具体要求

### 3.1 每一步必须是有效数学操作

每一行 reasoning 应该对应一个可解释的操作，例如：

```text
align_digits
add_digit
carry
borrow
partial_product
bring_down
reduce_fraction
find_lcm
distribute
collect_like_terms
factor
find_roots
split_number_line
determine_sign_intervals
check_domain
verify_solution
differentiate_power
apply_chain_rule
```

不要写空话：

```text
Now solve it.
Obviously the answer is ...
We can see that ...
By simple math ...
```

---

### 3.2 不能跳过关键步骤

以下题型必须显式展开关键步骤。

#### 加法

必须写：

```text
从低位到高位
每一位相加
是否进位
最终合成答案
```

#### 减法

必须写：

```text
从低位到高位
是否借位
跨 0 借位时如何传递
每一位相减
最终合成答案
```

#### 乘法

必须写：

```text
按乘数每一位生成 partial product
每个 partial product 的计算
十位、百位对应补 0
partial products 相加
```

#### 除法

必须写：

```text
选择当前 prefix
估商
回乘
相减
落下一位
是否有余数
```

#### 分数

必须写：

```text
通分或约分原因
公分母 / gcd
分子计算
最终化简
```

#### 方程

必须写：

```text
两边同时做什么操作
为什么解保持等价
最终代回检查，尤其是分式方程、根式方程、对数方程
```

#### 不等式

必须写：

```text
两边乘除负数时必须说明不等号翻转
二次/分式不等式必须写零点、区间、符号判断、端点是否包含
```

#### 定义域

涉及以下内容时必须显式写定义域：

```text
分母不能为 0
偶次根号内非负
log 真数大于 0
tan 中 cos 不为 0
两边平方后需要检查增根
```

---

## 4. 答案格式要求

默认使用：

```text
<think>
...
</think>
#### \boxed{answer}
```

要求：

1. `<think>` 和 `</think>` 必须单独成行。
2. `####` 后面必须是最终答案。
3. `answer` 字段必须保存可机器读取的 raw answer。
4. `assistant.content` 中的 boxed answer 必须和 `answer` 字段一致。
5. 不允许多个互相矛盾的 final answer。
6. 不允许在 `####` 后写解释。

例子：

```json
{
  "answer": "7459",
  "messages": [
    {
      "role": "assistant",
      "content": "<think>\nAlign 6568 and 891 by place value, then add from right to left.\nAt the ones place: 8+1=9, so write 9 with no carry.\nAt the tens place: 6+9=15, so write 5 and carry 1 to the next place.\nAt the hundreds place: 5+8+1=14, so write 4 and carry 1 to the next place.\nAt the thousands place: 6+0+1=7, so write 7 with no carry.\nTherefore, 6568+891=7459.\n</think>\n#### \\boxed{7459}"
    }
  ]
}
```

---

## 5. 表达式渲染质量要求

必须实现统一 formatter，禁止到处手写字符串拼接。

必须避免以下脏格式：

```text
-4×(6)+-9
x + -3
-12--7
1+-2
sqrt(72)=6sqrt(2) 但没有解释为什么
```

应该渲染为：

```text
-4×6 - 9
x - 3
-12 - (-7)
1 - 2
sqrt(72)=sqrt(36×2)=6sqrt(2)
```

负数参与减法时必须加括号：

```text
1 - (-2)
-12 - (-7)
```

加负数时应改写成减法：

```text
x + (-3)  →  x - 3
5 + (-8)  →  5 - 8
```

分数应规范化：

```text
2/4     → 1/2
-1/-2   → 1/2
1/-2    → -1/2
```

---

## 6. 结构化 trace 要求

每条样本必须保存结构化 trace，不能只保存自然语言。

TraceStep 格式：

```json
{
  "op": "add_digit",
  "text": "At the tens place: 6+9=15, so write 5 and carry 1 to the next place.",
  "before": null,
  "after": null,
  "meta": {
    "place": "tens",
    "digits": [6, 9],
    "carry_in": 0,
    "write": 5,
    "carry_out": 1
  }
}
```

每条 trace 至少包含：

```text
op
text
```

推荐包含：

```text
before
after
meta
```

trace 的作用是：

1. 方便 debug 题目生成器。
2. 方便统计每种数学操作出现频率。
3. 方便未来做课程学习。
4. 方便定位模型到底在哪类 op 上失败。

---

## 7. verifier 要求

所有样本必须自动校验。未校验或校验失败的样本不能写入最终数据。

### 7.1 算术

使用 Python 精确计算：

```text
int
fractions.Fraction
decimal.Decimal
```

不允许使用浮点误差大的方式校验精确题。

### 7.2 表达式化简

使用 sympy 校验等价性：

```python
sympy.simplify(before - after) == 0
```

### 7.3 方程

必须代回原方程验证解。

分式方程、根式方程、对数方程必须检查定义域。

### 7.4 不等式

必须验证解集。对于二次不等式，可以由构造参数推导解集，也可以用符号/抽样双重检查。

二次不等式必须正确处理：

```text
两个不同实根
重根
无实根
开口向上
开口向下
严格不等式
非严格不等式
空集
全体实数
单点解
```

### 7.5 导数

使用 sympy.diff 校验。

### 7.6 几何、数列、概率

使用 exact arithmetic 或 sympy 校验。

---

## 8. 题目生成质量要求

### 8.1 不要只生成 easy case

每个 source 都应该支持 difficulty：

```text
easy
medium
hard
```

例如加法：

```text
easy: 两三位数，最多一次进位
medium: 三四位数，多次进位
hard: 四到六位数，连续进位，含多个 9
```

例如减法：

```text
easy: 无借位或一次借位
medium: 多次借位
hard: 跨 0 连续借位，如 1000-376
```

例如二次不等式：

```text
easy: a=1，两个整数根，可直接因式分解
medium: a≠1，开口可能向下，带等号
hard: 重根、无实根、分数根、空集、全体实数、单点解
```

### 8.2 每个 source 要覆盖正反例

不要只覆盖一种模式。

例如比较大小不能只生成：

```text
1/2 < 2/3
```

也要生成：

```text
5/6 > 7/9
-3/4 < -2/5
sqrt(8) < 3
```

例如二次不等式不能只生成：

```text
x^2 - 5x + 6 > 0
```

也要生成：

```text
x^2 - 5x + 6 <= 0
-(x-2)(x-5) > 0
(x-3)^2 >= 0
(x-3)^2 < 0
x^2 + x + 1 > 0
```

---

## 9. 丢弃样本规则

遇到以下情况必须丢弃并重新采样：

1. 题目有歧义。
2. answer 为空。
3. trace 为空。
4. verifier 失败。
5. assistant 格式不符合要求。
6. reasoning 中出现明显数学错误。
7. renderer 出现脏格式：

   * `+-`
   * `+ -`
   * `--` 用作错误减法拼接，例如 `-12--7`
8. 最终答案和 metadata 中的 answer 不一致。
9. 题目难度与 difficulty 设置明显不符。
10. 解答跳过关键步骤。
11. 需要定义域检查但没有检查。
12. 需要端点开闭判断但没有判断。

---

## 10. 推荐 JSONL 输出格式

每行一个样本：

```json
{
  "source": "routine.quadratic.inequality_two_distinct_roots",
  "messages": [
    {
      "role": "user",
      "content": "Solve x^2 - 5x + 6 > 0."
    },
    {
      "role": "assistant",
      "content": "<think>\nFactor the quadratic: x^2 - 5x + 6 = (x - 2)(x - 3).\nThe zeros are x=2 and x=3.\nThese zeros split the number line into (-∞, 2), (2, 3), and (3, +∞).\nThe leading coefficient is positive, so the parabola opens upward.\nTherefore, the quadratic is positive outside the two roots and negative between them.\nBecause the inequality is strict, the roots are not included.\nThus the solution set is (-∞, 2) ∪ (3, +∞).\n</think>\n#### \\boxed{(-∞, 2) ∪ (3, +∞)}"
    }
  ],
  "answer": "(-∞, 2) ∪ (3, +∞)",
  "trace": [
    {
      "op": "factor_quadratic",
      "text": "Factor the quadratic: x^2 - 5x + 6 = (x - 2)(x - 3).",
      "before": "x^2 - 5x + 6",
      "after": "(x - 2)(x - 3)",
      "meta": {
        "roots": [2, 3]
      }
    },
    {
      "op": "find_zeros",
      "text": "The zeros are x=2 and x=3.",
      "meta": {
        "zeros": [2, 3]
      }
    },
    {
      "op": "split_number_line",
      "text": "These zeros split the number line into (-∞, 2), (2, 3), and (3, +∞)."
    },
    {
      "op": "determine_opening_direction",
      "text": "The leading coefficient is positive, so the parabola opens upward.",
      "meta": {
        "leading_coefficient": 1
      }
    },
    {
      "op": "apply_inequality_operator",
      "text": "Because the inequality is strict, the roots are not included.",
      "meta": {
        "operator": ">"
      }
    }
  ],
  "metadata": {
    "difficulty": "medium",
    "a": 1,
    "roots": [2, 3],
    "operator": ">",
    "answer_type": "interval_union"
  },
  "verified": true
}
```

---

## 11. 重点实现方向

第一阶段不需要实现所有数学领域。优先实现质量最高、最容易验证、最能训练底层能力的领域：

```text
arithmetic_core
expression_rewrite_core
equation_inequality_core
quadratic_function_inequality_schema
```

每个领域宁可少做一些 source，也要保证：

```text
题目干净
推演完整
答案可验
格式稳定
trace 结构化
```

---

## 12. 验收标准

生成器完成后必须通过以下检查：

1. 每个 source 可以独立生成至少 100 条样本。
2. 每条样本 `verified=true`。
3. 每条样本有非空 `trace`。
4. 每条样本有非空 `answer`。
5. 每条 assistant content 符合：

```text
<think>
...
</think>
#### \boxed{...}
```

6. reasoning 中没有步骤编号。
7. reasoning 中没有明显 renderer 脏格式。
8. 所有需要关键步骤的题型都没有跳步。
9. 所有涉及定义域、端点、增根的题都必须检查。
10. 同一个 seed 生成结果可复现。
11. 随机抽查 100 条，不能发现数学错误。
12. 能输出 JSONL，供后续 SFT 直接使用。

---

## 13. 最重要的原则

这个项目不是为了生成“看起来像数学题”的文本，而是为了生成能教会弱模型基础数学操作的训练样本。

因此每条数据都必须体现：

```text
explicit symbolic reasoning
step-by-step derivation
clean answer format
automatic verification
controlled difficulty
structured trace
```

质量优先于数量。
可验证优先于自然语言花样。
推演完整优先于解答简短。
