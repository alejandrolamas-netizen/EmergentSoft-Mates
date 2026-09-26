import os
from typing import Any

import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Agentic Compliance Accelerator - Marketplace Fulfillment", version="0.1.0")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
PRODUCT_CODE = os.getenv("AWS_MARKETPLACE_PRODUCT_CODE")

marketplace = boto3.client("marketplacecommerceanalytics", region_name=AWS_REGION)
entitlement = boto3.client("marketplace-entitlement", region_name=AWS_REGION)


class ResolveCustomerRequest(BaseModel):
    x_amzn_marketplace_token: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aca-marketplace-fulfillment"}


@app.post("/marketplace/resolve-customer")
def resolve_customer(request: ResolveCustomerRequest) -> dict[str, Any]:
    if not PRODUCT_CODE:
        raise HTTPException(status_code=500, detail="AWS_MARKETPLACE_PRODUCT_CODE is not configured")

    try:
        result = marketplace.resolve_customer(
            RegistrationToken=request.x_amzn_marketplace_token,
            ProductCode=PRODUCT_CODE,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AWS Marketplace customer resolution failed") from exc

    return {
        "customerIdentifier": result.get("CustomerIdentifier"),
        "productCode": result.get("ProductCode"),
        "marketplaceIdentifier": result.get("MarketplaceIdentifier"),
    }


@app.get("/marketplace/entitlements")
def get_entitlements(customer_id: str) -> dict[str, Any]:
    if not PRODUCT_CODE:
        raise HTTPException(status_code=500, detail="AWS_MARKETPLACE_PRODUCT_CODE is not configured")

    try:
        result = entitlement.get_entitlements(
            ProductCode=PRODUCT_CODE,
            Filter={"CUSTOMER_IDENTIFIER": [customer_id]},
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AWS Marketplace entitlement lookup failed") from exc

    return {
        "entitlements": result.get("Entitlements", []),
        "nextToken": result.get("NextToken"),
    }
