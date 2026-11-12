"""Evaluate operating scenarios across every shift in an input CSV."""
from pathlib import Path
import json
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from packages.eie_core import Candidate, Criterion, Evaluation, run_campaign
from packages.industrial_twin import Scenario, load_shift_records, simulate

DATA_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "industrial_shift_template.csv"
SHIFT_RECORDS = load_shift_records(DATA_PATH)

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
    return [Candidate(name, {"scenario": name}) for name in SCENARIOS]


def evaluate(candidate: Candidate) -> Evaluation:
    scenario = SCENARIOS[str(candidate.payload["scenario"])]
    shift_results = []
    normalized = {"good_output": [], "uptime": [], "energy_efficiency": []}

    for record in SHIFT_RECORDS:
        result = simulate(record.line, scenario)
        normalized["good_output"].append(min(1.0, result.estimated_good_units / 90.0))
        normalized["uptime"].append(result.uptime_rate)
        good_units_per_kwh = result.estimated_good_units / max(result.estimated_energy_kwh, 1.0)
        normalized["energy_efficiency"].append(min(1.0, good_units_per_kwh / 0.5))
        shift_results.append({
            "timestamp": record.timestamp.isoformat(),
            "line_id": record.line.line_id,
            "data_class": record.line.data_class,
            "simulation": result.to_dict(),
        })

    metrics = {name: statistics.fmean(values) for name, values in normalized.items()}
    return Evaluation(
        candidate_id=candidate.candidate_id,
        metrics=metrics,
        evidence={
            "source": "csv_imported_unverified",
            "input_file": DATA_PATH.name,
            "shift_count": len(SHIFT_RECORDS),
            "shift_results": shift_results,
            "aggregation": "arithmetic_mean_of_per_shift_normalized_metrics",
            "normalization": {
                "good_output_reference_units": 90.0,
                "reference_good_units_per_kwh": 0.5,
            },
        },
    )


if __name__ == "__main__":
    result = run_campaign(
        product="digital-south-industrial-twin",
        objective="compare production-line operating scenarios across CSV shift records",
        generator=generate,
        evaluator=evaluate,
        criteria=[
            Criterion("good_output", 0.50),
            Criterion("uptime", 0.30),
            Criterion("energy_efficiency", 0.20),
        ],
    )
    print(json.dumps(result.to_dict(), indent=2))
