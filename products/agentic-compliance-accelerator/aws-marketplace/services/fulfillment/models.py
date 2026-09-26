from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MarketplaceCustomer(BaseModel):
    customer_identifier: str
    product_code: str
    marketplace_identifier: str | None = None
    tenant_id: str


class ProvisionRequest(BaseModel):
    registration_token: str = Field(min_length=1)


class ProvisionResponse(BaseModel):
    tenant: MarketplaceCustomer
    entitlements: list[dict[str, Any]]
    provisioned_at: datetime
    session_token: str | None = None
    session_expires_at: datetime | None = None


class SubscriptionStatus(BaseModel):
    tenant_id: str
    customer_identifier: str
    plan: str
    status: str
    expiration: datetime | None = None
