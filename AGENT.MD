# Project Instructions

## Project purpose

This project supports a Statistics for Data Science assignment about migrating a legacy Android e-wallet Home screen toward Material 3. The project uses a reproducible synthetic migration-task dataset for descriptive and exploratory statistical analysis.

The authoritative Step 3B requirements are:

- `documentation-plan`
- `documentation-plan`

Read both documents before changing the dataset, notebook, or generated outputs.

## Scope boundary

Allowed work includes:

- creating and validating migration-task and execution-observation datasets;
- descriptive statistics such as mean, median, mode, variance, standard deviation, quartiles, IQR, and frequency tables;
- 1.5 × IQR potential-outlier detection;
- histograms, boxplots, scatter plots, and correlation summaries; and
- cautious descriptive interpretation of this synthetic sample.

Do not implement forecasting, time-series prediction, machine learning, classification, causal inference, production benchmarking, or statistical generalization beyond the synthetic sample.

## Design-system context

The migration scenario moves a legacy Material/AppCompat-style Android e-wallet Home screen toward Material 3. Treat the design system as the UI context for the task catalog, not as a measured outcome of the synthetic analysis.

Use consistent Material 3 migration vocabulary for these screen areas:

- App Bar: top app bar structure, actions, typography, color, and elevation.
- Balance: balance-card container, typography, visibility state, and call-to-action buttons.
- Quick Action: Send, Top Up, Pay, and More actions, including icons, labels, spacing, and navigation behavior.
- Promo: promotional card, illustration, copy, and call-to-action behavior.
- Transactions: section header, transaction rows, typography hierarchy, amounts, statuses, spacing, and interaction.
- UI States: loading, empty, error, offline, masked, accessibility, and state-transition behavior.

Migration categories map to design-system concerns as follows:

- `Component`: replacing a legacy widget or container with its Material 3 counterpart.
- `Styling`: applying Material 3 typography, color, shape, spacing, elevation, or icon treatments.
- `Behavior`: preserving or implementing interaction, navigation, visibility, and accessibility behavior.
- `State`: representing loading, empty, error, offline, masked, or transition states consistently.

Do not claim that the synthetic metrics measure Material 3 quality, visual parity, accessibility compliance, design-token correctness, or production user experience. Those require separate design and UI-audit evidence.

## Synthetic-data requirements

`execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, and `error_count` are simulated teaching metrics. They must always be described as synthetic or simulated and must never be presented as real Codex, AI-agent, production Android, or benchmark measurements.

Use the fixed seed defined in `analysis/generate_synthetic_data.py`. Keep generation deterministic and preserve the `data_status=synthetic` label in observation records and analysis outputs.

Do not add external benchmark data or real user/project data.

## Repository structure

- `data/migration_tasks.csv`: one row per migration task.
- `data/migration_observations.csv`: one simulated execution observation per record.
- `analysis/generate_synthetic_data.py`: deterministic input-data generator.
- `analysis/descriptive_statistics.ipynb`: required analysis notebook.
- `outputs/`: generated summaries, outlier reports, and PNG visualizations.
- `requirements.txt`: Python dependencies for PyCharm/Jupyter execution.

Raw CSV inputs must not be modified by analysis or cleaning steps. Write summaries and visualizations under `outputs/`.

## Data-quality expectations

Before interpreting results, validate:

- required columns and data types;
- non-null identifiers;
- unique `ticket_id` values in the task catalog;
- unique `observation_id` values in observations;
- complete observation-to-task foreign-key coverage;
- non-negative duration, token, and error values;
- scores and pass rates within the inclusive 0–1 range; and
- consistent categorical labels.

Use the task metadata join only for descriptive grouping by component area, migration category, or difficulty.

## PyCharm workflow

Use a project interpreter with the packages listed in `requirements.txt`. Open `analysis/descriptive_statistics.ipynb` in PyCharm and run all cells from the repository root.

To regenerate the deterministic observation input before analysis, run:

```text
python analysis/generate_synthetic_data.py
```

The notebook must run from the repository root or from `analysis/` and must regenerate the required files under `outputs/` without overwriting raw inputs.

## Change and verification rules

- Keep changes focused on the requested analysis scope.
- Preserve existing user changes and unrelated files.
- Update the notebook and generator together when schema or generation logic changes.
- Verify the notebook end-to-end after changes.
- Check that required CSV and PNG outputs are present and readable.
- Repeat the synthetic-data limitation in the notebook introduction, result interpretations, and conclusion.
