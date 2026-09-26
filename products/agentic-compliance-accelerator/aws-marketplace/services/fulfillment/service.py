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
        # ResolveCustomer exchanges the registration token for the product and
        # customer identity returned by AWS Marketplace.
        return self.marketplace.resolve_customer(RegistrationToken=registration_token)

    def get_entitlements(self, customer_identifier: str) -> list[dict[str, Any]]:
        result = self.entitlement.get_entitlements(
            ProductCode=self.product_code,
            Filter={"CUSTOMER_AWS_ACCOUNT_ID": [customer_identifier]},
        )
        return result.get("Entitlements", [])

    def provision(self, registration_token: str) -> dict[str, Any]:
        resolved = self.resolve_customer(registration_token)

        # New SaaS integrations should use CustomerAWSAccountId and LicenseArn.
        # CustomerIdentifier is retained only as a legacy fallback.
        customer_identifier = (
            resolved.get("CustomerAWSAccountId")
            or resolved.get("CustomerIdentifier")
        )
        if not customer_identifier:
            raise ValueError("AWS Marketplace did not return a customer identity")

        product_code = resolved.get("ProductCode") or self.product_code
        marketplace_identifier = resolved.get("LicenseArn")

        tenant = self.repository.upsert(
            customer_identifier=customer_identifier,
            product_code=product_code,
            marketplace_identifier=marketplace_identifier,
        )

        entitlements = self.get_entitlements(customer_identifier)

        return {
            "tenant": tenant,
            "entitlements": entitlements,
            "provisioned_at": datetime.now(timezone.utc),
        }
