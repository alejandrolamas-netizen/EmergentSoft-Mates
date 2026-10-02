# EmergentSoft Mates — ESIA/ECIA

**EmergentSoft · Digital Mate for Enterprise Research & Communication**

## Status

**Architecture baseline — implementation recovery / build-out required.**

ESIA/ECIA (Emergent Content Intelligence Agent) is the research and communication Digital Mate within the EmergentSoft M8s architecture.

This repository currently documents the target engineering baseline. It must not be represented as a completed 19-agent production platform until the corresponding source, tests and deployment artifacts are present and verifiable in this repository.

## What it is

ESIA/ECIA is intended to provide governed AI research, reasoning, content and communication workflows for enterprise environments.

## Engineering baseline

The target architecture is based on the original ECIA nine-phase monorepo specification.

### Core principles

- Clean / Hexagonal Architecture + DDD bounded contexts
- API-first and event-driven
- Multi-tenant with `org_id` isolation and quotas
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
├── services/               # Orchestrator + specialized agents + billing
├── packages/               # Domain, AI providers, connectors, events and SDKs
├── infra/                  # Terraform, Helm and Kubernetes
├── tests/                  # Unit, integration and E2E
└── docs/                   # Architecture and operational documentation
```

The target specification describes 19 specialized agents plus an Orchestrator.

## Evidence boundary

The current repository contains the architecture/documentation baseline. Missing implementation files are not fabricated.

Claims about production readiness, agent count, integrations, throughput, security certification or external validation should only be made when supported by code, tests, deployment artifacts or independent evidence.

## M8s role

Within M8s, ESIA/ECIA is the research and communication Mate. M8s is intended to coordinate it with governance, security and other specialized capabilities.

## Commercial role

ESIA/ECIA is intended as an enterprise Digital Mate that can be deployed as part of governed M8s transformations.

## Security & IP

See `SECURITY.md` and `LICENSE`.

## Commercial contact

**Alejandro Lamas — Founder & CEO, EmergentSoft**  
https://emergentsoft.io
