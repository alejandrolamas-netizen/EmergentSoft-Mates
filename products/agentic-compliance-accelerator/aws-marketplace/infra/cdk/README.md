# ACA AWS infrastructure

CDK baseline for:

- VPC across two AZs
- ECR repository
- ECS/Fargate service
- Application Load Balancer
- private PostgreSQL RDS
- Secrets Manager-backed database credentials
- CloudWatch logs
- IAM task role

## Important deployment gate

The stack intentionally requires the actual AWS Marketplace product code before production use.

The current CDK baseline does not claim HTTPS, custom DNS, Marketplace registration, or production deployment. For production, add an ACM certificate and HTTPS listener, Route 53 record, WAF if required, alarms, autoscaling policy, and the real Marketplace product code.

The container image must exist in ECR under tag `latest` before the ECS service can become healthy.

## Deploy

From this directory after installing AWS CDK and authenticating to the target AWS account:

```bash
python -m pip install -r requirements.txt
cdk bootstrap
cdk deploy -c marketplaceProductCode=<REAL_PRODUCT_CODE>
```

Never commit AWS credentials or production secrets.
