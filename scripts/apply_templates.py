#!/usr/bin/env python3
"""Batch-apply question template rotation to low-diversity generators."""
import re, sys

BASE = '/data/zilu/Compute_Cot/mathgen/domains'

# (filename, old_line_fragment, replacement_line_string)
# Each replacement is a lambda that takes the match groups and returns the new line
REPLACEMENTS = [
    # === calculus_core.py ===
    ('calculus_core.py',
     r'(\s+)f"Find the indefinite integral ∫ (\{a\})x\^(\{n\}) dx\."',
     r'\1pick_template(rng, f"Find the indefinite integral ∫ \2x^\3 dx.", f"Integrate ∫ \2x^\3 dx.", f"Compute ∫ \2x^\3 dx.", f"Evaluate the indefinite integral ∫ \2x^\3 dx."),'),

    ('calculus_core.py',
     r'(\s+)f"Evaluate the definite integral of (\{a\})x\^(\{n\}) from 0 to (\{b\})\."',
     r'\1pick_template(rng, f"Evaluate the definite integral of \2x^\3 from 0 to \4.", f"Compute ∫_0^\4 \2x^\3 dx.", f"Find the definite integral ∫_0^\4 \2x^\3 dx.", f"Evaluate ∫_0^\4 \2x^\3 dx."),'),

    # === combinatorics_core.py ===
    ('combinatorics_core.py',
     r'(\s+)f"Compute the number of permutations P\(\{n\}, \{r\}\)."',
     r'\1pick_template(rng, f"Compute the number of permutations P({n}, {r}).", f"Find P({n}, {r}).", f"How many permutations of {n} items taken {r} at a time?", f"Calculate the number of ordered arrangements of {r} items from {n}."),'),

    ('combinatorics_core.py',
     r'(\s+)f"Compute the number of combinations C\(\{n\}, \{r\}\)."',
     r'\1pick_template(rng, f"Compute the number of combinations C({n}, {r}).", f"Find C({n}, {r}).", f"How many ways to choose {r} items from {n}?", f"Calculate the number of unordered selections of {r} from {n}."),'),

    ('combinatorics_core.py',
     r'(\s+)f"How many outcomes are there for (\{count\}) independent stages with (\{opts_str\}) options\?"',
     r'\1pick_template(rng, f"How many outcomes are there for \2 independent stages with \3 options?", f"In an experiment with \2 stages having \3 options respectively, how many possible outcomes?", f"Multiply: \3. How many total outcomes?", f"Count the total number of outcomes for \2 stages with \3 options each."),'),

    ('combinatorics_core.py',
     r'(\s+)f"Find the coefficient of a\^(\{n1\})b\^(\{n2\}) in the expansion of \(a \+ b\)\^(\{n\})\."',
     r'\1pick_template(rng, f"Find the coefficient of a^\2b^\3 in the expansion of (a + b)^\4.", f"In (a+b)^\4, what is the coefficient of a^\2b^\3?", f"Determine the coefficient of a^\2b^\3 in (a+b)^\4.", f"Expand (a+b)^\4 and give the coefficient of a^\2b^\3."),'),

    ('combinatorics_core.py',
     r'(\s+)f"Events A and B are independent with P\(A\) = (\{p1\}) and P\(B\) = (\{p2\}). Find P\(A and B\)."',
     r'\1pick_template(rng, f"Events A and B are independent with P(A) = \2 and P(B) = \3. Find P(A and B).", f"Given independent events A and B with P(A)=\2 and P(B)=\3, compute P(A∩B).", f"Find the probability that both independent events A (P=\2) and B (P=\3) occur."),'),

    ('combinatorics_core.py',
     r'(\s+)f"Find the (mean|median|mode) of the data set (\[.*\]\.")',
     r'\1pick_template(rng, f"Find the \2 of the data set \3", f"Calculate the \2 of \3.", f"What is the \2 of \3?", f"Determine the \2 for \3."),'),

    # === derivative_schema.py ===
    ('derivative_schema.py',
     r'(\s+)f"Find the derivative of f\(x\)=(\{poly\}\.")',
     r'\1pick_template(rng, f"Find the derivative of f(x)=\2", f"Differentiate f(x)=\2.", f"Compute f\'(x) for f(x)=\2.", f"Determine d/dx of \2."),'),

    ('derivative_schema.py',
     r'(\s+)f"Find the tangent line to (\{func\}) at x=(\{x0\})."',
     r'\1pick_template(rng, f"Find the tangent line to \2 at x=\3.", f"Determine the equation of the tangent line to \2 at x=\3.", f"Find the line tangent to \2 at the point where x=\3."),'),

    ('derivative_schema.py',
     r'(\s+)f"Use derivative signs to state where f\(x\)=x\^2 decreases and increases."',
     r'\1pick_template(rng, f"Use derivative signs to state where f(x)=x^2 decreases and increases.", f"By analysing f\'(x), determine where f(x)=x^2 is increasing and decreasing.", f"Find the intervals where f(x)=x^2 is increasing and where it is decreasing."),'),

    ('derivative_schema.py',
     r'(\s+)f"Find the critical x-value of (\{expr\}\.")',
     r'\1pick_template(rng, f"Find the critical x-value of \2", f"Determine the critical point(s) of \2.", f"Find where f\'(x)=0 for \2."),'),

    ('derivative_schema.py',
     r'(\s+)f"Find the local extremum of f\(x\)=(\{expr\}\)."',
     r'\1pick_template(rng, f"Find the local extremum of f(x)=\2.", f"Determine the local extreme value(s) of f(x)=\2.", f"Find any local maxima or minima of f(x)=\2."),'),

    ('derivative_schema.py',
     r'(\s+)f"Find the absolute extrema of f\(x\)=x\^2 on \[(-?\d+), (-?\d+)\]\."',
     r'\1pick_template(rng, f"Find the absolute extrema of f(x)=x^2 on [\2, \3].", f"Determine the global maximum and minimum of f(x)=x^2 on the interval [\2, \3].", f"Find the maximum and minimum values of f(x)=x^2 for x in [\2, \3]."),'),

    # === sequences_core.py ===
    ('sequences_core.py',
     r'(\s+)f"In an arithmetic sequence the first term is (\{a1\}) and the common difference is (\{d\}). Find the (\{ordinal_s\}) term."',
     r'\1pick_template(rng, f"In an arithmetic sequence the first term is \2 and the common difference is \3. Find the \4 term.", f"An arithmetic sequence has a_1=\2 and d=\3. Determine a_\4.", f"Find the \4 term of the arithmetic sequence with first term \2 and common difference \3.", f"Given a_1=\2 and d=\3, compute the \4 term of this arithmetic sequence."),'),

    ('sequences_core.py',
     r'(\s+)f"Find the sum of the first (\{n\}) terms of the arithmetic sequence with first term (\{a1\}) and common difference (\{d\})."',
     r'\1pick_template(rng, f"Find the sum of the first \2 terms of the arithmetic sequence with a_1=\3 and d=\4.", f"Calculate S_\2 for the arithmetic sequence with first term \3, common difference \4.", f"An arithmetic sequence has a_1=\3, d=\4. Find the sum of the first \2 terms."),'),

    ('sequences_core.py',
     r'(\s+)f"In a geometric sequence the first term is (\{a1\}) and the common ratio is (\{r\}). Find the (\{ordinal_s\}) term."',
     r'\1pick_template(rng, f"In a geometric sequence the first term is \2 and the common ratio is \3. Find the \4 term.", f"A geometric sequence has a_1=\2 and r=\3. Determine a_\4.", f"Find the \4 term of the geometric sequence with first term \2 and common ratio \3."),'),

    ('sequences_core.py',
     r'(\s+)f"Find the sum of the first (\{n\}) terms of the geometric sequence with first term (\{a1\}) and common ratio (\{r\})."',
     r'\1pick_template(rng, f"Find the sum of the first \2 terms of the geometric sequence with a_1=\3 and r=\4.", f"Calculate S_\2 for the geometric sequence with first term \3, common ratio \4.", f"A geometric sequence has a_1=\3, r=\4. Find the sum of the first \2 terms."),'),

    # === trigonometric_schema.py (already diversified - just the remaining ones) ===
    ('trigonometric_schema.py',
     r'(\s+)f"Find the reference angle for (\{angle\})°."',
     r'\1pick_template(rng, f"Find the reference angle for \2°.", f"Determine the reference angle of \2°.", f"What is the reference angle for \2°?", f"Calculate the acute reference angle for \2°."),'),

    ('trigonometric_schema.py',
     r'(\s+)f"A trigonometric equation has solution (\{base\})° and period (\{period\})°. Write the periodic solution set."',
     r'\1pick_template(rng, f"A trigonometric equation has solution \2° and period \3°. Write the periodic solution set.", f"Given a base solution \2° and period \3°, express all solutions.", f"Write the general solution given one solution \2° and period \3°."),'),

    # === function_property_schema.py ===
    ('function_property_schema.py',
     r'(\s+)f"Find the domain restriction for f\(x\)=1/(\{denom\})."',
     r'\1pick_template(rng, f"Find the domain restriction for f(x)=1/(\2).", f"State the values of x for which f(x)=1/(\2) is undefined.", f"Determine the domain restriction of f(x)=1/(\2).", f"What x-values must be excluded from the domain of 1/(\2)?"),'),

    ('function_property_schema.py',
     r'(\s+)f"Find the domain of f\(x\)=(sqrt|log)\((\{inner\})\)."',
     r'\1pick_template(rng, f"Find the domain of f(x)=\2(\3).", f"Determine the domain of f(x)=\2(\3).", f"What is the domain of \2(\3)?", f"State the domain of f(x)=\2(\3)."),'),

    ('function_property_schema.py',
     r'(\s+)f"Find the range of f\(x\)=(\{expr\})."',
     r'\1pick_template(rng, f"Find the range of f(x)=\2.", f"Determine the range of f(x)=\2.", f"What is the range of f(x)=\2?", f"Find all possible output values of f(x)=\2."),'),

    ('function_property_schema.py',
     r'(\s+)f"Find the zero of f\(x\)=(\{expr\})."',
     r'\1pick_template(rng, f"Find the zero of f(x)=\2.", f"Solve f(x)=0 for f(x)=\2.", f"Determine the x-intercept of f(x)=\2.", f"Find the root of f(x)=\2."),'),

    ('function_property_schema.py',
     r'(\s+)f"Find where f\(x\)=(\{expr\}) is positive."',
     r'\1pick_template(rng, f"Find where f(x)=\2 is positive.", f"Solve f(x)>0 for f(x)=\2.", f"Determine the interval(s) where f(x)=\2 > 0.", f"For which x is f(x)=\2 positive?"),'),

    ('function_property_schema.py',
     r'(\s+)f"Let f\(x\)=(\{f1\}) if x<(\{c\}), and f\(x\)=(\{f2\}) if x≥(\{c2\}). Find f\((\{x0\})\)."',
     r'\1pick_template(rng, f"Let f(x)=\2 if x<\4, and f(x)=\3 if x≥\4. Find f(\5).", f"Evaluate the piecewise function f(x) at x=\5 given f(x)=\2 (x<\4) and f(x)=\3 (x≥\4).", f"A function is defined as \2 (x<\4) and \3 (x≥\4). Compute f(\5)."),'),

    ('function_property_schema.py',
     r'(\s+)f"Let f\(x\)=(\{f1\}) and g\(x\)=(\{g1\}). Find f\(g\((\{x0\})\)\)."',
     r'\1pick_template(rng, f"Let f(x)=\2 and g(x)=\3. Find f(g(\4)).", f"Given f(x)=\2 and g(x)=\3, evaluate f∘g at x=\4.", f"Compute the composition f(g(\4)) where f(x)=\2 and g(x)=\3."),'),

    # === ratio_core / combinatorics patterns ===
    ('combinatorics_core.py',
     r'(\s+)f"A bag has (\{red\}) red and (\{other\}) other balls. What is the probability of drawing a red ball\?"',
     r'\1pick_template(rng, f"A bag has \2 red and \3 other balls. What is the probability of drawing a red ball?", f"In a bag with \2 red and \3 other balls, find P(red).", f"A bag contains \2 red and \3 other balls. Find the probability of picking a red ball at random.", f"There are \2 red and \3 non-red balls. What is the probability of drawing red?"),'),

    ('combinatorics_core.py',
     r'(\s+)f"Of (\{total\}) outcomes in event B, (\{both\}) are also in event A. Find P\(A\|B\)."',
     r'\1pick_template(rng, f"Of \2 outcomes in event B, \3 are also in event A. Find P(A|B).", f"Given |B|=\2 and |A∩B|=\3, compute the conditional probability P(A|B).", f"Find P(A|B) if event B has \2 outcomes and \3 of them also belong to A."),'),

    ('combinatorics_core.py',
     r'(\s+)f"A variable X takes values (\[.*\]) with weights (\[.*\]). Find E\[X\]."',
     r'\1pick_template(rng, f"A variable X takes values \2 with weights \3. Find E[X].", f"Compute the expected value E[X] for the distribution \2 with weights \3.", f"Find the expectation of X given values \2 and weights \3."),'),

    ('combinatorics_core.py',
     r'(\s+)f"Find the population variance of the data set (\[.*\]\.")',
     r'\1pick_template(rng, f"Find the population variance of the data set \2", f"Calculate the variance of \2.", f"Compute the population variance for \2."),'),
]

count = 0
for fname, pattern, replacement in REPLACEMENTS:
    path = f'{BASE}/{fname}'
    try:
        with open(path) as f:
            content = f.read()
        new_content, n = re.subn(pattern, replacement, content)
        if n > 0:
            with open(path, 'w') as f:
                f.write(new_content)
            count += n
            print(f'{fname}: {n} replacement(s)')
    except Exception as e:
        print(f'{fname}: ERROR - {e}')

print(f'\nTotal: {count} template diversifications applied')
