from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from aws_cdk import aws_wafv2 as wafv2


class AcaMarketplaceStack(Stack):
    """Production-oriented AWS Marketplace SaaS fulfillment plane.

    The application itself remains decoupled from Marketplace. This stack owns
    the customer registration/entitlement boundary, tenant persistence,
    private database, load balancer and security controls.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        product_code = self.node.try_get_context("marketplaceProductCode")
        image_tag = self.node.try_get_context("imageTag") or "latest"
        certificate_arn = self.node.try_get_context("certificateArn")

        if not product_code or product_code == "REPLACE_ME":
            raise ValueError("marketplaceProductCode is required")
        if not certificate_arn:
            raise ValueError(
                "certificateArn is required for the production HTTPS fulfillment endpoint"
            )

        vpc = ec2.Vpc(
            self,
            "AcaVpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        repository = ecr.Repository.from_repository_name(
            self,
            "FulfillmentRepository",
            "aca-marketplace-fulfillment",
        )

        db = rds.DatabaseInstance(
            self,
            "AcaPostgres",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_4
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            database_name="aca",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.SMALL,
            ),
            allocated_storage=20,
            max_allocated_storage=100,
            multi_az=True,
            publicly_accessible=False,
            deletion_protection=True,
            backup_retention=Duration.days(7),
            storage_encrypted=True,
            auto_minor_version_upgrade=True,
            removal_policy=RemovalPolicy.SNAPSHOT,
        )

        cluster = ecs.Cluster(
            self,
            "AcaCluster",
            vpc=vpc,
            container_insights=True,
        )

        log_group = logs.LogGroup(
            self,
            "FulfillmentLogs",
            retention=logs.RetentionDays.ONE_YEAR,
            removal_policy=RemovalPolicy.RETAIN,
        )

        task_role = iam.Role(
            self,
            "FulfillmentTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "aws-marketplace:ResolveCustomer",
                    "aws-marketplace:GetEntitlements",
                ],
                resources=["*"],
            )
        )
        db.secret.grant_read(task_role)

        task_definition = ecs.FargateTaskDefinition(
            self,
            "FulfillmentTask",
            cpu=512,
            memory_limit_mib=1024,
            task_role=task_role,
        )
        if task_definition.execution_role:
            db.secret.grant_read(task_definition.execution_role)

        container = task_definition.add_container(
            "Fulfillment",
            image=ecs.ContainerImage.from_ecr_repository(repository, image_tag),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="aca-fulfillment",
                log_group=log_group,
            ),
            environment={
                "AWS_REGION": self.region,
                "AWS_MARKETPLACE_PRODUCT_CODE": product_code,
                "DB_HOST": db.db_instance_endpoint_address,
                "DB_PORT": str(db.db_instance_endpoint_port),
                "DB_NAME": "aca",
                "MARKETPLACE_INTEGRATION_MODE": "saas-contract",
            },
            secrets={
                "DB_USERNAME": ecs.Secret.from_secrets_manager(
                    db.secret,
                    "username",
                ),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                    db.secret,
                    "password",
                ),
            },
        )
        container.add_port_mappings(container_port=8080)

        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FulfillmentService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=2,
            public_load_balancer=True,
            listener_port=443,
            certificate=ecs_patterns.ApplicationLoadBalancedTaskImageOptions.__annotations__.get(
                "certificate"
            ) if False else None,
            health_check_grace_period=Duration.seconds(90),
        )

        # Replace the pattern's HTTP listener with an HTTPS listener is not
        # supported by mutating the generated listener. The certificate is
        # therefore attached to the generated listener below.
        listener = service.listener
        listener.add_certificates(
            "MarketplaceCertificate",
            [__import__("aws_cdk.aws_elasticloadbalancingv2", fromlist=["ListenerCertificate"]).ListenerCertificate.from_arn(
                certificate_arn
            )],
        )

        db.connections.allow_default_port_from(service.service)

        service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
        )

        web_acl = wafv2.CfnWebACL(
            self,
            "FulfillmentWebAcl",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            scope="REGIONAL",
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="AcaMarketplaceWaf",
                sampled_requests_enabled=True,
            ),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedCommonRuleSet",
                    priority=1,
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(none={}),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name="AWSManagedRulesCommonRuleSet",
                            vendor_name="AWS",
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="AcaCommonRules",
                        sampled_requests_enabled=True,
                    ),
                )
            ],
        )

        wafv2.CfnWebACLAssociation(
            self,
            "FulfillmentWebAclAssociation",
            resource_arn=service.load_balancer.load_balancer_arn,
            web_acl_arn=web_acl.attr_arn,
        )

        CfnOutput(
            self,
            "FulfillmentRepositoryUri",
            value=repository.repository_uri,
        )
        CfnOutput(
            self,
            "FulfillmentLoadBalancerDns",
            value=service.load_balancer.load_balancer_dns_name,
        )
        CfnOutput(
            self,
            "PostgresSecretArn",
            value=db.secret.secret_arn,
        )
        CfnOutput(
            self,
            "MarketplaceProductCode",
            value=product_code,
        )
