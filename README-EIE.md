# EmergentSoft Intelligence Engine (EIE)

A provider-agnostic, deterministic prototype of a reusable Generate → Evaluate → Score → Select → Refine engine for EmergentSoft products.

## Status

**Functional local prototype.** Python standard library only. No GPU, API key, database, paid service, or external model is required for the demo.

This is not a production orchestration platform. It does not yet provide persistence, multi-tenant authorization, distributed execution, model calls, or production security controls.

## Architecture

- **Product adapter:** supplies product-specific candidate generation and domain evaluation.
- **Generator:** produces one or more candidate solutions.
- **Evaluator:** returns normalized metrics and supporting evidence.
- **Reward engine:** computes a weighted score from explicit criteria.
- **Selector:** deterministically chooses the highest-scoring candidate.
- **Refiner:** optionally derives a new candidate from the current best candidate for another iteration.
- **Trace:** records iteration, candidate, metrics, score, and evidence.

## Run the demo

Requires Python 3.10+.

```bash
python examples/digital_south_campaign.py
python -m unittest discover -s tests -v
```

The Digital South example uses **synthetic fixture data** to demonstrate the engine. It is not factory telemetry or a real optimization recommendation.

## Integrating another product

Implement three small callables:
1. `generator(iteration) -> Iterable[Candidate]`
2. `evaluator(candidate) -> Evaluation`
3. optionally, `refiner(best_candidate, best_evaluation, iteration) -> Candidate`

Define product-specific `Criterion` weights and call `run_campaign(...)`. Keep domain logic in the product adapter; do not fork the core.

## Scoring contract

Every metric must be normalized to [0, 1]. For a metric where lower is better, set `direction="min"`; the reward engine inverts it before applying the weight. Criterion weights must have a positive sum.

Scores are decision-support signals, not truth labels. Evaluation evidence and metric provenance must be reviewed before acting on a selected candidate.

## Roadmap

- [x] Deterministic campaign loop and weighted reward
- [x] Optional iterative refinement
- [x] Evidence trace and JSON serialization
- [x] Standard-library unit tests
- [ ] Product adapter contracts and schema versioning
- [ ] Persistent campaign store and replay
- [ ] Model-provider ports (including optional NVIDIA NIM)
- [ ] Human approval gates and policy constraints
- [ ] Authentication, tenant isolation, observability and deployment hardening

## License

See the repository-level license and security policy. This package does not introduce a separate license.
