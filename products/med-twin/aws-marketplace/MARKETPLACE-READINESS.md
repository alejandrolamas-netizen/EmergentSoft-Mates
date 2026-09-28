# EmergentSoft Med Twin — AWS Marketplace Readiness Contract

This folder defines the Marketplace integration contract for Med Twin. It is intentionally separate from the Med Twin application source.

## Target model

SaaS Contract on AWS Marketplace.

## Required architecture

- AWS-hosted application component owned/managed by EmergentSoft.
- HTTPS fulfillment/registration endpoint.
- x-amzn-marketplace-token capture.
- Server-side ResolveCustomer.
- CustomerAWSAccountId and LicenseArn as the primary customer identifiers.
- GetEntitlements for subscription/dimension verification.
- Tenant isolation at application and persistence layers.
- Short-lived application session after successful Marketplace verification.
- Periodic entitlement revalidation.
- CloudWatch audit/security logging.
- Encryption in transit and at rest.
- Secrets Manager for credentials.
- IAM roles and GitHub OIDC for deployment.

## Healthcare-specific gates

Med Twin must keep a strict separation between Marketplace entitlement and clinical authorization.

- Marketplace subscription grants software access, not clinical authority.
- Clinical data must be tenant-isolated.
- Access must be authenticated and authorized.
- Data classification and retention must be documented.
- PHI/PII handling must be explicitly documented before production use.
- Any clinical decision-support behavior must be documented with appropriate human oversight and product/regulatory review.
- Model outputs must be traceable to model/version, input context and audit event where applicable.
- Backup, deletion and incident-response procedures must be documented.
- Customer-facing security/privacy documentation must be complete before Marketplace submission.

## NVIDIA integration targets

NVIDIA NIM, Triton Inference Server, NeMo, CUDA, TensorRT, NVIDIA AI Enterprise, DGX Cloud, AI Blueprints and NGC can be exposed as optional infrastructure/model adapters.

The product should not hard-code a dependency on any single NVIDIA service unless the commercial SKU explicitly requires it.

## Microsoft integration targets

Microsoft Foundry/Azure AI, Azure OpenAI, Entra ID, Fabric, Defender for Cloud, Purview, Power Platform, Teams, Dynamics 365 and GitHub can be exposed as optional enterprise adapters.

The product should not hard-code a dependency on any single Microsoft service unless the commercial SKU explicitly requires it.

## Submission gates

- [ ] Med Twin application source attached to this repository/product path.
- [ ] Production deployment architecture verified.
- [ ] Fulfillment URL configured.
- [ ] Product Code configured.
- [ ] ResolveCustomer E2E verified.
- [ ] GetEntitlements E2E verified.
- [ ] Tenant provisioning verified.
- [ ] Session lifecycle verified.
- [ ] Security/privacy documentation published.
- [ ] Healthcare data classification completed.
- [ ] Public pricing dimension defined.
- [ ] Marketplace screenshots/logo/video prepared.
- [ ] AWS Marketplace limited listing test completed.
