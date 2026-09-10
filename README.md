# EmergentSoft Mates — ESIA/ECIA

ESIA/ECIA (Emergent Content Intelligence Agent) is the research and communication Digital Mate within the EmergentSoft M8s architecture.

## Engineering baseline

The implementation target is the original ECIA nine-phase monorepo defined in the EmergentSoft Engineering OS documentation. This repository must contain recovered ECIA/ESIA source; unrelated Sentinel, GreenLedger, or QAIzero standalone projects must not be substituted for it.

### Core principles

- Clean / Hexagonal Architecture + DDD bounded contexts
- API-first and event-driven
- Multi-tenant from day one with `org_id` isolation and quotas
- Model-agnostic AI providers behind ports
- Extensible agent/plugin model
- REST, GraphQL, gRPC, WebSocket/SSE and CLI interfaces
- Kafka for domain events and RabbitMQ for low-latency task queues
- QAIzero registration, discovery, task assignment, progress, cancellation and health integration
- Zero-trust security: OAuth2/OIDC, scoped API keys, short-lived JWTs, mTLS, TLS 1.3, AES-256 and append-only audit logging

## Target monorepo structure

```text
ecia/
├── apps/
│   ├── dashboard/          # Next.js + React + TypeScript + Tailwind
│   └── core-api/           # FastAPI REST + GraphQL + gRPC gateway
├── services/
│   ├── orchestrator/       # Orchestrator Agent
│   ├── agents/             # 19 specialized agents
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

The ECIA architecture specifies 19 specialized agents plus an Orchestrator: Trend, Research, Competitor, SEO, Strategy, Copywriter, Image Generation, Video Generation, Podcast, Translation, Brand, Compliance, Scheduler, Publishing, Moderation, Analytics, Learning, Campaign and Notification.

## M8s role

Within M8s, ESIA/ECIA is the research and communication Mate. M8s coordinates it with QAIzero, A-CRM, Sentinel and GreenLedger/Desbank.

## Repository status

Architecture baseline established. The complete nine-phase implementation must be populated only from recovered ECIA/ESIA source artifacts. Missing implementation files are not to be fabricated.
