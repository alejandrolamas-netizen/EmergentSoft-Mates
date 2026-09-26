import os
from datetime import datetime, timezone

import boto3
from fastapi import FastAPI, HTTPException

from .models import ProvisionRequest, ProvisionResponse, SubscriptionStatus
from .repository import TenantRepository
from .service import MarketplaceService

app = FastAPI(title="Agentic Compliance Accelerator - Marketplace Fulfillment", version="0.2.0")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
PRODUCT_CODE = os.getenv("AWS_MARKETPLACE_PRODUCT_CODE")

marketplace = boto3.client("marketplacecommerceanalytics", region_name=AWS_REGION)
entitlement = boto3.client("marketplace-entitlement", region_name=AWS_REGION)
repository = TenantRepository()

service = MarketplaceService(
    marketplace_client=marketplace,
    entitlement_client=entitlement,
    product_code=PRODUCT_CODE or "",
    repository=repository,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aca-marketplace-fulfillment"}


@app.post("/marketplace/provision", response_model=ProvisionResponse)
def provision(request: ProvisionRequest) -> ProvisionResponse:
    if not PRODUCT_CODE:
        raise HTTPException(status_code=500, detail="AWS_MARKETPLACE_PRODUCT_CODE is not configured")
    try:
        result = service.provision(request.registration_token)
        return ProvisionResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AWS Marketplace provisioning failed") from exc


@app.get("/marketplace/tenants/{customer_identifier}")
def tenant(customer_identifier: str):
    record = repository.get_by_customer(customer_identifier)
    if record is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return record


@app.get("/marketplace/entitlements")
def get_entitlements(customer_id: str):
    if not PRODUCT_CODE:
        raise HTTPException(status_code=500, detail="AWS_MARKETPLACE_PRODUCT_CODE is not configured")
    try:
        return {"entitlements": service.get_entitlements(customer_id)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AWS Marketplace entitlement lookup failed") from exc


@app.get("/marketplace/subscription/{customer_identifier}", response_model=SubscriptionStatus)
def subscription(customer_identifier: str) -> SubscriptionStatus:
    record = repository.get_by_customer(customer_identifier)
    if record is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    entitlements = service.get_entitlements(customer_identifier)
    now = datetime.now(timezone.utc)
    active = [
        e for e in entitlements
        if e.get("ExpirationDate") is None or e.get("ExpirationDate") > now
    ]

    if not active:
        return SubscriptionStatus(
            tenant_id=record.tenant_id,
            customer_identifier=customer_identifier,
            plan="none",
            status="inactive",
        )

    dimension = active[0].get("Dimension", "unknown")
    return SubscriptionStatus(
        tenant_id=record.tenant_id,
        customer_identifier=customer_identifier,
        plan=dimension,
        status="active",
        expiration=active[0].get("ExpirationDate"),
    )
