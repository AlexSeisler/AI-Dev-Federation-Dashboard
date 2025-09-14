from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server import auth

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

# Routers
app.include_router(auth.router)

@app.get("/healthz")
def health_check():
    return {"status": "ok", "message": "Backend service is alive"}
