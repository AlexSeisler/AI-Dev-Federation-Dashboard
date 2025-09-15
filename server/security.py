import yaml
import os
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from server.database import get_db
from server.models import AuditLog
from sqlalchemy.orm import Session

# --- Load Allowlist --- #
ALLOWLIST_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "endpoint_allowlist.yaml")
with open(ALLOWLIST_PATH, "r") as f:
    ALLOWLIST = yaml.safe_load(f)

# --- Rate Limit (Guests) --- #
GUEST_LIMIT = 5  # tasks/minute


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
        # Always allow authentication endpoints
        if path.startswith("/auth/"):
            return await call_next(request)

        if path not in ALLOWLIST.get("endpoints", []):
            if role == "guest":
                raise HTTPException(status_code=403, detail="❌ Endpoint not permitted in Guest Mode")

        # --- Rate Limiting (Guests) --- #
        if role == "guest" and path.startswith("/tasks/run"):
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)

            task_count = (
                db.query(AuditLog)
                .filter(
                    AuditLog.user_id.is_(None),  # ✅ guests log with NULL user_id
                    AuditLog.timestamp >= one_minute_ago,
                    AuditLog.action.like("TASK_%"),
                )
                .count()
            )

            if task_count >= GUEST_LIMIT:
                raise HTTPException(status_code=429, detail="❌ Guest rate limit exceeded (5 tasks/min)")

        # --- Audit Log --- #
        log = AuditLog(
            user_id=user["id"] if user else None,  # ✅ fallback for guests
            action=f"{method} {path}",
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()

        return await call_next(request)
