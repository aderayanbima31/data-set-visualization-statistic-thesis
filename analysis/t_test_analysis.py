"""Run the three required T-tests on the synthetic migration dataset.

This coursework uses synthetic teaching data only. The results describe this
generated sample; they are not measurements of real AI agents, Codex runs,
production Android work, or a validated benchmark.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ALPHA = 0.05
ONE_SAMPLE_REFERENCE_SECONDS = 75.0
REQUIRED_TASK_COLUMNS = {
    "ticket_id", "component_area", "migration_task", "migration_category", "difficulty"
}
REQUIRED_OBSERVATION_COLUMNS = {
    "observation_id", "ticket_id", "agent_id", "execution_time_sec", "token_usage",
    "accuracy_score", "test_pass_rate", "error_count", "status", "data_status",
}


@dataclass(frozen=True)
class TTestResult:
    """A portable, tabular representation of one T-test result."""

    test_id: str
    test_type: str
    outcome: str
    unit_of_analysis: str
    null_hypothesis: str
    alternative_hypothesis: str
    group_a: str
    group_b_or_reference: str
    n_a: int
    n_b: int | None
    mean_a: float
    mean_b_or_reference: float
    mean_difference_a_minus_b: float
    t_statistic: float
    degrees_of_freedom: float
    p_value_two_sided: float
    confidence_interval_low: float
    confidence_interval_high: float
    effect_size_name: str
    effect_size: float
    decision_at_alpha_0_05: str


def validate_inputs(tasks: pd.DataFrame, observations: pd.DataFrame) -> None:
    """Fail early if the raw teaching inputs no longer meet their specification."""

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
    """Aggregate repeats before testing so a task is not treated as many independent units."""

    task_metrics = (
        observations.groupby("ticket_id", as_index=False)
        .agg(execution_time_sec=("execution_time_sec", "mean"), accuracy_score=("accuracy_score", "mean"))
    )
    return tasks.merge(task_metrics, on="ticket_id", validate="one_to_one")


def _decision(p_value: float) -> str:
    return "Reject H0" if p_value < ALPHA else "Fail to reject H0"


def _cohens_d_one_sample(values: np.ndarray, reference: float) -> float:
    return float((values.mean() - reference) / values.std(ddof=1))


def _cohens_d_paired(differences: np.ndarray) -> float:
    return float(differences.mean() / differences.std(ddof=1))


def _hedges_g_independent(first: np.ndarray, second: np.ndarray) -> float:
    """Return Hedges' g using the pooled-standard-deviation correction."""

    n_first, n_second = len(first), len(second)
    pooled_variance = (
        (n_first - 1) * first.var(ddof=1) + (n_second - 1) * second.var(ddof=1)
    ) / (n_first + n_second - 2)
    cohen_d = (first.mean() - second.mean()) / np.sqrt(pooled_variance)
    correction = 1 - 3 / (4 * (n_first + n_second) - 9)
    return float(correction * cohen_d)


def _welch_degrees_of_freedom(first: np.ndarray, second: np.ndarray) -> float:
    first_term = first.var(ddof=1) / len(first)
    second_term = second.var(ddof=1) / len(second)
    return float((first_term + second_term) ** 2 / (
        first_term**2 / (len(first) - 1) + second_term**2 / (len(second) - 1)
    ))


