# Non-Parametric Test Analysis

This report uses the existing synthetic migration-task dataset. The results describe this generated teaching sample only; they are not measurements of real AI agents, Codex runs, production Android work, or a validated benchmark.

## Design

The raw observations contain five executions per migration task. Repeated executions are averaged by `ticket_id` when the task is the unit of analysis. The Wilcoxon comparison is paired by task, and the Chi-Square test uses one majority status per task to avoid pseudo-replication. All tests are two-sided with `alpha = 0.05`.

## Results

| Test | Statistic | df | p-value | Effect size | Decision |
|---|---:|---:|---:|---:|---|
| Mann-Whitney U | U = 70.000 | - | 0.0001028 | Rank-biserial correlation = 1.000 | Reject H0 |
| Wilcoxon signed-rank | W = 286.500 | - | 0.6406 | Matched-pairs rank-biserial correlation = 0.090 | Fail to reject H0 |
| Kruskal-Wallis H | H = 8.184 | 5 | 0.1464 | Epsilon-squared = 0.106 | Fail to reject H0 |
| Chi-Square test of independence | chi-square = 31.535 | 2 | 1.42e-07 | Cramer's V = 0.936 | Reject H0 |

## Interpretation

* **Mann-Whitney:** compares independent Hard and Easy task-level execution-time distributions.
* **Wilcoxon:** compares matched task-level accuracy for synthetic agent A and B.
* **Kruskal-Wallis:** tests the omnibus difference among component-area execution-time distributions; a significant result would need post-hoc tests to locate pairwise differences.
* **Chi-Square:** tests whether task difficulty and majority status are associated. Sparse expected counts should be considered when interpreting the result.

Reproduce with `python analysis/non_parametric_analysis.py`. The raw CSV inputs are not modified.
