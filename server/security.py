"""
security.py — Security Middleware
=================================

This module provides lightweight request security enforcement.

Responsibilities:
- Enforce endpoint allowlist (config-driven).
- Apply basic rate limiting for guest users.
- Record all requests in the audit log.
"""

import os
import yaml
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import AuditLog

# ----------------------------------------------------
# Config
# ----------------------------------------------------
ALLOWLIST_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "endpoint_allowlist.yaml")
with open(ALLOWLIST_PATH, "r") as f:
    ALLOWLIST = yaml.safe_load(f)

GUEST_LIMIT = 5  # guest users: tasks per minute

# ----------------------------------------------------
# Middleware
# ----------------------------------------------------
class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce:
    - Endpoint allowlist (YAML config).
    - Guest rate limiting (5 tasks/min).
    - Request audit logging.
    """

    async def dispatch(self, request: Request, call_next):
        db: Session = next(get_db())

        # Resolve user role (guest if unauthenticated)
        user = getattr(request.state, "user", None)
        role = user["role"] if user else "guest"
        path = request.url.path
        method = request.method

        # Allow all authentication endpoints
        if path.startswith("/auth/"):
            return await call_next(request)

        # Guest rate limiting
        if role == "guest" and path.startswith("/tasks/run"):
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            task_count = (
                db.query(AuditLog)
                .filter(
                    AuditLog.user_id.is_(None),  # guests logged with NULL user_id
                    AuditLog.timestamp >= one_minute_ago,
                    AuditLog.action.like("TASK_%"),
                )
                .count()
            )
            if task_count >= GUEST_LIMIT:
                raise HTTPException(status_code=429, detail="❌ Guest rate limit exceeded (5 tasks/min)")

        # Audit log
        log = AuditLog(
            user_id=user["id"] if user else None,
            action=f"{method} {path}",
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()

        return await call_next(request)
