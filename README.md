# EmergentSoft Mates — ESIA/ECIA

**EmergentSoft · Digital Mate for Enterprise Research & Communication**

## What it is

ESIA/ECIA (Emergent Content Intelligence Agent) is the research and communication Digital Mate within the EmergentSoft M8s architecture.

## Business problem

Enterprises need specialized AI agents that can research, reason, create, coordinate and execute communication workflows under organizational governance.

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
├── apps/                   # Dashboard + Core API
├── services/               # Orchestrator + 19 specialized agents + billing
├── packages/               # Domain, AI providers, connectors, events and SDKs
├── infra/                  # Terraform, Helm and Kubernetes
├── tests/                  # Unit, integration and E2E
└── docs/                   # Architecture and operational documentation
```

The ECIA architecture specifies 19 specialized agents plus an Orchestrator: Trend, Research, Competitor, SEO, Strategy, Copywriter, Image Generation, Video Generation, Podcast, Translation, Brand, Compliance, Scheduler, Publishing, Moderation, Analytics, Learning, Campaign and Notification.

## M8s role

Within M8s, ESIA/ECIA is the research and communication Mate. M8s coordinates it with QAIzero, A-CRM, Sentinel and GreenLedger/Desbank.

## Commercial role

ESIA/ECIA is positioned as an enterprise Digital Mate that can be deployed as part of governed M8s transformations, with SaaS, implementation and enterprise deployment paths defined by the underlying architecture.

## Evidence & status

Architecture baseline established. The complete nine-phase implementation must be populated only from recovered ECIA/ESIA source artifacts. Missing implementation files are not to be fabricated.

## Security & IP

See [`SECURITY.md`](SECURITY.md) and [`LICENSE`](LICENSE).

## Commercial contact

**Alejandro Lamas — Founder & CEO, EmergentSoft**  
https://emergentsoft.io
