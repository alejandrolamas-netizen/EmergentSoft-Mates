from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .repository import TenantRepository


class MarketplaceService:
    def __init__(self, marketplace_client: Any, entitlement_client: Any, product_code: str, repository: TenantRepository):
        self.marketplace = marketplace_client
        self.entitlement = entitlement_client
        self.product_code = product_code
        self.repository = repository

    def resolve_customer(self, registration_token: str) -> dict[str, Any]:
        return self.marketplace.resolve_customer(
            RegistrationToken=registration_token,
            ProductCode=self.product_code,
        )

    def get_entitlements(self, customer_identifier: str) -> list[dict[str, Any]]:
        result = self.entitlement.get_entitlements(
            ProductCode=self.product_code,
            Filter={"CUSTOMER_IDENTIFIER": [customer_identifier]},
        )
        return result.get("Entitlements", [])

    def provision(self, registration_token: str) -> dict[str, Any]:
        resolved = self.resolve_customer(registration_token)
        customer_identifier = resolved["CustomerIdentifier"]

        tenant = self.repository.upsert(
            customer_identifier=customer_identifier,
            product_code=resolved.get("ProductCode", self.product_code),
            marketplace_identifier=resolved.get("MarketplaceIdentifier"),
        )

        entitlements = self.get_entitlements(customer_identifier)

        return {
            "tenant": tenant,
            "entitlements": entitlements,
            "provisioned_at": datetime.now(timezone.utc),
        }
