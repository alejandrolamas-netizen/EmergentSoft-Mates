# SaaS Architecture

Agentic Compliance Accelerator is a multi-tenant SaaS application.

## Logical domains
- Compliance assessment
- Requirements/framework management
- Evidence
- Documentation
- Remediation
- Organization and access control
- Subscription
- Entitlements
- Audit events

## Tenant isolation
Customer organizations are logically isolated at the application/data layer. Organization identity must be propagated through authenticated requests and enforced at every data access boundary.

## Billing
Billing and entitlements are a separate business context from the compliance domain.

The ECIA Phase 9 implementation defines:
- entitlements.py
- subscription.py
- marketplace.py
- stripe_adapter.py

The first three modules are pure business logic; the Stripe adapter isolates external billing concerns.

## AWS deployment
The production deployment may use AWS managed compute, database, networking, storage, secrets, observability and AI services. Exact services are deployment-specific and must be documented from the production infrastructure.

## Enterprise limitation
Multi-region deployment, real IdP/SSO integration, SIEM export and contractual enterprise SLA infrastructure are not to be represented as fully implemented merely because corresponding entitlements exist in the business model.
