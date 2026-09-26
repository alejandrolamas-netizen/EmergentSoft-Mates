#!/usr/bin/env python3
import aws_cdk as cdk
from aca_marketplace_stack import AcaMarketplaceStack

app = cdk.App()
AcaMarketplaceStack(
    app,
    "AcaMarketplaceStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1",
    ),
)
app.synth()
