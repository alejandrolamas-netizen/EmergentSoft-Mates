"""Run a no-API industrial optimization example."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from packages.eie_core import Candidate, Criterion, Evaluation, run_campaign


def generate(_iteration: int):
    return [
        Candidate("plan-a", {"schedule": "balanced", "changeovers": 3}),
        Candidate("plan-b", {"schedule": "short-runs", "changeovers": 5}),
        Candidate("plan-c", {"schedule": "long-runs", "changeovers": 2}),
    ]


def evaluate(candidate: Candidate) -> Evaluation:
    # Illustrative normalized fixture values, not measured factory data.
    fixtures = {
        "plan-a": {"throughput": 0.82, "quality": 0.96, "energy": 0.78},
        "plan-b": {"throughput": 0.91, "quality": 0.87, "energy": 0.68},
        "plan-c": {"throughput": 0.76, "quality": 0.94, "energy": 0.91},
    }
    return Evaluation(
        candidate_id=candidate.candidate_id,
        metrics=fixtures[candidate.candidate_id],
        evidence={"source": "synthetic-demo-fixture", "payload": dict(candidate.payload)},
    )


if __name__ == "__main__":
    result = run_campaign(
        product="digital-south",
        objective="select a balanced production schedule",
        generator=generate,
        evaluator=evaluate,
        criteria=[
            Criterion("throughput", 0.4, "max"),
            Criterion("quality", 0.35, "max"),
            Criterion("energy", 0.25, "max"),
        ],
    )
    print(json.dumps(result.to_dict(), indent=2))
