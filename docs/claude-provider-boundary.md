# Claude provider boundary — EmergentSoft Mates

**Status:** architecture note only. This repository currently documents a target architecture; this file does not claim a working Claude adapter or a production agent runtime.

## Intended responsibility

EmergentSoft Mates may eventually consume a model-agnostic provider port. A Claude-specific adapter belongs behind that port and must not leak Anthropic SDK types into domain logic, public APIs, or other provider implementations.

## Proposed contract

The eventual provider interface should accept:
- a typed task or capability identifier, not an unrestricted system prompt from an end user;
- bounded, explicitly classified context;
- a maximum output-token budget and timeout;
- tenant/request metadata for quota enforcement and audit correlation.

It should return a typed result plus minimal usage metadata, or a normalized provider error. Provider calls must be replaceable by a deterministic mock in tests.

## Security and governance requirements

- Keep the Anthropic key server-side in an approved secret store; never commit credentials or send them to browser clients.
- Enforce authentication, tenant isolation, authorization, input limits, output limits, rate limits and durable spend/request quotas outside the model.
- Do not assume model output is trusted. Validate it against a schema and treat it as untrusted data.
- Do not give the provider action tools, write permissions, arbitrary URL access, or operational control in the first pilot.
- Use synthetic or approved, minimized data only. Do not pass patient-identifiable or otherwise regulated information without a separate governance review.
- Do not log secrets, full prompts or full responses by default.
- Keep Claude disabled until the adapter, tests, quotas and provider/account spend controls are verified.

## Relationship to MedDigtwin

For the first Operational Digital Twins pilot, MedDigtwin's FastAPI backend is the proposed execution boundary because it already owns tenant authentication and synthetic simulation state. Mates should not independently call Claude for the same use case until ownership, routing and quota accounting are explicitly designed; otherwise requests could bypass consistent authorization and cost controls.

## Acceptance gates before implementation

- [ ] Inspect and establish the actual runtime/module structure before creating provider code.
- [ ] Define the provider port from existing code, not from this document alone.
- [ ] Add mocked contract tests and provider error/timeout tests.
- [ ] Demonstrate tenant isolation and durable quota enforcement.
- [ ] Verify the model identifier, API account configuration and external spend controls.
- [ ] Review the diff and run the available checks before merge.

No source adapter, SDK dependency, deployment workflow or credentials are added by this documentation-only change.
