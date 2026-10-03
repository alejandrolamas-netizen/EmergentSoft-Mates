from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass(frozen=True)
class TenantRecord:
    tenant_id: str
    customer_identifier: str
    product_code: str
    marketplace_identifier: str | None
    created_at: datetime


class TenantRepository:
    """Temporary repository boundary.

    The in-memory implementation makes idempotency testable without claiming
    that persistence is production-ready. Replace with PostgreSQL/DynamoDB
    behind the same interface before production deployment.
    """

    def __init__(self) -> None:
        self._records: dict[str, TenantRecord] = {}
        self._lock = Lock()

    def get_by_customer(self, customer_identifier: str) -> TenantRecord | None:
        with self._lock:
            return self._records.get(customer_identifier)

    def upsert(
        self,
        customer_identifier: str,
        product_code: str,
        marketplace_identifier: str | None,
    ) -> TenantRecord:
        with self._lock:
            existing = self._records.get(customer_identifier)
            if existing:
                return existing

            record = TenantRecord(
                tenant_id=f"awsmp-{customer_identifier}",
                customer_identifier=customer_identifier,
                product_code=product_code,
                marketplace_identifier=marketplace_identifier,
                created_at=datetime.now(timezone.utc),
            )
            self._records[customer_identifier] = record
            return record
