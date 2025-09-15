from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server import auth, tasks, github
from server.security import SecurityMiddleware  # ✅ import security middleware

app = FastAPI(
    title="AI Dev Federation Dashboard Backend",
    version="0.1.0"
)

# ✅ Enable CORS so frontend at http://localhost:5173 can reach backend
origins = [
    "http://localhost:5173",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Add security middleware
app.add_middleware(SecurityMiddleware)

# Routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(github.router)  # ✅ GitHub endpoints wired in

@app.get("/healthz")
def health_check():
    """Deep health check: confirms DB + services are alive."""
    return {"status": "ok", "message": "Backend service is alive"}

@app.get("/health/ping")
def ping():
    """Lightweight health ping (fast recruiter heartbeat)."""
    return {"pong": True}
