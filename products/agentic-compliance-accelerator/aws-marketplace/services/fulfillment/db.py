import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def build_database_url() -> str | None:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit

    host = os.getenv("DB_HOST")
    password = os.getenv("DB_PASSWORD")
    username = os.getenv("DB_USERNAME", "aca")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "aca")
    if not host or password is None:
        return None

    return (
        f"postgresql+psycopg://{quote_plus(username)}:{quote_plus(password)}"
        f"@{host}:{port}/{database}"
    )


DATABASE_URL = build_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine) if engine else None

SCHEMA = """
CREATE TABLE IF NOT EXISTS marketplace_tenants (
    tenant_id TEXT PRIMARY KEY,
    customer_identifier TEXT NOT NULL UNIQUE,
    product_code TEXT NOT NULL,
    marketplace_identifier TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS marketplace_sessions (
    session_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES marketplace_tenants(tenant_id),
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_marketplace_sessions_token_hash
ON marketplace_sessions(token_hash);
"""


def initialize_schema() -> None:
    if not engine:
        return
    with engine.begin() as connection:
        for statement in SCHEMA.strip().split(";"):
            statement = statement.strip()
            if statement:
                connection.execute(text(statement))
