# ECIA architecture baseline

## Product vision

ECIA is EmergentSoft's content-intelligence agent: an autonomous, event-driven, multi-agent system that researches trends, detects opportunities, generates multimodal content, publishes, measures and learns, operating continuously under exception-based human supervision.

## Design principles

1. Decoupled microservice: ECIA is a specialized agent registered in QAIzero.
2. API-first and event-driven: relevant state is exposed through events and APIs.
3. Model-agnostic: Claude, GPT, Gemini and local models are interchangeable behind a port using Hexagonal Architecture.
4. Multi-tenant from day one: workspaces, brands and organizations are isolated at the data and quota levels.
5. Extensible without changing the core: new agents are added as plugins.

## System planes

- Intelligence Plane — trend, research, competitor and SEO agents.
- Generation Plane — copywriter, image, video, podcast and translation agents.
- Governance Plane — brand, compliance and moderation agents.
- Distribution Plane — scheduler, publishing and campaign agents.
- Insight Plane — analytics and learning agents.

## Hexagonal layers

- Driving adapters: REST, GraphQL, gRPC, WebSocket, SSE, CLI and QAIzero SDK.
- Application layer: use cases, command/query handlers, sagas and orchestrator.
- Domain layer: entities, value objects, aggregates, domain events, domain services and policies.
- Ports: `IContentRepository`, `IAIProvider`, `IPublisher`, `IEventBus`.
- Driven adapters: Postgres/Supabase, Redis, S3, Kafka/RabbitMQ, AI providers and social APIs.

## Repository target

```text
ecia/
├── apps/
│   ├── dashboard/          # Next.js + React + TS + Tailwind
│   └── core-api/           # FastAPI: REST + GraphQL + gRPC gateway
├── services/
│   ├── orchestrator/       # Orchestrator Agent (gRPC server)
│   ├── agents/
│   │   ├── trend-agent/
│   │   ├── research-agent/
│   │   ├── competitor-agent/
│   │   ├── seo-agent/
│   │   ├── strategy-agent/
│   │   ├── copywriter-agent/
│   │   ├── image-agent/
│   │   ├── video-agent/
│   │   ├── podcast-agent/
│   │   ├── translation-agent/
│   │   ├── brand-agent/
│   │   ├── compliance-agent/
│   │   ├── scheduler-agent/
│   │   ├── analytics-agent/
│   │   ├── learning-agent/
│   │   ├── campaign-agent/
│   │   ├── publishing-agent/
│   │   ├── moderation-agent/
│   │   └── notification-agent/
│   └── billing-service/
├── packages/
│   ├── domain/
│   ├── ai-providers/
│   ├── social-connectors/
│   ├── event-bus/
│   └── sdk/
│       ├── typescript/
│       ├── python/
│       └── go/
├── infra/
│   ├── terraform/
│   ├── helm/
│   └── k8s/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/
```

## Agent contract

The architecture defines a declarative `AgentCapability` contract including agent type, version, capabilities, supported languages, AI providers, SLA, health endpoint and metrics endpoint.

## Orchestration

The end-to-end Saga is:

`SignalDetected → Strategy → content generation → Brand → Compliance → Scheduler → Publishing → Analytics → Learning → Strategy feedback loop`.

Rejected content routes to Notification.

## QAIzero integration

- ECIA self-registers with QAIzero at startup.
- QAIzero discovers agent capabilities, state and version.
- Tasks can be assigned through gRPC `AssignTask`.
- Progress is streamed through `StreamProgress`.
- `CancelTask` propagates cooperative cancellation.
- QAIzero may request additional instances under demand.
- Heartbeat is every 15 seconds; degradation is reported for automatic failover.

## Security baseline

- OAuth2 + OpenID Connect for human users.
- Scoped API keys for machine-to-machine integrations.
- Short-lived JWTs with rotating refresh tokens.
- mTLS between internal services.
- TLS 1.3 in transit.
- AES-256 at rest for sensitive data.
- Vault or AWS/GCP Secrets Manager for secrets.
- Append-only audit log.
- OWASP ASVS Level 2 baseline.

## Event transport

Kafka carries long-retention domain events and replay for Learning. RabbitMQ handles low-latency agent task queues, acknowledgement/retry and dead-letter queues. Events are idempotent through `idempotency_key` and versioned in a CloudEvents-compatible model.

## Phase 9 billing boundary

The final architecture defines `eica-billing` as a sibling bounded context to `ecia_domain`, with:

- `entitlements.py`
- `subscription.py`
- `marketplace.py`
- `stripe_adapter.py`

The documented Phase 9 verification reports 36/36 tests for the pure billing logic; Stripe integration remains isolated in its adapter.
