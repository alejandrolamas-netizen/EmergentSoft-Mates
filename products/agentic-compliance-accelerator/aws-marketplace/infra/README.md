# AWS Marketplace infrastructure

This directory is reserved for the deployment definition of the ACA Marketplace SaaS path.

Recommended production topology:

- HTTPS ingress / API Gateway or ALB
- ACA web application
- Fulfillment service
- Private application networking
- Managed PostgreSQL
- Redis where required by the application
- Secrets Manager / Parameter Store
- CloudWatch logs, metrics and alarms
- IAM roles with least privilege

Do not claim a service is deployed until the corresponding AWS account resources have been provisioned and validated.

The first implementation milestone is the fulfillment service. Infrastructure-as-code should be added after the target AWS runtime (ECS/Fargate, EKS, or another supported architecture) is selected.
