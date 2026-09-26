from datetime import datetime, timezone

from services.fulfillment.repository import TenantRepository
from services.fulfillment.service import MarketplaceService


class MarketplaceStub:
    def __init__(self):
        self.calls = 0

    def resolve_customer(self, **kwargs):
        self.calls += 1
        return {
            "CustomerIdentifier": "customer-123",
            "ProductCode": "prod-aca",
            "MarketplaceIdentifier": "aws-marketplace",
        }


class EntitlementStub:
    def get_entitlements(self, **kwargs):
        return {
            "Entitlements": [
                {
                    "Dimension": "professional",
                    "ExpirationDate": datetime.now(timezone.utc),
                }
            ]
        }


def test_provisioning_is_idempotent():
    repo = TenantRepository()
    marketplace = MarketplaceStub()
    service = MarketplaceService(marketplace, EntitlementStub(), "prod-aca", repo)

    first = service.provision("token")
    second = service.provision("token")

    assert first["tenant"].tenant_id == second["tenant"].tenant_id
    assert marketplace.calls == 2
    assert repo.get_by_customer("customer-123") is not None


def test_unknown_customer_has_no_tenant():
    repo = TenantRepository()
    assert repo.get_by_customer("missing") is None
