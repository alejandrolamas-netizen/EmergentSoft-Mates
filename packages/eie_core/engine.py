"""A small, deterministic implementation of Generate → Evaluate → Score → Select → Refine.

The core deliberately has no model, network, database, or GPU dependency.
Product-specific behavior is injected through ordinary Python callables.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Callable, Iterable, Mapping, Sequence
import hashlib
import json


@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float
    direction: str = "max"  # "max" or "min"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("criterion name cannot be empty")
        if self.weight < 0:
            raise ValueError("criterion weight cannot be negative")
        if self.direction not in {"max", "min"}:
            raise ValueError("direction must be 'max' or 'min'")


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    payload: Mapping[str, object]
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Evaluation:
    candidate_id: str
    metrics: Mapping[str, float]
    evidence: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CampaignResult:
    campaign_id: str
    selected: Candidate
    score: float
    evaluations: tuple[Evaluation, ...]
    scores: Mapping[str, float]
    iterations: int
    created_at: str
    trace: tuple[Mapping[str, object], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "campaign_id": self.campaign_id,
            "selected": asdict(self.selected),
            "score": self.score,
            "evaluations": [asdict(item) for item in self.evaluations],
            "scores": dict(self.scores),
            "iterations": self.iterations,
            "created_at": self.created_at,
            "trace": [dict(item) for item in self.trace],
        }


Generator = Callable[[int], Iterable[Candidate]]
Evaluator = Callable[[Candidate], Evaluation]
Refiner = Callable[[Candidate, Evaluation, int], Candidate]


def weighted_reward(evaluation: Evaluation, criteria: Sequence[Criterion]) -> float:
    """Return a weighted mean; metric values must be finite and in [0, 1]."""
    total_weight = sum(item.weight for item in criteria)
    if not criteria or total_weight <= 0:
        raise ValueError("at least one criterion with positive total weight is required")
    score = 0.0
    for criterion in criteria:
        if criterion.name not in evaluation.metrics:
            raise ValueError(f"missing metric: {criterion.name}")
        value = float(evaluation.metrics[criterion.name])
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"metric {criterion.name!r} must be normalized to [0, 1]")
        if criterion.direction == "min":
            value = 1.0 - value
        score += value * criterion.weight
    return score / total_weight


def _campaign_id(product: str, objective: str, candidates: Sequence[Candidate]) -> str:
    material = json.dumps(
        {"product": product, "objective": objective,
         "candidate_ids": [c.candidate_id for c in candidates]},
        sort_keys=True,
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def run_campaign(
    *,
    product: str,
    objective: str,
    generator: Generator,
    evaluator: Evaluator,
    criteria: Sequence[Criterion],
    refiner: Refiner | None = None,
    iterations: int = 1,
) -> CampaignResult:
    """Run a bounded campaign and return a reproducible evidence trace.

    Each iteration evaluates all candidates generated for that iteration.
    The best candidate is passed to the refiner for the next iteration.
    """
    if not product.strip() or not objective.strip():
        raise ValueError("product and objective are required")
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    if iterations > 1 and refiner is None:
        raise ValueError("refiner is required when iterations > 1")

    candidates = list(generator(0))
    if not candidates:
        raise ValueError("generator returned no candidates")

    all_evaluations: list[Evaluation] = []
    all_scores: dict[str, float] = {}
    trace: list[Mapping[str, object]] = []
    best_candidate: Candidate | None = None
    best_evaluation: Evaluation | None = None
    best_score = float("-inf")

    for iteration in range(iterations):
        if iteration > 0:
            assert refiner is not None and best_candidate is not None and best_evaluation is not None
            candidates = [refiner(best_candidate, best_evaluation, iteration)]

        if not candidates:
            raise ValueError(f"no candidates generated at iteration {iteration}")

        seen: set[str] = set()
        for candidate in candidates:
            if not candidate.candidate_id or candidate.candidate_id in seen:
                raise ValueError("candidate IDs must be non-empty and unique per iteration")
            seen.add(candidate.candidate_id)
            evaluation = evaluator(candidate)
            if evaluation.candidate_id != candidate.candidate_id:
                raise ValueError("evaluator returned an evaluation for a different candidate")
            score = weighted_reward(evaluation, criteria)
            all_evaluations.append(evaluation)
            all_scores[candidate.candidate_id] = score
            trace.append({
                "iteration": iteration,
                "candidate_id": candidate.candidate_id,
                "metrics": dict(evaluation.metrics),
                "score": round(score, 6),
                "evidence": dict(evaluation.evidence),
            })
            if score > best_score or (
                score == best_score and
                (best_candidate is None or candidate.candidate_id < best_candidate.candidate_id)
            ):
                best_candidate, best_evaluation, best_score = candidate, evaluation, score

    assert best_candidate is not None
    return CampaignResult(
        campaign_id=_campaign_id(product, objective, all_evaluations and [
            Candidate(item.candidate_id, {}) for item in all_evaluations
        ] or candidates),
        selected=best_candidate,
        score=best_score,
        evaluations=tuple(all_evaluations),
        scores=all_scores,
        iterations=iterations,
        created_at=datetime.now(timezone.utc).isoformat(),
        trace=tuple(trace),
    )
