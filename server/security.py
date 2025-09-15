import yaml
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from server.database import get_db
from server.models import AuditLog
from sqlalchemy.orm import Session

# --- Load Allowlist --- #
with open("config/endpoint_allowlist.yaml", "r") as f:
    ALLOWLIST = yaml.safe_load(f)

# --- Rate Limit (Guests) --- #
GUEST_LIMIT = 5  # tasks/hour

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce endpoint allowlist + rate limiting for guests.
    """

    async def dispatch(self, request: Request, call_next):
        db: Session = next(get_db())

        user = getattr(request.state, "user", None)  # populated by JWT middleware
        role = user["role"] if user else "guest"
        path = request.url.path
        method = request.method

        # --- Allowlist Enforcement --- #
        if path not in ALLOWLIST.get("endpoints", []):
            if role == "guest":
                raise HTTPException(status_code=403, detail="❌ Endpoint not permitted in Guest Mode")

        # --- Rate Limiting (Guests) --- #
        if role == "guest" and path.startswith("/tasks/run"):
            one_hour_ago = int(time.time()) - 3600
            task_count = db.query(AuditLog).filter(
                AuditLog.user_id == user["id"] if user else None,
                AuditLog.timestamp >= one_hour_ago,
                AuditLog.action.like("TASK_%")
            ).count()

            if task_count >= GUEST_LIMIT:
                raise HTTPException(status_code=429, detail="❌ Guest rate limit exceeded")

        # --- Audit Log --- #
        log = AuditLog(
            user_id=user["id"] if user else None,
            action=f"{method} {path}",
            timestamp=int(time.time())
        )
        db.add(log)
        db.commit()

        return await call_next(request)