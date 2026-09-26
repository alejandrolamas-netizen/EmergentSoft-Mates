import os
from datetime import datetime, timezone

import boto3
from fastapi import Depends, FastAPI, HTTPException

from .db import initialize_schema
from .models import ProvisionRequest, ProvisionResponse, SubscriptionStatus
from .persistence import PostgresTenantRepository
from .repository import TenantRepository
from .service import MarketplaceService
from .session import require_marketplace_session

app = FastAPI(title="Agentic Compliance Accelerator - Marketplace Fulfillment", version="0.3.0")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
PRODUCT_CODE = os.getenv("AWS_MARKETPLACE_PRODUCT_CODE")

marketplace = boto3.client("marketplacecommerceanalytics", region_name=AWS_REGION)
entitlement = boto3.client("marketplace-entitlement", region_name=AWS_REGION)

memory_repository = TenantRepository()
postgres_repository = PostgresTenantRepository()
service = MarketplaceService(marketplace, entitlement, PRODUCT_CODE or "", memory_repository)


@app.on_event("startup")
def startup() -> None:
    initialize_schema()


@app.get("/health")
def health():
    return {"status": "ok", "service": "aca-marketplace-fulfillment"}


@app.post("/marketplace/provision", response_model=ProvisionResponse)
def provision(request: ProvisionRequest):
    if not PRODUCT_CODE:
        raise HTTPException(status_code=500, detail="AWS_MARKETPLACE_PRODUCT_CODE is not configured")
    try:
        result = service.provision(request.registration_token)
        tenant = result["tenant"]
        if os.getenv("DATABASE_URL"):
            persisted = postgres_repository.upsert(
                tenant.customer_identifier,
                tenant.product_code,
                tenant.marketplace_identifier,
            )
        token, expires_at = postgres_repository.create_session(tenant.tenant_id) if os.getenv("DATABASE_URL") else ("", None)
        payload = ProvisionResponse(**result)
        payload.session_token = token
        payload.session_expires_at = expires_at
        return payload
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AWS Marketplace provisioning failed") from exc


@app.get("/marketplace/me")
def me(session=Depends(require_marketplace_session)):
    return session


@app.get("/marketplace/tenants/{customer_identifier}")
def tenant(customer_identifier: str, session=Depends(require_marketplace_session)):
    if session["customer_identifier"] != customer_identifier:
        raise HTTPException(status_code=403, detail="Tenant access denied")
    record = postgres_repository.get_by_customer(customer_identifier)
    if not record:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return record


@app.get("/marketplace/subscription", response_model=SubscriptionStatus)
def subscription(session=Depends(require_marketplace_session)):
    customer_identifier = session["customer_identifier"]
    entitlements = service.get_entitlements(customer_identifier)
    now = datetime.now(timezone.utc)
    active = [e for e in entitlements if e.get("ExpirationDate") is None or e.get("ExpirationDate") > now]
    if not active:
        return SubscriptionStatus(
            tenant_id=session["tenant_id"],
            customer_identifier=customer_identifier,
            plan="none",
            status="inactive",
        )
    current = active[0]
    return SubscriptionStatus(
        tenant_id=session["tenant_id"],
        customer_identifier=customer_identifier,
        plan=current.get("Dimension", "unknown"),
        status="active",
        expiration=current.get("ExpirationDate"),
    )
