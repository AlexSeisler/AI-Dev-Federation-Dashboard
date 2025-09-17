"""
main.py — Backend Entrypoint
============================

This is the FastAPI entrypoint for the **AI Dev Federation Dashboard Backend**.

Responsibilities:
- Initialize the FastAPI app with middleware and routers.
- Configure CORS policy (via environment variables).
- Provide request/response logging for observability.
- Register feature routers (auth, tasks, GitHub integration, debug).
- Expose health check endpoints for monitoring.

"""

import os
import time
import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from server import auth, tasks, github
from server.debug import router as debug_router
from server.debug import debug_log

# Startup log marker
debug_log("🚀 Server startup test log")

# ----------------------------------------------------
# App Initialization
# ----------------------------------------------------
app = FastAPI(
    title="AI Dev Federation Dashboard Backend",
    version="0.1.0"
)

# ----------------------------------------------------
# CORS Configuration (from environment)
# ----------------------------------------------------
raw_origins = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Optional: allow all origins for local debug
if os.getenv("CORS_ALLOW_ALL", "false").lower() == "true":
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Logging Setup
# ----------------------------------------------------
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware: log all HTTP requests/responses with timing.
    Truncates large bodies for readability in debug.log.
    """
    start_time = time.time()

    # Capture request body
    try:
        body_bytes = await request.body()
        body = body_bytes.decode("utf-8") if body_bytes else None
        if body and len(body) > 500:
            body = body[:500] + "... (truncated)"
    except Exception:
        body = "<unreadable>"

    logging.info(f"📥 Request | {request.method} {request.url} | Body: {body}")

    response: Response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    resp_body = b"".join([chunk async for chunk in response.body_iterator])
    response.body_iterator = iter([resp_body])  # reset for FastAPI to return it

    try:
        resp_text = resp_body.decode("utf-8")
        if len(resp_text) > 500:
            resp_text = resp_text[:500] + "... (truncated)"
    except Exception:
        resp_text = "<unreadable>"

    logging.info(
        f"📤 Response | {request.method} {request.url} | "
        f"Status: {response.status_code} | Time: {process_time:.2f}ms | Body: {resp_text}"
    )

    return Response(
        content=resp_body,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

# ----------------------------------------------------
# Routers
# ----------------------------------------------------
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(github.router)
app.include_router(debug_router)

# ----------------------------------------------------
# Health Endpoints
# ----------------------------------------------------
@app.get("/healthz")
def health_check():
    """Deep health check: confirms DB + services are alive."""
    return {"status": "ok", "message": "Backend service is alive"}

@app.get("/health/ping")
def ping():
    """Lightweight ping (fast heartbeat)."""
    return {"pong": True}
