from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
)
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager


class AcaMarketplaceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "AcaVpc",
            max_azs=2,
            nat_gateways=1,
        )

        repository = ecr.Repository(
            self,
            "FulfillmentRepository",
            repository_name="aca-marketplace-fulfillment",
            image_scan_on_push=True,
            lifecycle_rules=[ecr.LifecycleRule(max_image_count=10)],
            removal_policy=RemovalPolicy.RETAIN,
        )

        db = rds.DatabaseInstance(
            self,
            "AcaPostgres",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_4
            ),
            vpc=vpc,
            database_name="aca",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.SMALL,
            ),
            allocated_storage=20,
            max_allocated_storage=100,
            multi_az=False,
            publicly_accessible=False,
            deletion_protection=True,
            backup_retention=Duration.days(7),
            storage_encrypted=True,
            removal_policy=RemovalPolicy.SNAPSHOT,
        )

        cluster = ecs.Cluster(self, "AcaCluster", vpc=vpc, container_insights=True)
        log_group = logs.LogGroup(
            self,
            "FulfillmentLogs",
            retention=logs.RetentionDays.ONE_MONTH,
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
        container = task_definition.add_container(
            "Fulfillment",
            image=ecs.ContainerImage.from_ecr_repository(repository, "latest"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="aca-fulfillment",
                log_group=log_group,
            ),
            environment={
                "AWS_REGION": self.region,
                "AWS_MARKETPLACE_PRODUCT_CODE": self.node.try_get_context(
                    "marketplaceProductCode"
                ) or "REPLACE_ME",
                "DB_HOST": db.db_instance_endpoint_address,
                "DB_PORT": str(db.db_instance_endpoint_port),
                "DB_NAME": "aca",
            },
            secrets={
                "DB_USERNAME": ecs.Secret.from_secrets_manager(db.secret, "username"),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(db.secret, "password"),
            },
            },
        )
        container.add_port_mappings(container_port=8080)

        db.secret.grant_read(task_definition.task_role)

        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FulfillmentService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=2,
            public_load_balancer=True,
            listener_port=80,
            health_check_grace_period=Duration.seconds(90),
        )

        db.connections.allow_default_port_from(service.service.connections.security_groups[0])

        service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
        )

        CfnOutput(self, "FulfillmentRepositoryUri", value=repository.repository_uri)
        CfnOutput(self, "FulfillmentLoadBalancerDns", value=service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "PostgresSecretArn", value=db.secret.secret_arn)
