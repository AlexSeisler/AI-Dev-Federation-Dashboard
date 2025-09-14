from fastapi import FastAPI
from server import auth

app = FastAPI(title="AI Dev Federation Dashboard Backend", version="0.1.0")

# Routers
app.include_router(auth.router)

@app.get("/healthz")
def health_check():
    return {"status": "ok", "message": "Backend service is alive"}
