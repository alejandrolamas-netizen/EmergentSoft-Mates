"""Connect the industrial scenario simulator to the EIE campaign loop."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from packages.eie_core import Candidate, Criterion, Evaluation, run_campaign
from packages.industrial_twin import MachineLine, Scenario, simulate


LINE = MachineLine(
    line_id="demo-metalworking-line-01",
    shift_hours=8,
    units_per_hour=12,
    utilization=0.82,
    planned_downtime_minutes=20,
    unplanned_downtime_minutes=35,
    changeover_minutes=45,
    energy_kwh_per_hour=18,
    quality_rate=0.96,
)

SCENARIOS = {
    "baseline": Scenario("baseline"),
    "maintenance": Scenario("maintenance", downtime_reduction=0.35),
    "changeover": Scenario("changeover", changeover_reduction=0.50),
    "combined": Scenario(
        "combined", downtime_reduction=0.35,
        changeover_reduction=0.50, utilization_delta=0.03,
    ),
}


def generate(_iteration: int):
    return [
        Candidate(name, {"scenario": name})
        for name in SCENARIOS
    ]


def evaluate(candidate: Candidate) -> Evaluation:
    result = simulate(LINE, SCENARIOS[str(candidate.payload["scenario"])])
    # Normalize against explicit demo reference limits for comparable scoring.
    metrics = {
        "good_output": min(1.0, result.estimated_good_units / 90.0),
        "uptime": result.uptime_rate,
        "energy_efficiency": max(0.0, 1.0 - result.estimated_energy_kwh / 200.0),
    }
    return Evaluation(
        candidate_id=candidate.candidate_id,
        metrics=metrics,
        evidence={
            "source": "synthetic_demo_parameters",
            "simulation": result.to_dict(),
            "normalization": {
                "good_output_reference_units": 90.0,
                "energy_reference_kwh": 200.0,
            },
        },
    )


if __name__ == "__main__":
    result = run_campaign(
        product="digital-south-industrial-twin",
        objective="compare production-line operating scenarios",
        generator=generate,
        evaluator=evaluate,
        criteria=[
            Criterion("good_output", 0.50),
            Criterion("uptime", 0.30),
            Criterion("energy_efficiency", 0.20),
        ],
    )
    print(json.dumps(result.to_dict(), indent=2))
