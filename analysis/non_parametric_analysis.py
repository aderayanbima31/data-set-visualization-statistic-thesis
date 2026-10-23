"""Run the four non-parametric tests required by the coursework.

The repository data is a deterministic synthetic teaching dataset. Repeated
observations are aggregated by ``ticket_id`` where a task is the meaningful
unit of analysis; this avoids treating the five executions of one task as
independent samples.

Tests implemented:

* Mann-Whitney U: Hard versus Easy task-level execution time;
* Wilcoxon signed-rank: matched agent-A versus agent-B task-level accuracy;
* Kruskal-Wallis: task-level execution time across component areas; and
* Chi-Square: task difficulty versus the majority status for each task.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ALPHA = 0.05
AGENT_A = "synthetic-agent-A"
AGENT_B = "synthetic-agent-B"
STATUS_ORDER = ["Failed", "Passed with fixes", "Passed"]

REQUIRED_TASK_COLUMNS = {
    "ticket_id", "component_area", "migration_task", "migration_category", "difficulty"
}
REQUIRED_OBSERVATION_COLUMNS = {
    "observation_id", "ticket_id", "agent_id", "execution_time_sec", "token_usage",
    "accuracy_score", "test_pass_rate", "error_count", "status", "data_status",
}


def _decision(p_value: float) -> str:
    return "Reject H0" if p_value < ALPHA else "Fail to reject H0"


def validate_inputs(tasks: pd.DataFrame, observations: pd.DataFrame) -> None:
    """Validate the raw synthetic inputs without modifying them."""

    missing_tasks = REQUIRED_TASK_COLUMNS.difference(tasks.columns)
    missing_observations = REQUIRED_OBSERVATION_COLUMNS.difference(observations.columns)
    if missing_tasks or missing_observations:
        raise ValueError(
            f"Missing columns: tasks={sorted(missing_tasks)}, "
            f"observations={sorted(missing_observations)}"
        )
    if tasks["ticket_id"].isna().any() or tasks["ticket_id"].duplicated().any():
        raise ValueError("Task ticket_id values must be present and unique.")
    if observations[["observation_id", "ticket_id"]].isna().any().any():
        raise ValueError("Observation identifiers and ticket IDs must be present.")
    if observations["observation_id"].duplicated().any():
        raise ValueError("Observation IDs must be unique.")
    if not observations["ticket_id"].isin(tasks["ticket_id"]).all():
        raise ValueError("Every observation ticket_id must exist in the task catalog.")
    numeric_columns = [
        "execution_time_sec", "token_usage", "accuracy_score", "test_pass_rate", "error_count"
    ]
    if observations[numeric_columns].isna().any().any() or not all(
        pd.api.types.is_numeric_dtype(observations[column]) for column in numeric_columns
    ):
        raise ValueError("Required execution metrics must be complete numeric values.")
    if not observations["data_status"].eq("synthetic").all():
        raise ValueError("This analysis only accepts rows labelled data_status=synthetic.")
    if (observations[["execution_time_sec", "token_usage", "error_count"]] < 0).any().any():
        raise ValueError("Durations, tokens, and error counts must be non-negative.")
    if not observations[["accuracy_score", "test_pass_rate"]].apply(
        lambda series: series.between(0, 1).all()
    ).all():
        raise ValueError("Accuracy and pass-rate values must be in the inclusive 0–1 range.")


def task_level_data(tasks: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    """Aggregate repeated observations so each task contributes one row."""

    task_metrics = (
        observations.groupby("ticket_id", as_index=False)
        .agg(
            execution_time_sec=("execution_time_sec", "mean"),
            accuracy_score=("accuracy_score", "mean"),
        )
    )
    return tasks.merge(task_metrics, on="ticket_id", validate="one_to_one")


def _group_summary(test_id: str, groups: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for group, values in groups.items():
        rows.append({
            "test_id": test_id,
            "group": group,
            "n": len(values),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "mean_rank": float(stats.rankdata(np.concatenate(list(groups.values())))[
                sum(len(item) for item in list(groups.values())[:list(groups).index(group)]):
                sum(len(item) for item in list(groups.values())[:list(groups).index(group)]) + len(values)
            ].mean()),
        })
    return pd.DataFrame(rows)


def mann_whitney_difficulty_time(task_data: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame, dict[str, object]]:
    """Compare independent Hard and Easy task-level execution times."""

    groups = {
        "Hard tasks": task_data.loc[task_data["difficulty"].eq("Hard"), "execution_time_sec"].to_numpy(float),
        "Easy tasks": task_data.loc[task_data["difficulty"].eq("Easy"), "execution_time_sec"].to_numpy(float),
    }
    if min(map(len, groups.values())) < 2:
        raise ValueError("Mann-Whitney needs at least two tasks in each group.")
    first, second = groups.values()
    test = stats.mannwhitneyu(first, second, alternative="two-sided", method="auto")
    u = float(test.statistic)
    rank_biserial = 2 * u / (len(first) * len(second)) - 1
    result = {
        "test_id": "mann_whitney_difficulty_time",
        "test_type": "Mann-Whitney U",
        "outcome": "Task-level execution time (seconds)",
        "unit_of_analysis": "One task-level mean across repeated synthetic executions",
        "null_hypothesis": "Hard and Easy task execution-time distributions are equal",
        "alternative_hypothesis": "Hard and Easy task execution-time distributions differ",
        "group_a": "Hard tasks",
        "group_b_or_factor": "Easy tasks",
        "n_total": len(first) + len(second),
        "n_groups": 2,
        "statistic_name": "U",
        "statistic": u,
        "degrees_of_freedom": np.nan,
        "p_value_two_sided": float(test.pvalue),
        "alpha": ALPHA,
        "effect_size_name": "Rank-biserial correlation",
        "effect_size": float(rank_biserial),
        "decision_at_alpha_0_05": _decision(float(test.pvalue)),
        "notes": "Positive effect means Hard tasks tend to have larger values than Easy tasks.",
    }
    diagnostic = {
        "test_id": result["test_id"],
        "diagnostic": "Normality assumption",
        "value": np.nan,
        "threshold": np.nan,
        "flag": "Not required; inspect distributions and independence design",
    }
    return result, _group_summary(result["test_id"], groups), diagnostic


def _paired_accuracy(observations: pd.DataFrame) -> pd.DataFrame:
    paired = (
        observations.groupby(["ticket_id", "agent_id"], as_index=False)["accuracy_score"]
        .mean()
        .pivot(index="ticket_id", columns="agent_id", values="accuracy_score")
    )
    missing = {AGENT_A, AGENT_B}.difference(paired.columns)
    if missing:
        raise ValueError(f"Paired Wilcoxon requires both agents; missing {sorted(missing)}.")
    return paired[[AGENT_A, AGENT_B]].dropna()


def wilcoxon_agent_accuracy(observations: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame, dict[str, object]]:
    """Compare matched task-level accuracy scores for agent A and agent B."""

    pairs = _paired_accuracy(observations)
    first = pairs[AGENT_A].to_numpy(float)
    second = pairs[AGENT_B].to_numpy(float)
    differences = first - second
    nonzero = differences[differences != 0]
    if len(nonzero) < 2:
        raise ValueError("Wilcoxon needs at least two non-zero paired differences.")
    test = stats.wilcoxon(first, second, alternative="two-sided", zero_method="wilcox", method="auto")
    ranks = stats.rankdata(np.abs(nonzero), method="average")
    rank_biserial = float((ranks[nonzero > 0].sum() - ranks[nonzero < 0].sum()) / ranks.sum())
    test_id = "wilcoxon_agent_accuracy"
    result = {
        "test_id": test_id,
        "test_type": "Wilcoxon signed-rank",
        "outcome": "Task-level accuracy score (0-1)",
        "unit_of_analysis": "One matched task with agent-specific mean accuracy",
        "null_hypothesis": "The paired median accuracy difference (A - B) is zero",
        "alternative_hypothesis": "The paired median accuracy difference (A - B) is not zero",
        "group_a": AGENT_A,
        "group_b_or_factor": AGENT_B,
        "n_total": len(pairs),
        "n_groups": 2,
        "statistic_name": "W",
        "statistic": float(test.statistic),
        "degrees_of_freedom": np.nan,
        "p_value_two_sided": float(test.pvalue),
        "alpha": ALPHA,
        "effect_size_name": "Matched-pairs rank-biserial correlation",
        "effect_size": rank_biserial,
        "decision_at_alpha_0_05": _decision(float(test.pvalue)),
        "notes": f"{len(nonzero)} non-zero paired differences were ranked.",
    }
    groups = {
        AGENT_A: first,
        AGENT_B: second,
    }
    diagnostic = {
        "test_id": test_id,
        "diagnostic": "Zero paired differences",
        "value": int(len(differences) - len(nonzero)),
        "threshold": 0,
        "flag": "Informational; zero differences are omitted by Wilcoxon",
    }
    return result, _group_summary(test_id, groups), diagnostic


def kruskal_component_area_time(task_data: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame, dict[str, object]]:
    """Compare task-level execution time across the six component areas."""

    groups = {
        area: values.to_numpy(float)
        for area, values in task_data.groupby("component_area", sort=True)["execution_time_sec"]
    }
    if len(groups) < 3 or min(map(len, groups.values())) < 2:
        raise ValueError("Kruskal-Wallis needs at least three groups with two observations each.")
    test = stats.kruskal(*groups.values())
    n = sum(map(len, groups.values()))
    k = len(groups)
    epsilon_squared = max(0.0, float((test.statistic - k + 1) / (n - k)))
    test_id = "kruskal_component_area_time"
    result = {
        "test_id": test_id,
        "test_type": "Kruskal-Wallis H",
        "outcome": "Task-level execution time (seconds)",
        "unit_of_analysis": "One task-level mean across repeated synthetic executions",
        "null_hypothesis": "All component-area execution-time distributions are equal",
        "alternative_hypothesis": "At least one component-area distribution differs",
        "group_a": "Component area",
        "group_b_or_factor": "App Bar, Balance, Promo, Quick Action, Transactions, UI States",
        "n_total": n,
        "n_groups": k,
        "statistic_name": "H",
        "statistic": float(test.statistic),
        "degrees_of_freedom": float(k - 1),
        "p_value_two_sided": float(test.pvalue),
        "alpha": ALPHA,
        "effect_size_name": "Epsilon-squared",
        "effect_size": epsilon_squared,
        "decision_at_alpha_0_05": _decision(float(test.pvalue)),
        "notes": "A significant omnibus result would require post-hoc pairwise tests to identify which areas differ.",
    }
    diagnostic = {
        "test_id": test_id,
        "diagnostic": "Smallest group size",
        "value": int(min(map(len, groups.values()))),
        "threshold": 2,
        "flag": "Passes minimum group-size check",
    }
    return result, _group_summary(test_id, groups), diagnostic


def task_majority_status(tasks: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    """Attach a deterministic majority status to each task for categorical testing."""

    def majority(series: pd.Series) -> str:
        counts = series.value_counts()
        top = counts[counts.eq(counts.max())].index.tolist()
        return sorted(top, key=lambda value: STATUS_ORDER.index(value) if value in STATUS_ORDER else len(STATUS_ORDER))[0]

    status_by_task = observations.groupby("ticket_id")["status"].agg(majority).rename("task_status")
    return tasks.merge(status_by_task, on="ticket_id", validate="one_to_one")


def chi_square_difficulty_status(tasks: pd.DataFrame, observations: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame, dict[str, object]]:
    """Test association between task difficulty and task-level majority status."""

    task_data = task_majority_status(tasks, observations)
    table = pd.crosstab(task_data["difficulty"], task_data["task_status"]).reindex(
        index=["Easy", "Medium", "Hard"], columns=STATUS_ORDER, fill_value=0
    )
    table = table.loc[(table.sum(axis=1) > 0), (table.sum(axis=0) > 0)]
    if table.shape[0] < 2 or table.shape[1] < 2:
        raise ValueError("Chi-Square needs at least two non-empty categories on each axis.")
    statistic, p_value, degrees_of_freedom, expected = stats.chi2_contingency(table, correction=False)
    n = int(table.to_numpy().sum())
    cramers_v = float(np.sqrt(statistic / (n * min(table.shape[0] - 1, table.shape[1] - 1))))
    test_id = "chi_square_difficulty_status"
    result = {
        "test_id": test_id,
        "test_type": "Chi-Square test of independence",
        "outcome": "Task-level majority status",
        "unit_of_analysis": "One migration task with majority status across its synthetic executions",
        "null_hypothesis": "Task difficulty and majority status are independent",
        "alternative_hypothesis": "Task difficulty and majority status are associated",
        "group_a": "Difficulty",
        "group_b_or_factor": "Majority status",
        "n_total": n,
        "n_groups": 2,
        "statistic_name": "chi-square",
        "statistic": float(statistic),
        "degrees_of_freedom": float(degrees_of_freedom),
        "p_value_two_sided": float(p_value),
        "alpha": ALPHA,
        "effect_size_name": "Cramer's V",
        "effect_size": cramers_v,
        "decision_at_alpha_0_05": _decision(float(p_value)),
        "notes": f"Status is reduced to the majority label per task; contingency table shape is {table.shape[0]}x{table.shape[1]}.",
    }
    contingency = table.reset_index().rename(columns={"difficulty": "row_category"})
    contingency.insert(0, "test_id", test_id)
    expected_min = float(expected.min())
    expected_below_five = int((expected < 5).sum())
    diagnostic = {
        "test_id": test_id,
        "diagnostic": "Expected cells below 5",
        "value": expected_below_five,
        "threshold": 0,
        "flag": "Review sparse expected counts before strong interpretation" if expected_below_five else "No cells below 5",
        "expected_min": expected_min,
    }
    return result, contingency, diagnostic


def _format_p(value: float) -> str:
    return f"{value:.4g}"


def write_report(results: pd.DataFrame, project_root: Path) -> Path:
    """Write a compact, reproducible Markdown report alongside CSV outputs."""

    output = project_root / "outputs" / "non_parametric_report.md"
    lines = [
        "# Non-Parametric Test Analysis",
        "",
        "This report uses the existing synthetic migration-task dataset. The results describe this generated teaching sample only; they are not measurements of real AI agents, Codex runs, production Android work, or a validated benchmark.",
        "",
        "## Design",
        "",
        "The raw observations contain five executions per migration task. Repeated executions are averaged by `ticket_id` when the task is the unit of analysis. The Wilcoxon comparison is paired by task, and the Chi-Square test uses one majority status per task to avoid pseudo-replication. All tests are two-sided with `alpha = 0.05`.",
        "",
        "## Results",
        "",
        "| Test | Statistic | df | p-value | Effect size | Decision |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for _, row in results.iterrows():
        df_value = "-" if pd.isna(row["degrees_of_freedom"]) else f"{row['degrees_of_freedom']:.0f}"
        lines.append(
            f"| {row['test_type']} | {row['statistic_name']} = {row['statistic']:.3f} | {df_value} | {_format_p(row['p_value_two_sided'])} | {row['effect_size_name']} = {row['effect_size']:.3f} | {row['decision_at_alpha_0_05']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "* **Mann-Whitney:** compares independent Hard and Easy task-level execution-time distributions.",
        "* **Wilcoxon:** compares matched task-level accuracy for synthetic agent A and B.",
        "* **Kruskal-Wallis:** tests the omnibus difference among component-area execution-time distributions; a significant result would need post-hoc tests to locate pairwise differences.",
        "* **Chi-Square:** tests whether task difficulty and majority status are associated. Sparse expected counts should be considered when interpreting the result.",
        "",
        "Reproduce with `python analysis/non_parametric_analysis.py`. The raw CSV inputs are not modified.",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def run_analysis(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run all tests and write result, supporting, and diagnostic tables."""

    data_dir = project_root / "data"
    output_dir = project_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = pd.read_csv(data_dir / "migration_tasks.csv")
    observations = pd.read_csv(data_dir / "migration_observations.csv")
    validate_inputs(tasks, observations)
    task_data = task_level_data(tasks, observations)

    mann_result, mann_groups, mann_diag = mann_whitney_difficulty_time(task_data)
    wilcoxon_result, wilcoxon_groups, wilcoxon_diag = wilcoxon_agent_accuracy(observations)
    kruskal_result, kruskal_groups, kruskal_diag = kruskal_component_area_time(task_data)
    chi_result, chi_contingency, chi_diag = chi_square_difficulty_status(tasks, observations)

    results = pd.DataFrame([mann_result, wilcoxon_result, kruskal_result, chi_result])
    group_summary = pd.concat([mann_groups, wilcoxon_groups, kruskal_groups], ignore_index=True)
    diagnostics = pd.DataFrame([mann_diag, wilcoxon_diag, kruskal_diag, chi_diag])

    results.to_csv(output_dir / "non_parametric_results.csv", index=False)
    group_summary.to_csv(output_dir / "non_parametric_group_summaries.csv", index=False)
    chi_contingency.to_csv(output_dir / "non_parametric_contingency_table.csv", index=False)
    diagnostics.to_csv(output_dir / "non_parametric_diagnostics.csv", index=False)
    write_report(results, project_root)
    return results, group_summary, chi_contingency, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the four non-parametric coursework tests.")
    parser.add_argument(
        "--project-root", type=Path, default=Path(__file__).resolve().parents[1],
        help="Repository root containing data/ and outputs/.",
    )
    args = parser.parse_args()
    results, _, _, _ = run_analysis(args.project_root.resolve())
    print(results[["test_type", "statistic", "p_value_two_sided", "decision_at_alpha_0_05"]].to_string(index=False))
    print(f"Wrote outputs under {args.project_root.resolve() / 'outputs'}")


if __name__ == "__main__":
    main()
