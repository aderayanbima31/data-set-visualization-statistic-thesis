# Correlation Analysis Homework

## Scope and data

This report completes the five requested correlation exercises using the project’s synthetic migration dataset. The task catalog contains 36 migration tasks and the observation file contains repeated simulated executions. For relationships involving execution metrics, repeated observations are averaged within `ticket_id`; therefore, the task is the unit of analysis.

The variables `execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, and `error_count` are simulated teaching metrics. The results describe this generated sample only and are not evidence about real AI agents, Codex runs, production Android work, or a validated benchmark.

## Variable preparation

- Point-Biserial uses only Easy and Hard tasks so `difficulty` is genuinely binary (`is_hard`).
- Contingency Coefficient uses the task-catalog relationship between nominal `component_area` and `difficulty`.
- Phi uses two binary task-level variables: `is_hard` (Hard vs non-Hard) and `has_error` (any positive mean error count vs none).
- Spearman converts the ordered difficulty labels to ranks: Easy=1, Medium=2, Hard=3.
- Pearson uses the two continuous task-level means `execution_time_sec` and `token_usage`.

## Results

| Method | Variables | n | Coefficient | p-value | Decision |
|---|---|---:|---:|---:|---|
| Point-Biserial | is_hard (Easy vs Hard) and mean execution_time_sec | 17 | 0.9526 | <0.001 | Significant at alpha=0.05 |
| Contingency Coefficient (CC) | component_area and difficulty | 36 | 0.3376 | 0.9144 | Not significant at alpha=0.05 |
| Phi (phi) | is_hard (Hard vs non-Hard) and has_error | 36 | 0.1870 | 0.2619 | Not significant at alpha=0.05 |
| Spearman Rank | difficulty rank (Easy=1, Medium=2, Hard=3) and mean execution_time_sec | 36 | 0.9045 | <0.001 | Significant at alpha=0.05 |
| Pearson Product-Moment | mean execution_time_sec and mean token_usage | 36 | 0.9608 | <0.001 | Significant at alpha=0.05 |

## Formulas used

- Point-Biserial: `r_pb = ((M1 - M0) / s_y) * sqrt(pq)`.
- Contingency Coefficient: `CC = sqrt(chi-square / (chi-square + N))`. 
- Phi: `phi = (ad - bc) / sqrt((a+b)(c+d)(a+c)(b+d))` for a 2x2 table.
- Spearman Rank: `rho = 1 - 6*sum(d^2) / (n*(n^2 - 1))` when there are no tied ranks.
- Pearson Product-Moment: covariance of the two continuous variables divided by the product of their standard deviations.

## Supporting values

For the Point-Biserial comparison, mean execution time was **52.51 seconds** for Easy tasks and **130.75 seconds** for Hard tasks.

The Contingency Coefficient uses the full 6 x 3 task table (`component_area` by `difficulty`), while Phi uses a 2 x 2 table (`is_hard` by `has_error`). Complete cell counts are saved in `outputs/correlation_contingency_tables.csv`.

## Conclusions by method

1. **Point-Biserial:** Appropriate for one binary nominal variable and one continuous variable. Here it is suitable for comparing Easy versus Hard tasks against execution time. Hard tasks took longer on average, and the association is statistically significant in this synthetic sample.
2. **Contingency Coefficient:** Appropriate for testing association between categorical variables using a contingency table and chi-square. It is suitable for `component_area` versus `difficulty`, but the observed association is weak and not statistically significant.
3. **Phi:** Appropriate only when both variables are binary. It is suitable for `is_hard` versus `has_error` after the explicit binary transformation. The association is weak and not statistically significant.
4. **Spearman Rank:** Appropriate for ordinal variables or monotonic relationships without requiring a linear-normal relationship. It is suitable for ordered difficulty versus execution time and shows a strong positive association.
5. **Pearson Product-Moment:** Appropriate for two continuous variables when a linear relationship is the target. It is suitable for execution time versus token usage and shows a strong positive linear association.

## Final selection

The best method depends on the measurement scale, not on the strength of the result alone. For the natural variable pairs in this dataset, use **Pearson** for two continuous metrics such as execution time and token usage; **Spearman** for ordered difficulty and a metric such as execution time; **Contingency Coefficient** for multi-category variables such as component area and difficulty; **Phi** only for two binary variables; and **Point-Biserial** for one binary variable paired with one continuous metric. These conclusions are exploratory and limited to the synthetic sample.
