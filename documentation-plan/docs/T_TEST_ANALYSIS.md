# T-Test Homework: Synthetic Migration Dataset

## Purpose and scope

This deliverable implements the three T-test types required by the assignment:

1. one-sample T-test;
2. paired-samples T-test; and
3. independent-samples T-test.

All source data and results are synthetic teaching data. They must not be
interpreted as results from real Codex runs, AI agents, production Android
projects, or a validated benchmark. The tests only describe the generated
sample in this repository.

## Reproducible execution

From the repository root, install the project requirements and run:

```text
python analysis/t_test_analysis.py
```

The command reads the raw CSV files without altering them and regenerates:

- `outputs/t_test_results.csv`
- `outputs/t_test_assumption_checks.csv`

## Analysis design and documented assumptions

The raw observations repeat each migration task five times. A repetition from
the same task is not treated as a new independent task. Time-based tests first
average repetitions within each `ticket_id`, making the task the unit of
analysis.

| Required test | Outcome and comparison | Null hypothesis | Rationale |
|---|---|---|---|
| One-sample | Task-level mean `execution_time_sec` vs. 75 seconds | mean time = 75 sec | 75 seconds is an explicitly documented teaching reference, not a production SLA. |
| Paired | Per-task mean `accuracy_score`: synthetic-agent-A minus synthetic-agent-B | mean paired difference = 0 | Both agents have runs for the same migration task, so `ticket_id` provides the matching unit. |
| Independent | Task-level mean `execution_time_sec`: Hard vs. Easy tasks | mean difference = 0 | Distinct tasks are compared. Welch's T-test is used because equal variances are not assumed. |

All tests are two-sided with `alpha = 0.05`. The results table includes sample
size, group means, mean difference, t statistic, degrees of freedom, p value,
95% confidence interval, an effect size, and the decision for the stated null
hypothesis.

## Diagnostics and interpretation

`outputs/t_test_assumption_checks.csv` reports Shapiro-Wilk diagnostics for
the tested values (or paired differences) and a Levene diagnostic for the
independent comparison. These are diagnostics, not automatic proof that an
assumption holds. The interpretation also relies on the documented design:
task-level aggregation reduces pseudo-replication, matching is by ticket for
the paired test, and Welch's method does not require equal variances.

Because the values are generated, p values and confidence intervals have no
claim beyond this synthetic sample. They demonstrate the mechanics and clear
reporting of T-tests for the course assignment.

## Current deterministic run

With the repository's current fixed-seed data, the one-sample test finds a
mean task-level time of 88.03 seconds, 13.03 seconds above the 75-second
teaching reference (`t(35)=2.546`, `p=0.0155`, 95% CI for the difference
`[2.64, 23.41]`). The paired agent comparison finds no evidence of a non-zero
mean accuracy difference (`t(35)=0.802`, `p=0.428`). The Welch test finds
hard-task mean time exceeds easy-task mean time by 78.25 seconds
(`t(12.09)=14.002`, `p<0.001`, 95% CI `[66.08, 90.41]`).

The Shapiro-Wilk diagnostic for the one-sample time values is below 0.05
(`p=0.0138`), so that result should be interpreted cautiously; the spread
reflects the deliberately mixed synthetic task difficulties. The other
diagnostics are retained in the output file for transparent review.
