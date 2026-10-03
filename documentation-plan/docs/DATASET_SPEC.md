# Synthetic Android UI Migration Dataset Specification

## Purpose

This dataset supports a Statistics for Data Science assignment about AI-assisted migration of a legacy Android e-wallet Home screen toward Material 3.

The dataset is **synthetic** and is intended for descriptive-statistics practice only. It may be used to demonstrate:

- central tendency: mean, median, and mode where appropriate;
- dispersion: variance and standard deviation;
- quartiles, IQR, and outlier detection;
- distributions using histograms and boxplots; and
- exploratory relationships using scatter plots and correlation.

It must not be used for forecasting, machine learning, causal claims, or claims about production performance.

## Scenario

The source system is a legacy Material/AppCompat-style Android e-wallet Home screen containing an app bar, balance card, quick actions, promotional content, transaction content, and supporting UI states. The target system uses Material 3 components and styling.

The catalog covers migration tasks such as:

- app-bar actions and styling;
- balance-card container, typography, visibility action, and CTAs;
- Send, Top Up, Pay, and More quick actions;
- quick-action icon styling;
- promotional card and CTA;
- transaction-list presentation; and
- loading, empty, and error states.

## Entity and unit of observation

- **Task entity:** one Android UI migration task.
- **Observation entity:** one simulated AI-assisted execution of one migration task.
- **Unit of observation in `migration_observations.csv`:** one execution record identified by `observation_id`.

The task catalog and execution observations are separate so that task metadata is not confused with measured variables.

## Files

### `data/migration_tasks.csv`

One row per migration task.

Required columns:

| Column | Type | Meaning |
|---|---|---|
| `ticket_id` | string | Stable task identifier, for example `MIG-001`. |
| `component_area` | categorical | Screen area, such as `App Bar`, `Balance`, or `Quick Action`. |
| `migration_task` | string | Plain-language task description. |
| `migration_category` | categorical | `Component`, `Styling`, `Behavior`, or `State`. |
| `difficulty` | categorical | `Easy`, `Medium`, or `Hard`. |

The initial catalog should contain at least 30 tasks and should represent the agreed legacy e-wallet Home scenario. IDs must be unique.

### `data/migration_observations.csv`

Simulated execution records joined to `migration_tasks.csv` through `ticket_id`.

Required columns:

| Column | Type | Meaning |
|---|---|---|
| `observation_id` | string | Unique execution identifier. |
| `ticket_id` | string | Migration task identifier. |
| `agent_id` | categorical | Simulated agent/configuration label. |
| `execution_time_sec` | numeric | Simulated execution duration in seconds. |
| `token_usage` | integer | Simulated tokens used by the execution. |
| `accuracy_score` | numeric | Simulated task accuracy score, preferably on a 0–1 scale. |
| `test_pass_rate` | numeric | Simulated proportion of checks passed, on a 0–1 scale. |
| `error_count` | integer | Simulated number of errors recorded during execution. |
| `status` | categorical | Simulated outcome, such as `Passed`, `Passed with fixes`, or `Failed`. |

The dataset should include enough observations to make distributions and relationships visible. A practical starting point is multiple observations per task, with a documented random seed if values are generated programmatically.

## Synthetic-data disclosure

`execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, and `error_count` are **simulated variables**. They are not collected from real Codex runs, real AI agents, production Android projects, or a validated benchmark. Any patterns, correlations, or outliers are properties of the synthetic teaching dataset only.

Reports and notebook outputs must repeat this limitation wherever results are interpreted. Do not describe the values as actual AI-agent performance.

## Data-quality rules

1. `observation_id` and `ticket_id` are non-null; IDs are unique within their intended scope.
2. Every observation `ticket_id` exists in `migration_tasks.csv`.
3. `execution_time_sec`, `token_usage`, and `error_count` are non-negative.
4. `accuracy_score` and `test_pass_rate` are between 0 and 1 inclusive.
5. Categorical labels use a consistent spelling and capitalization.
6. Missing values, if intentionally included, are documented and handled explicitly in the notebook.
7. The raw CSV files remain unchanged by analysis; cleaned or summarized outputs go under `outputs/`.

## Analysis boundary

The required analysis is descriptive and exploratory. It may compare groups such as difficulty or component area, but it must not predict future execution results or train a machine-learning model.

