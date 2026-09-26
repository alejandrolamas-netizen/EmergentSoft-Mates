# AWS Marketplace Fulfillment Service

Minimal backend boundary for Agentic Compliance Accelerator SaaS onboarding.

## Responsibilities

- Resolve an AWS Marketplace registration token server-side.
- Retrieve current Marketplace entitlements for a resolved customer.
- Keep Marketplace-specific AWS API calls isolated from ACA domain logic.
- Expose a health endpoint for deployment checks.

## Required environment

- AWS_REGION
- AWS_MARKETPLACE_PRODUCT_CODE

AWS credentials must be supplied by the runtime IAM role/task role. Do not place access keys in source control.

## End-to-end production gates

Before Marketplace publication, connect this service to:

1. The public SaaS signup/landing flow.
2. The AWS Marketplace registration-token callback flow.
3. The ACA organization/tenant model.
4. Subscription and plan lifecycle state.
5. Idempotent customer provisioning.
6. Authentication/session establishment.
7. Production observability and alerting.
8. Automated integration tests against the deployed environment.

This service is an implementation skeleton; it is not a declaration that Marketplace onboarding is production-ready.
