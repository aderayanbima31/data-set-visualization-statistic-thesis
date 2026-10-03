# Step 3B Plan: Synthetic Execution Dataset and Descriptive Analysis

## Objective

Create a reproducible, synthetic dataset for the Statistics for Data Science assignment and analyze it with Python. The context is AI-assisted migration of a legacy Android e-wallet Home screen toward Material 3.

The deliverable is a transparent descriptive analysis, not an AI benchmark and not a predictive system.

## Scope

### In scope

- build `data/migration_tasks.csv` from the agreed migration-task catalog;
- generate or document synthetic execution observations in `data/migration_observations.csv`;
- validate types, ranges, IDs, and the task-to-observation relationship;
- calculate mean, median, and mode where meaningful;
- calculate variance and standard deviation;
- calculate quartiles and IQR;
- identify potential outliers using the 1.5 × IQR rule;
- create histograms and boxplots;
- create scatter plots for selected numeric pairs; and
- calculate and interpret correlation as exploratory association only.

### Out of scope

- forecasting or time-series prediction;
- machine learning or classification;
- causal inference;
- claims about real Codex, AI-agent, or production performance;
- statistical generalization beyond this synthetic dataset; and
- collecting external benchmark data.

## Inputs and outputs

Use the specification in `docs/DATASET_SPEC.md` as the source of truth for entities, columns, ranges, and disclosure language.

Required inputs:

- `data/migration_tasks.csv`
- `data/migration_observations.csv`

Required notebook:

- `analysis/descriptive_statistics.ipynb`

Required outputs:

- plots under `outputs/` as PNG files;
- `outputs/descriptive_summary.csv`; and
- `outputs/outliers.csv`.

## Execution workflow for Codex

1. Create the folder structure shown below.
2. Create a task catalog with at least 30 unique `MIG-###` tasks covering the legacy e-wallet Home areas: App Bar, Balance, Quick Action, Promo, Transactions, and UI States.
3. Generate a reproducible synthetic observation dataset. Set and record a fixed random seed. Use plausible ranges and preserve the disclosure that all execution metrics are simulated.
4. Load both CSV files into the notebook and validate schema, nulls, duplicate IDs, numeric ranges, and foreign-key coverage.
5. Join observations with task metadata when group analysis requires `component_area`, `migration_category`, or `difficulty`.
6. Produce a descriptive summary for the numeric variables: count, mean, median, standard deviation, variance, minimum, Q1, Q2, Q3, maximum, and IQR.
7. Report mode only for variables where it is meaningful, especially categorical fields or clearly repeated discrete values. Explain when no useful unique mode exists.
8. Detect potential outliers for numeric variables with the 1.5 × IQR rule. Record `observation_id`, `ticket_id`, variable name, value, lower fence, and upper fence in `outputs/outliers.csv`.
9. Create and save labeled PNG plots with readable titles and axis units.
10. Add short interpretations beneath each result. Interpret correlation as association within this synthetic sample, not causation or predictive validity.
11. Repeat the synthetic-data limitation in the notebook introduction, summary, and final interpretation.

## Minimum analysis and figures

The notebook must include:

- a frequency summary for key categorical variables;
- mean, median, and appropriate mode analysis;
- variance and standard deviation for numeric metrics;
- quartiles and IQR;
- outlier detection and a review of whether outliers are plausible synthetic observations;
- histograms for `execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, and `error_count`;
- boxplots for the same numeric variables, optionally grouped by `difficulty` or `component_area`;
- scatter plots for at least two meaningful pairs, such as execution time versus token usage and accuracy score versus test pass rate; and
- a correlation matrix or correlation table for numeric variables, with cautious interpretation.

Suggested PNG names include `execution_time_histogram.png`, `numeric_metrics_boxplots.png`, `time_vs_tokens_scatter.png`, `accuracy_vs_test_pass_scatter.png`, and `correlation_matrix.png`.

## Reproducibility and reporting requirements

- Keep generation and analysis logic in the notebook or in clearly referenced project code.
- Record Python/library versions if available.
- Use deterministic randomness and state the seed.
- Use consistent units and axis labels.
- Do not overwrite raw CSV inputs during cleaning.
- Ensure the notebook runs from the repository root or documents its working-directory assumption.
- Keep conclusions limited to the observed synthetic sample.

## Expected conclusion style

The conclusion should summarize the observed center, spread, distribution shape, potential outliers, and exploratory associations. It must explicitly state that `execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, and `error_count` are simulated and are not real AI benchmark results.

## Recommended folder structure

```text
project/
├── docs/
│   ├── DATASET_SPEC.md
│   └── STEP_3B_PLAN.md
├── data/
│   ├── migration_tasks.csv
│   └── migration_observations.csv
├── analysis/
│   └── descriptive_statistics.ipynb
└── outputs/
    ├── *.png
    ├── descriptive_summary.csv
    └── outliers.csv
```

