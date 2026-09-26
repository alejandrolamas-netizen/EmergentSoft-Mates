from fastapi import Header, HTTPException
from .persistence import PostgresTenantRepository

def require_marketplace_session(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Marketplace session required")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Marketplace session required")
    record = PostgresTenantRepository().resolve_session(token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return record