def one_sample_execution_time_test(task_data: pd.DataFrame) -> TTestResult:
    values = task_data["execution_time_sec"].to_numpy(dtype=float)
    test = stats.ttest_1samp(values, popmean=ONE_SAMPLE_REFERENCE_SECONDS)
    difference = float(values.mean() - ONE_SAMPLE_REFERENCE_SECONDS)
    standard_error = values.std(ddof=1) / np.sqrt(len(values))
    critical_value = stats.t.ppf(1 - ALPHA / 2, df=len(values) - 1)
    interval = (difference - critical_value * standard_error, difference + critical_value * standard_error)
    return TTestResult(
        test_id="one_sample_execution_time",
        test_type="One-sample T-test",
        outcome="Mean task-level execution time (seconds)",
        unit_of_analysis="One task-level mean across its five synthetic executions",
        null_hypothesis=f"Mean execution time = {ONE_SAMPLE_REFERENCE_SECONDS:.0f} seconds",
        alternative_hypothesis=f"Mean execution time != {ONE_SAMPLE_REFERENCE_SECONDS:.0f} seconds",
        group_a="All migration tasks",
        group_b_or_reference=f"Teaching reference: {ONE_SAMPLE_REFERENCE_SECONDS:.0f} seconds",
        n_a=len(values), n_b=None, mean_a=float(values.mean()),
        mean_b_or_reference=ONE_SAMPLE_REFERENCE_SECONDS, mean_difference_a_minus_b=difference,
        t_statistic=float(test.statistic), degrees_of_freedom=float(len(values) - 1),
        p_value_two_sided=float(test.pvalue), confidence_interval_low=float(interval[0]),
        confidence_interval_high=float(interval[1]), effect_size_name="Cohen's d",
        effect_size=_cohens_d_one_sample(values, ONE_SAMPLE_REFERENCE_SECONDS),
        decision_at_alpha_0_05=_decision(float(test.pvalue)),
    )


def paired_agent_accuracy_test(observations: pd.DataFrame) -> TTestResult:
    """Compare agents A and B within each ticket, paired by migration task."""

    task_agent_accuracy = (
        observations.groupby(["ticket_id", "agent_id"], as_index=False)["accuracy_score"]
        .mean().pivot(index="ticket_id", columns="agent_id", values="accuracy_score")
    )
    pairs = task_agent_accuracy[["synthetic-agent-A", "synthetic-agent-B"]].dropna()
    agent_a = pairs["synthetic-agent-A"].to_numpy(dtype=float)
    agent_b = pairs["synthetic-agent-B"].to_numpy(dtype=float)
    differences = agent_a - agent_b
    test = stats.ttest_rel(agent_a, agent_b)
    standard_error = differences.std(ddof=1) / np.sqrt(len(differences))
    critical_value = stats.t.ppf(1 - ALPHA / 2, df=len(differences) - 1)
    interval = (
        differences.mean() - critical_value * standard_error,
        differences.mean() + critical_value * standard_error,
    )
    return TTestResult(
        test_id="paired_agent_accuracy", test_type="Paired-samples T-test",
        outcome="Task-level mean accuracy score (0-1)",
        unit_of_analysis="One matched task with agent-specific mean accuracy",
        null_hypothesis="Mean paired accuracy difference (agent A - agent B) = 0",
        alternative_hypothesis="Mean paired accuracy difference (agent A - agent B) != 0",
        group_a="synthetic-agent-A", group_b_or_reference="synthetic-agent-B",
        n_a=len(agent_a), n_b=len(agent_b), mean_a=float(agent_a.mean()),
        mean_b_or_reference=float(agent_b.mean()), mean_difference_a_minus_b=float(differences.mean()),
        t_statistic=float(test.statistic), degrees_of_freedom=float(len(differences) - 1),
        p_value_two_sided=float(test.pvalue), confidence_interval_low=float(interval[0]),
        confidence_interval_high=float(interval[1]), effect_size_name="Paired Cohen's d_z",
        effect_size=_cohens_d_paired(differences), decision_at_alpha_0_05=_decision(float(test.pvalue)),
    )


