import unittest

from packages.eie_core import Candidate, Criterion, Evaluation, run_campaign, weighted_reward


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.criteria = [Criterion("quality", 0.7), Criterion("latency", 0.3, "min")]

    def test_weighted_reward_inverts_min_metric(self):
        evaluation = Evaluation("x", {"quality": 0.8, "latency": 0.2})
        self.assertAlmostEqual(weighted_reward(evaluation, self.criteria), 0.8)

    def test_campaign_selects_best_candidate(self):
        candidates = [
            Candidate("slow", {"kind": "slow"}),
            Candidate("fast", {"kind": "fast"}),
        ]

        def evaluate(candidate):
            values = {
                "slow": {"quality": 0.7, "latency": 0.8},
                "fast": {"quality": 0.9, "latency": 0.3},
            }[candidate.candidate_id]
            return Evaluation(candidate.candidate_id, values, {"fixture": True})

        result = run_campaign(
            product="test", objective="select", generator=lambda _: candidates,
            evaluator=evaluate, criteria=self.criteria,
        )
        self.assertEqual(result.selected.candidate_id, "fast")
        self.assertEqual(len(result.trace), 2)

    def test_refinement_runs_between_iterations(self):
        def generator(_):
            return [Candidate("v1", {"version": 1})]

        def evaluator(candidate):
            quality = 0.5 if candidate.candidate_id == "v1" else 0.95
            return Evaluation(candidate.candidate_id, {"quality": quality})

        def refine(candidate, evaluation, iteration):
            return Candidate(f"v{iteration + 1}", {"version": iteration + 1})

        result = run_campaign(
            product="test", objective="refine", generator=generator,
            evaluator=evaluator, criteria=[Criterion("quality", 1.0)],
            refiner=refine, iterations=3,
        )
        self.assertEqual(result.selected.candidate_id, "v3")
        self.assertEqual(len(result.evaluations), 3)

    def test_rejects_out_of_range_metric(self):
        with self.assertRaises(ValueError):
            weighted_reward(Evaluation("x", {"quality": 1.2}), [Criterion("quality", 1.0)])


if __name__ == "__main__":
    unittest.main()
