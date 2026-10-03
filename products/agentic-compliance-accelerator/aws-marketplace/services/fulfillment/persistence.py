from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from .db import SessionLocal


class PostgresTenantRepository:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def upsert(self, customer_identifier: str, product_code: str, marketplace_identifier: str | None):
        if not self.session_factory:
            raise RuntimeError("DATABASE_URL is required for PostgreSQL persistence")
        tenant_id = f"awsmp-{customer_identifier}"
        with self.session_factory() as session:
            session.execute(text("""
                INSERT INTO marketplace_tenants
                (tenant_id, customer_identifier, product_code, marketplace_identifier)
                VALUES (:tenant_id, :customer_identifier, :product_code, :marketplace_identifier)
                ON CONFLICT (customer_identifier) DO UPDATE SET
                    product_code = EXCLUDED.product_code,
                    marketplace_identifier = EXCLUDED.marketplace_identifier,
                    updated_at = NOW()
            """), {
                "tenant_id": tenant_id,
                "customer_identifier": customer_identifier,
                "product_code": product_code,
                "marketplace_identifier": marketplace_identifier,
            })
            session.commit()
            return self.get_by_customer(customer_identifier)

    def get_by_customer(self, customer_identifier: str):
        if not self.session_factory:
            raise RuntimeError("DATABASE_URL is required for PostgreSQL persistence")
        with self.session_factory() as session:
            row = session.execute(text("""
                SELECT tenant_id, customer_identifier, product_code,
                       marketplace_identifier, created_at
                FROM marketplace_tenants
                WHERE customer_identifier = :customer_identifier
            """), {"customer_identifier": customer_identifier}).mappings().first()
            return dict(row) if row else None

    def create_session(self, tenant_id: str, ttl_minutes: int = 60):
        if not self.session_factory:
            raise RuntimeError("DATABASE_URL is required for PostgreSQL persistence")
        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        session_id = secrets.token_urlsafe(24)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        with self.session_factory() as session:
            session.execute(text("""
                INSERT INTO marketplace_sessions
                (session_id, tenant_id, token_hash, expires_at)
                VALUES (:session_id, :tenant_id, :token_hash, :expires_at)
            """), {
                "session_id": session_id,
                "tenant_id": tenant_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
            })
            session.commit()
        return raw_token, expires_at

    def resolve_session(self, raw_token: str):
        if not self.session_factory:
            raise RuntimeError("DATABASE_URL is required for PostgreSQL persistence")
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        with self.session_factory() as session:
            row = session.execute(text("""
                SELECT s.session_id, s.tenant_id, s.expires_at,
                       t.customer_identifier, t.product_code
                FROM marketplace_sessions s
                JOIN marketplace_tenants t ON t.tenant_id = s.tenant_id
                WHERE s.token_hash = :token_hash AND s.expires_at > NOW()
            """), {"token_hash": token_hash}).mappings().first()
            return dict(row) if row else None