def independent_difficulty_time_test(task_data: pd.DataFrame) -> TTestResult:
    """Compare hard and easy tasks with Welch's T-test at the task level."""

    hard = task_data.loc[task_data["difficulty"].eq("Hard"), "execution_time_sec"].to_numpy(dtype=float)
    easy = task_data.loc[task_data["difficulty"].eq("Easy"), "execution_time_sec"].to_numpy(dtype=float)
    if min(len(hard), len(easy)) < 2:
        raise ValueError("The independent test needs at least two hard and two easy tasks.")
    test = stats.ttest_ind(hard, easy, equal_var=False)
    difference = float(hard.mean() - easy.mean())
    standard_error = np.sqrt(hard.var(ddof=1) / len(hard) + easy.var(ddof=1) / len(easy))
    degrees_of_freedom = _welch_degrees_of_freedom(hard, easy)
    critical_value = stats.t.ppf(1 - ALPHA / 2, df=degrees_of_freedom)
    interval = (difference - critical_value * standard_error, difference + critical_value * standard_error)
    return TTestResult(
        test_id="independent_difficulty_time", test_type="Independent-samples Welch T-test",
        outcome="Mean task-level execution time (seconds)",
        unit_of_analysis="One task-level mean across its five synthetic executions",
        null_hypothesis="Mean hard-task time - mean easy-task time = 0",
        alternative_hypothesis="Mean hard-task time - mean easy-task time != 0",
        group_a="Hard tasks", group_b_or_reference="Easy tasks", n_a=len(hard), n_b=len(easy),
        mean_a=float(hard.mean()), mean_b_or_reference=float(easy.mean()),
        mean_difference_a_minus_b=difference, t_statistic=float(test.statistic),
        degrees_of_freedom=degrees_of_freedom, p_value_two_sided=float(test.pvalue),
        confidence_interval_low=float(interval[0]), confidence_interval_high=float(interval[1]),
        effect_size_name="Hedges' g", effect_size=_hedges_g_independent(hard, easy),
        decision_at_alpha_0_05=_decision(float(test.pvalue)),
    )


def assumption_checks(task_data: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    """Record diagnostics; these are not automatic proof that assumptions hold."""

    task_agent_accuracy = (
        observations.groupby(["ticket_id", "agent_id"], as_index=False)["accuracy_score"]
        .mean().pivot(index="ticket_id", columns="agent_id", values="accuracy_score")
    )
    paired_differences = (task_agent_accuracy["synthetic-agent-A"] - task_agent_accuracy["synthetic-agent-B"]).dropna()
    hard = task_data.loc[task_data["difficulty"].eq("Hard"), "execution_time_sec"]
    easy = task_data.loc[task_data["difficulty"].eq("Easy"), "execution_time_sec"]
    rows = [
        ("one_sample_execution_time", "Shapiro-Wilk normality of task-level times", *stats.shapiro(task_data["execution_time_sec"])),
        ("paired_agent_accuracy", "Shapiro-Wilk normality of paired accuracy differences", *stats.shapiro(paired_differences)),
        ("independent_difficulty_time", "Shapiro-Wilk normality of hard-task times", *stats.shapiro(hard)),
        ("independent_difficulty_time", "Shapiro-Wilk normality of easy-task times", *stats.shapiro(easy)),
        ("independent_difficulty_time", "Levene variance-homogeneity diagnostic", *stats.levene(hard, easy, center="median")),
    ]
    return pd.DataFrame(rows, columns=["test_id", "diagnostic", "statistic", "p_value"])


def run_analysis(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw CSVs and write result tables without changing those raw inputs."""

    data_dir, output_dir = project_root / "data", project_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = pd.read_csv(data_dir / "migration_tasks.csv")
    observations = pd.read_csv(data_dir / "migration_observations.csv")
    validate_inputs(tasks, observations)
    task_data = task_level_data(tasks, observations)
    results = pd.DataFrame([
        asdict(one_sample_execution_time_test(task_data)),
        asdict(paired_agent_accuracy_test(observations)),
        asdict(independent_difficulty_time_test(task_data)),
    ])
    diagnostics = assumption_checks(task_data, observations)
    results.to_csv(output_dir / "t_test_results.csv", index=False)
    diagnostics.to_csv(output_dir / "t_test_assumption_checks.csv", index=False)
    return results, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all required T-tests on synthetic coursework data.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    results, diagnostics = run_analysis(args.project_root)
    print("Synthetic T-test analysis completed. Results describe this teaching dataset only.\n")
    print(results[["test_type", "t_statistic", "degrees_of_freedom", "p_value_two_sided", "decision_at_alpha_0_05"]].to_string(index=False))
    print("\nAssumption diagnostics:\n")
    print(diagnostics.to_string(index=False))


if __name__ == "__main__":
    main()
