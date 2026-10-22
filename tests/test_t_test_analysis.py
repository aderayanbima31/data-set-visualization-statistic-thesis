"""Regression checks for the synthetic T-test coursework analysis."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "analysis"))

from t_test_analysis import (  # noqa: E402
    independent_difficulty_time_test,
    one_sample_execution_time_test,
    paired_agent_accuracy_test,
    task_level_data,
    validate_inputs,
)


class TTestAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = pd.read_csv(PROJECT_ROOT / "data" / "migration_tasks.csv")
        cls.observations = pd.read_csv(PROJECT_ROOT / "data" / "migration_observations.csv")
        validate_inputs(cls.tasks, cls.observations)
        cls.task_data = task_level_data(cls.tasks, cls.observations)

    def test_task_level_aggregation_preserves_one_row_per_task(self) -> None:
        self.assertEqual(len(self.task_data), len(self.tasks))
        self.assertTrue(self.task_data["ticket_id"].is_unique)

    def test_all_three_required_t_tests_return_finite_results(self) -> None:
        results = [
            one_sample_execution_time_test(self.task_data),
            paired_agent_accuracy_test(self.observations),
            independent_difficulty_time_test(self.task_data),
        ]
        self.assertEqual(
            [result.test_type for result in results],
            ["One-sample T-test", "Paired-samples T-test", "Independent-samples Welch T-test"],
        )
        for result in results:
            self.assertGreater(result.n_a, 1)
            self.assertGreater(result.p_value_two_sided, 0)
            self.assertLessEqual(result.p_value_two_sided, 1)
            self.assertLess(result.confidence_interval_low, result.confidence_interval_high)

    def test_validation_rejects_non_synthetic_rows(self) -> None:
        invalid_observations = self.observations.copy()
        invalid_observations.loc[0, "data_status"] = "real"
        with self.assertRaisesRegex(ValueError, "data_status=synthetic"):
            validate_inputs(self.tasks, invalid_observations)


if __name__ == "__main__":
    unittest.main()
