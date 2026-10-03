# Agentic Compliance Accelerator — AWS Marketplace Readiness

## Target architecture

Commercial model: SaaS Contract.

Customer flow:
1. Buyer subscribes in AWS Marketplace.
2. AWS Marketplace POSTs x-amzn-marketplace-token to the fulfillment/registration URL.
3. ACA resolves the token server-side with ResolveCustomer.
4. ACA identifies the buyer with CustomerAWSAccountId and records LicenseArn.
5. ACA queries GetEntitlements using CUSTOMER_AWS_ACCOUNT_ID.
6. ACA provisions an isolated tenant record.
7. ACA creates a short-lived opaque application session.
8. The application verifies entitlements before granting paid features.
9. Entitlements are rechecked periodically and on sensitive access paths.

## Production infrastructure
- Amazon ECS/Fargate for fulfillment API.
- Amazon RDS PostgreSQL in isolated subnets.
- Application Load Balancer with HTTPS.
- AWS WAF managed common rule set.
- CloudWatch Logs with one-year retention.
- Secrets Manager-backed database credentials.
- ECR image scanning and immutable release tags.
- Multi-AZ RDS enabled.
- Deletion protection and encrypted storage.
- IAM roles instead of embedded credentials.
- GitHub Actions OIDC for deployment.

## Required deployment inputs
- AWS account used to publish the Marketplace SaaS product.
- AWS region.
- AWS Marketplace Product Code.
- ACM certificate ARN for the HTTPS fulfillment endpoint.
- Public DNS name mapped to the fulfillment endpoint.
- GitHub secret AWS_DEPLOY_ROLE_ARN.
- Marketplace registration/fulfillment URL.
- Terms of Use URL.
- Privacy Policy URL.
- Support URL/contact.
- Product logo, screenshots and product video.
- Final public pricing dimensions.

## Marketplace validation checklist
- [ ] Product has at least one public paid pricing dimension.
- [ ] Pricing dimensions describe software only.
- [ ] Application components are hosted in infrastructure controlled by EmergentSoft.
- [ ] Fulfillment URL accepts x-amzn-marketplace-token.
- [ ] ResolveCustomer succeeds from the publishing account.
- [ ] CustomerAWSAccountId is persisted.
- [ ] LicenseArn is persisted.
- [ ] GetEntitlements returns the subscribed dimension.
- [ ] Tenant is provisioned idempotently.
- [ ] Session is created only after successful provisioning.
- [ ] Expired/invalid sessions are rejected.
- [ ] Entitlements are rechecked after subscription changes.
- [ ] HTTPS certificate and DNS are valid.
- [ ] WAF is attached.
- [ ] CloudWatch logs are retained for at least one year.
- [ ] Backup/restore procedure is documented.
- [ ] Incident/security-contact process is published.
- [ ] Data collection, storage, usage, sharing, retention and deletion policy is published.

## Important boundary

EmergentSoft is the software provider. ACA assists with compliance readiness, evidence organization and workflow automation; it does not itself issue SOC 2, ISO or other third-party certifications/attestations.
