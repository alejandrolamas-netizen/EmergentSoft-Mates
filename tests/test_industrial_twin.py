import unittest

from packages.industrial_twin import MachineLine, Scenario, simulate


class IndustrialTwinTests(unittest.TestCase):
    def setUp(self):
        self.line = MachineLine(
            line_id="test-line", shift_hours=8, units_per_hour=10,
            utilization=0.8, planned_downtime_minutes=20,
            unplanned_downtime_minutes=40, changeover_minutes=30,
            energy_kwh_per_hour=12, quality_rate=0.95,
        )

    def test_baseline_simulation(self):
        result = simulate(self.line, Scenario("baseline"))
        self.assertEqual(result.estimated_energy_kwh, 96)
        self.assertGreater(result.estimated_good_units, 0)
        self.assertEqual(result.assumptions["data_class"], "synthetic_demo_parameters")

    def test_reducing_downtime_increases_available_minutes(self):
        baseline = simulate(self.line, Scenario("baseline"))
        improved = simulate(self.line, Scenario("maintenance", downtime_reduction=0.5))
        self.assertGreater(improved.available_minutes, baseline.available_minutes)
        self.assertGreater(improved.estimated_units, baseline.estimated_units)

    def test_invalid_scenario_rejected(self):
        with self.assertRaises(ValueError):
            Scenario("invalid", downtime_reduction=1.5)


if __name__ == "__main__":
    unittest.main()
