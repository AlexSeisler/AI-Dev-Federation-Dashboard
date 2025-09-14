from fastapi import FastAPI

app = FastAPI(title="AI Dev Federation Dashboard Backend", version="0.1.0")


@app.get("/healthz")
def health_check():
    return {"status": "ok", "message": "Backend service is alive"}
