"""Generate the reproducible synthetic inputs used by the Step 3B notebook.

The execution metrics in this module are simulated teaching data. They are not
measurements from Codex, an AI agent, a production Android project, or a
validated benchmark.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path


SEED = 20260930
REPETITIONS_PER_TASK = 5
AGENTS = ("synthetic-agent-A", "synthetic-agent-B", "synthetic-agent-C")
STATUS_LABELS = ("Passed", "Passed with fixes", "Failed")


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def generate_observations(task_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Return deterministic synthetic execution observations for each task."""

    rng = random.Random(SEED)
    difficulty_time = {"Easy": 42.0, "Medium": 68.0, "Hard": 96.0}
    difficulty_penalty = {"Easy": 0.00, "Medium": 0.035, "Hard": 0.075}
    area_time = {
        "App Bar": 3.0,
        "Balance": 8.0,
        "Quick Action": 0.0,
        "Promo": 6.0,
        "Transactions": 10.0,
        "UI States": 14.0,
    }
    category_time = {"Component": 0.0, "Styling": 8.0, "Behavior": 14.0, "State": 12.0}

    observations: list[dict[str, object]] = []
    sequence = 0
    for task_index, task in enumerate(task_rows, start=1):
        difficulty = task["difficulty"]
        category = task["migration_category"]
        base_time = difficulty_time[difficulty] + area_time[task["component_area"]] + category_time[category]

        for repetition in range(1, REPETITIONS_PER_TASK + 1):
            sequence += 1
            is_plausible_edge_case = repetition == REPETITIONS_PER_TASK and task_index in {6, 22, 34}
            time = max(12.0, rng.gauss(base_time, base_time * 0.16))
            tokens = max(500, int(round(rng.gauss(1200 + base_time * 13, 130))))
            accuracy = clamp(rng.gauss(0.955 - difficulty_penalty[difficulty] - (0.018 if category in {"Behavior", "State"} else 0), 0.028), 0.60, 0.995)
            pass_rate = clamp(rng.gauss(0.975 - difficulty_penalty[difficulty] * 0.65, 0.035), 0.55, 1.0)
            errors = max(0, int(round(rng.gauss(0.25 + difficulty_penalty[difficulty] * 5 + (0.35 if category in {"Behavior", "State"} else 0), 0.75))))

            # These are deliberately plausible synthetic edge cases so that the
            # notebook demonstrates the 1.5 x IQR rule with reviewable results.
            if is_plausible_edge_case:
                time *= 2.35
                tokens = int(tokens * 1.80)
                accuracy = max(0.60, accuracy - 0.16)
                pass_rate = max(0.55, pass_rate - 0.20)
                errors += 4

            if accuracy < 0.70 or pass_rate < 0.75 or errors >= 4:
                status = "Failed"
            elif accuracy < 0.88 or pass_rate < 0.90 or errors >= 2:
                status = "Passed with fixes"
            else:
                status = "Passed"

            observations.append(
                {
                    "observation_id": f"OBS-{sequence:03d}",
                    "ticket_id": task["ticket_id"],
                    "agent_id": AGENTS[(sequence - 1) % len(AGENTS)],
                    "execution_time_sec": round(time, 1),
                    "token_usage": tokens,
                    "accuracy_score": round(accuracy, 3),
                    "test_pass_rate": round(pass_rate, 3),
                    "error_count": errors,
                    "status": status,
                    "data_status": "synthetic",
                }
            )
    return observations


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    task_path = data_dir / "migration_tasks.csv"
    observation_path = data_dir / "migration_observations.csv"

    with task_path.open(newline="", encoding="utf-8") as handle:
        task_rows = list(csv.DictReader(handle))
    observations = generate_observations(task_rows)

    fieldnames = [
        "observation_id",
        "ticket_id",
        "agent_id",
        "execution_time_sec",
        "token_usage",
        "accuracy_score",
        "test_pass_rate",
        "error_count",
        "status",
        "data_status",
    ]

    with observation_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(observations)

    print(f"Generated {len(task_rows)} tasks and {len(observations)} synthetic observations with seed {SEED}.")
    print(f"Wrote {observation_path}")


if __name__ == "__main__":
    main()
