# EIE — Architecture and integration contract

## Design intent

Transfer the useful systems pattern demonstrated by reward-guided inference-time search into a domain-neutral enterprise engine. EIE does not reproduce protein design algorithms, biological reward functions, or NVIDIA proprietary components.

## Execution flow

```text
Product Adapter
  └─ Generator(iteration)
       └─ Candidate[]
            └─ Evaluator(candidate)
                 └─ Evaluation(metrics, evidence)
                      └─ Weighted Reward
                           └─ Deterministic Selector
                                └─ Optional Refiner → next iteration
                                     └─ CampaignResult + trace
```

## Domain boundaries

| Product | Candidate examples | Evaluation examples |
|---|---|---|
| Digital South | production schedule, maintenance plan | throughput, quality, energy, downtime |
| Hospeda AI | workflow or response plan | task completion, policy compliance, latency |
| Agentic Compliance | control remediation plan | control coverage, evidence completeness, risk |
| MedDigtwin | care/workflow scenario | protocol adherence, completeness, review status |

These are integration examples, not implemented product adapters or validated domain metrics. Clinical, legal, safety, and operational decisions require qualified human review.

## Critical invariants

- The core is model-agnostic and does not import provider SDKs.
- Metrics are normalized to [0, 1], with direction declared per criterion.
- Every evaluation is tied to the candidate ID it evaluated.
- Selection is deterministic for equal inputs; ties break by candidate ID.
- Evidence is retained in the result trace.
- Synthetic demo data is clearly labeled and must never be represented as operational evidence.

## Next engineering increments

1. Version the Candidate, Evaluation, and Criterion schemas.
2. Add a persistence port with SQLite as an optional local adapter.
3. Add provider ports with timeouts, retries, budgets, and explicit opt-in.
4. Add human approval gates before executing consequential actions.
5. Add tenant isolation, authentication, secrets management, audit retention, and deployment controls before production use.
