"""Regression checks for the four non-parametric coursework tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "analysis"))

from non_parametric_analysis import (  # noqa: E402
    chi_square_difficulty_status,
    kruskal_component_area_time,
    mann_whitney_difficulty_time,
    task_level_data,
    validate_inputs,
    wilcoxon_agent_accuracy,
)


class NonParametricAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = pd.read_csv(PROJECT_ROOT / "data" / "migration_tasks.csv")
        cls.observations = pd.read_csv(PROJECT_ROOT / "data" / "migration_observations.csv")
        validate_inputs(cls.tasks, cls.observations)
        cls.task_data = task_level_data(cls.tasks, cls.observations)

    def test_task_level_aggregation_preserves_one_row_per_task(self) -> None:
        self.assertEqual(len(self.task_data), len(self.tasks))
        self.assertTrue(self.task_data["ticket_id"].is_unique)

    def test_all_four_tests_return_valid_results(self) -> None:
        results = [
            mann_whitney_difficulty_time(self.task_data)[0],
            wilcoxon_agent_accuracy(self.observations)[0],
            kruskal_component_area_time(self.task_data)[0],
            chi_square_difficulty_status(self.tasks, self.observations)[0],
        ]
        self.assertEqual(
            [result["test_type"] for result in results],
            [
                "Mann-Whitney U",
                "Wilcoxon signed-rank",
                "Kruskal-Wallis H",
                "Chi-Square test of independence",
            ],
        )
        for result in results:
            self.assertGreater(result["n_total"], 1)
            self.assertGreaterEqual(result["p_value_two_sided"], 0)
            self.assertLessEqual(result["p_value_two_sided"], 1)
            self.assertGreaterEqual(result["effect_size"], -1)
            self.assertLessEqual(result["effect_size"], 1)

    def test_chi_square_contingency_uses_one_row_per_task(self) -> None:
        result, contingency, _ = chi_square_difficulty_status(self.tasks, self.observations)
        self.assertEqual(result["n_total"], len(self.tasks))
        self.assertEqual(int(contingency.drop(columns="test_id").iloc[:, 1:].to_numpy().sum()), len(self.tasks))

    def test_validation_rejects_non_synthetic_rows(self) -> None:
        invalid_observations = self.observations.copy()
        invalid_observations.loc[0, "data_status"] = "real"
        with self.assertRaisesRegex(ValueError, "data_status=synthetic"):
            validate_inputs(self.tasks, invalid_observations)


if __name__ == "__main__":
    unittest.main()
