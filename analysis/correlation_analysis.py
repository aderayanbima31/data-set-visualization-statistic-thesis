"""Complete the five correlation exercises for the synthetic migration data.

The raw CSV files are read-only inputs. Repeated observations are averaged per
ticket before relationship tests that use execution metrics, so one task is
the unit of analysis and repeated runs do not create pseudo-replication.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ALPHA = 0.05
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"


def validate(tasks: pd.DataFrame, observations: pd.DataFrame) -> None:
    required_tasks = {
        "ticket_id", "component_area", "migration_category", "difficulty"
    }
    required_observations = {
        "observation_id", "ticket_id", "execution_time_sec", "token_usage",
        "accuracy_score", "test_pass_rate", "error_count", "data_status"
    }
    missing_tasks = required_tasks.difference(tasks.columns)
    missing_observations = required_observations.difference(observations.columns)
    if missing_tasks or missing_observations:
        raise ValueError(
            f"Missing columns: tasks={sorted(missing_tasks)}, "
            f"observations={sorted(missing_observations)}"
        )
    if tasks["ticket_id"].isna().any() or tasks["ticket_id"].duplicated().any():
        raise ValueError("Task IDs must be present and unique.")
    if observations["observation_id"].duplicated().any():
        raise ValueError("Observation IDs must be unique.")
    if not observations["ticket_id"].isin(tasks["ticket_id"]).all():
        raise ValueError("Every observation must reference a known task.")
    if not observations["data_status"].eq("synthetic").all():
        raise ValueError("This report only accepts synthetic observations.")


def task_level_data(tasks: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    metrics = (
        observations.groupby("ticket_id", as_index=False)
        .agg(
            execution_time_sec=("execution_time_sec", "mean"),
            token_usage=("token_usage", "mean"),
            accuracy_score=("accuracy_score", "mean"),
            test_pass_rate=("test_pass_rate", "mean"),
            error_count=("error_count", "mean"),
        )
    )
    return tasks.merge(metrics, on="ticket_id", validate="one_to_one")


def decision(p_value: float) -> str:
    return "Significant at alpha=0.05" if p_value < ALPHA else "Not significant at alpha=0.05"


def format_p(p_value: float) -> str:
    return "<0.001" if p_value < 0.001 else f"{p_value:.4f}"


def contingency_coefficient(table: pd.DataFrame) -> tuple[float, float, float, int]:
    chi2, p_value, degrees_of_freedom, _ = stats.chi2_contingency(table, correction=False)
    coefficient = float(np.sqrt(chi2 / (chi2 + table.to_numpy().sum())))
    return coefficient, float(p_value), float(chi2), int(degrees_of_freedom)


def phi_coefficient(table: pd.DataFrame) -> tuple[float, float, float, int]:
    chi2, p_value, degrees_of_freedom, _ = stats.chi2_contingency(table, correction=False)
    a, b = table.iloc[0, 0], table.iloc[0, 1]
    c, d = table.iloc[1, 0], table.iloc[1, 1]
    denominator = np.sqrt(table.sum(axis=1).prod() * table.sum(axis=0).prod())
    coefficient = float((a * d - b * c) / denominator)
    return coefficient, float(p_value), float(chi2), int(degrees_of_freedom)


def run() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    tasks = pd.read_csv(DATA_DIR / "migration_tasks.csv")
    observations = pd.read_csv(DATA_DIR / "migration_observations.csv")
    validate(tasks, observations)
    task_data = task_level_data(tasks, observations)

    results: list[dict[str, object]] = []
    tables: dict[str, pd.DataFrame] = {}

    # Point-biserial: continuous task time vs a truly binary difficulty subset.
    easy_hard = task_data[task_data["difficulty"].isin(["Easy", "Hard"])].copy()
    easy_hard["is_hard"] = (easy_hard["difficulty"] == "Hard").astype(int)
    point_biserial = stats.pointbiserialr(
        easy_hard["is_hard"], easy_hard["execution_time_sec"]
    )
    results.append({
        "method": "Point-Biserial",
        "variables": "is_hard (Easy vs Hard) and mean execution_time_sec",
        "unit_of_analysis": "Task-level means; Easy and Hard tasks only",
        "n": len(easy_hard),
        "coefficient": float(point_biserial.statistic),
        "p_value": float(point_biserial.pvalue),
        "decision": decision(float(point_biserial.pvalue)),
        "interpretation": "Hard tasks have higher mean execution time in this synthetic sample.",
    })

    # Contingency coefficient: nominal component area vs nominal/ordinal label.
    cc_table = pd.crosstab(tasks["component_area"], tasks["difficulty"])
    cc, cc_p, cc_chi2, cc_df = contingency_coefficient(cc_table)
    tables["contingency_component_area_by_difficulty"] = cc_table
    results.append({
        "method": "Contingency Coefficient (CC)",
        "variables": "component_area and difficulty",
        "unit_of_analysis": "Task catalog rows",
        "n": len(tasks),
        "coefficient": cc,
        "p_value": cc_p,
        "decision": decision(cc_p),
        "chi_square": cc_chi2,
        "degrees_of_freedom": cc_df,
        "interpretation": "The association between component area and difficulty is weak and not statistically significant.",
    })

    # Phi: two binary variables derived at task level.
    phi_data = task_data.copy()
    phi_data["is_hard"] = (phi_data["difficulty"] == "Hard").astype(int)
    phi_data["has_error"] = (phi_data["error_count"] > 0).astype(int)
    phi_table = pd.crosstab(phi_data["is_hard"], phi_data["has_error"]).reindex(
        index=[0, 1], columns=[0, 1], fill_value=0
    )
    phi, phi_p, phi_chi2, phi_df = phi_coefficient(phi_table)
    tables["phi_is_hard_by_has_error"] = phi_table
    results.append({
        "method": "Phi (phi)",
        "variables": "is_hard (Hard vs non-Hard) and has_error",
        "unit_of_analysis": "Task-level means; has_error means any positive mean error count",
        "n": len(phi_data),
        "coefficient": phi,
        "p_value": phi_p,
        "decision": decision(phi_p),
        "chi_square": phi_chi2,
        "degrees_of_freedom": phi_df,
        "interpretation": "Hard-task status and the presence of errors show a weak, non-significant association.",
    })

    # Spearman: ordered difficulty vs monotonic execution time.
    spearman_data = task_data.copy()
    spearman_data["difficulty_rank"] = spearman_data["difficulty"].map(
        {"Easy": 1, "Medium": 2, "Hard": 3}
    )
    spearman = stats.spearmanr(
        spearman_data["difficulty_rank"], spearman_data["execution_time_sec"]
    )
    results.append({
        "method": "Spearman Rank",
        "variables": "difficulty rank (Easy=1, Medium=2, Hard=3) and mean execution_time_sec",
        "unit_of_analysis": "Task-level means",
        "n": len(spearman_data),
        "coefficient": float(spearman.statistic),
        "p_value": float(spearman.pvalue),
        "decision": decision(float(spearman.pvalue)),
        "interpretation": "Higher difficulty is strongly associated with longer mean execution time.",
    })

    # Pearson: two continuous task-level means.
    pearson = stats.pearsonr(task_data["execution_time_sec"], task_data["token_usage"])
    results.append({
        "method": "Pearson Product-Moment",
        "variables": "mean execution_time_sec and mean token_usage",
        "unit_of_analysis": "Task-level means",
        "n": len(task_data),
        "coefficient": float(pearson.statistic),
        "p_value": float(pearson.pvalue),
        "decision": decision(float(pearson.pvalue)),
        "interpretation": "Execution time and token usage have a strong positive linear association.",
    })

    results_frame = pd.DataFrame(results)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_frame.to_csv(OUTPUT_DIR / "correlation_results.csv", index=False)

    table_rows = []
    for table_name, table in tables.items():
        for row_label, row in table.iterrows():
            for column_label, value in row.items():
                table_rows.append({
                    "table": table_name,
                    "row": row_label,
                    "column": column_label,
                    "count": int(value),
                })
    pd.DataFrame(table_rows).to_csv(
        OUTPUT_DIR / "correlation_contingency_tables.csv", index=False
    )

    report_lines = [
        "# Correlation Analysis Homework",
        "",
        "## Scope and data",
        "",
        "This report completes the five requested correlation exercises using the project’s synthetic migration dataset. The task catalog contains 36 migration tasks and the observation file contains repeated simulated executions. For relationships involving execution metrics, repeated observations are averaged within `ticket_id`; therefore, the task is the unit of analysis.",
        "",
        "The variables `execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, and `error_count` are simulated teaching metrics. The results describe this generated sample only and are not evidence about real AI agents, Codex runs, production Android work, or a validated benchmark.",
        "",
        "## Variable preparation",
        "",
        "- Point-Biserial uses only Easy and Hard tasks so `difficulty` is genuinely binary (`is_hard`).",
        "- Contingency Coefficient uses the task-catalog relationship between nominal `component_area` and `difficulty`.",
        "- Phi uses two binary task-level variables: `is_hard` (Hard vs non-Hard) and `has_error` (any positive mean error count vs none).",
        "- Spearman converts the ordered difficulty labels to ranks: Easy=1, Medium=2, Hard=3.",
        "- Pearson uses the two continuous task-level means `execution_time_sec` and `token_usage`.",
        "",
        "## Results",
        "",
        "| Method | Variables | n | Coefficient | p-value | Decision |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in results_frame.to_dict("records"):
        report_lines.append(
            f"| {row['method']} | {row['variables']} | {row['n']} | "
            f"{row['coefficient']:.4f} | {format_p(row['p_value'])} | {row['decision']} |"
        )

    easy_mean = easy_hard.loc[easy_hard["difficulty"].eq("Easy"), "execution_time_sec"].mean()
    hard_mean = easy_hard.loc[easy_hard["difficulty"].eq("Hard"), "execution_time_sec"].mean()
    report_lines += [
        "",
        "## Formulas used",
        "",
        "- Point-Biserial: `r_pb = ((M1 - M0) / s_y) * sqrt(pq)`.",
        "- Contingency Coefficient: `CC = sqrt(chi-square / (chi-square + N))`. ",
        "- Phi: `phi = (ad - bc) / sqrt((a+b)(c+d)(a+c)(b+d))` for a 2x2 table.",
        "- Spearman Rank: `rho = 1 - 6*sum(d^2) / (n*(n^2 - 1))` when there are no tied ranks.",
        "- Pearson Product-Moment: covariance of the two continuous variables divided by the product of their standard deviations.",
        "",
        "## Supporting values",
        "",
        f"For the Point-Biserial comparison, mean execution time was **{easy_mean:.2f} seconds** for Easy tasks and **{hard_mean:.2f} seconds** for Hard tasks.",
        "",
        "The Contingency Coefficient uses the full 6 x 3 task table (`component_area` by `difficulty`), while Phi uses a 2 x 2 table (`is_hard` by `has_error`). Complete cell counts are saved in `outputs/correlation_contingency_tables.csv`.",
        "",
        "## Conclusions by method",
        "",
        "1. **Point-Biserial:** Appropriate for one binary nominal variable and one continuous variable. Here it is suitable for comparing Easy versus Hard tasks against execution time. Hard tasks took longer on average, and the association is statistically significant in this synthetic sample.",
        "2. **Contingency Coefficient:** Appropriate for testing association between categorical variables using a contingency table and chi-square. It is suitable for `component_area` versus `difficulty`, but the observed association is weak and not statistically significant.",
        "3. **Phi:** Appropriate only when both variables are binary. It is suitable for `is_hard` versus `has_error` after the explicit binary transformation. The association is weak and not statistically significant.",
        "4. **Spearman Rank:** Appropriate for ordinal variables or monotonic relationships without requiring a linear-normal relationship. It is suitable for ordered difficulty versus execution time and shows a strong positive association.",
        "5. **Pearson Product-Moment:** Appropriate for two continuous variables when a linear relationship is the target. It is suitable for execution time versus token usage and shows a strong positive linear association.",
        "",
        "## Final selection",
        "",
        "The best method depends on the measurement scale, not on the strength of the result alone. For the natural variable pairs in this dataset, use **Pearson** for two continuous metrics such as execution time and token usage; **Spearman** for ordered difficulty and a metric such as execution time; **Contingency Coefficient** for multi-category variables such as component area and difficulty; **Phi** only for two binary variables; and **Point-Biserial** for one binary variable paired with one continuous metric. These conclusions are exploratory and limited to the synthetic sample.",
        "",
    ]
    (OUTPUT_DIR / "correlation_homework_report.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    return results_frame, tables


if __name__ == "__main__":
    frame, _ = run()
    print(frame[["method", "coefficient", "p_value", "decision"]].to_string(index=False))
