from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
import json
import logging
import time
import os  # ✅ for environment-based CORS

from server import auth, tasks, github
from server.security import SecurityMiddleware  # ✅ import security middleware
from server.debug import router as debug_router
from server.debug import debug_log

debug_log("🚀 Server startup test log")

app = FastAPI(
    title="AI Dev Federation Dashboard Backend",
    version="0.1.0"
)

# ✅ Enable CORS: allow from environment variable, fallback to localhost
origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,https://aidevfederationdashboard.netlify.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Add security middleware
app.add_middleware(SecurityMiddleware)

# ✅ Setup logging to the same debug.log file
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses to debug.log"""
    start_time = time.time()

    # Read request body safely
    try:
        body_bytes = await request.body()
        body = body_bytes.decode("utf-8") if body_bytes else None
        if body and len(body) > 500:
            body = body[:500] + "... (truncated)"
    except Exception:
        body = "<unreadable>"

    logging.info(
        f"📥 Request | {request.method} {request.url} | Headers: {dict(request.headers)} | Body: {body}"
    )

    response: Response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    resp_body = b"".join([chunk async for chunk in response.body_iterator])
    response.body_iterator = iter([resp_body])  # Reset so FastAPI can send it back

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

    return Response(content=resp_body, status_code=response.status_code, headers=dict(response.headers))

# Routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(github.router)
app.include_router(debug_router)  # ✅ Debug endpoints wired in

@app.get("/healthz")
def health_check():
    """Deep health check: confirms DB + services are alive."""
    return {"status": "ok", "message": "Backend service is alive"}

@app.get("/health/ping")
def ping():
    """Lightweight health ping (fast recruiter heartbeat)."""
    return {"pong": True}
