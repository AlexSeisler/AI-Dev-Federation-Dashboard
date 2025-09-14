from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import os
import asyncio
import json

from . import models, database, auth

router = APIRouter(prefix="/tasks", tags=["tasks"])

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODELS = [
    "microsoft/phi-3-mini-4k-instruct",
    "mistralai/Mistral-7B-Instruct-v0.2"
]

# Utility: DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility: SSE event generator
async def event_generator(task_id: int, db: Session):
    while True:
        logs = db.query(models.Log).filter(models.Log.task_id == task_id).order_by(models.Log.timestamp).all()
        for log in logs:
            yield f"data: {log.message}\n\n"
        await asyncio.sleep(1)

@router.post("/run/{preset}")
def run_task(preset: str, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    if preset not in ["structure", "file", "brainstorm"]:
        raise HTTPException(status_code=400, detail="Invalid preset")

    # Create task
    task = models.Task(
        user_id=user.id,
        type=preset,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Insert initial log
    log = models.Log(task_id=task.id, message=f"Task {preset} started")
    db.add(log)
    db.commit()

    # TODO: Background execution of Hugging Face call

    return {"task_id": task.id, "status": task.status}

@router.get("/{task_id}/stream")
async def stream_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return StreamingResponse(event_generator(task_id, db), media_type="text/event-stream")

@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    logs = db.query(models.Log).filter(models.Log.task_id == task.id).order_by(models.Log.timestamp).all()
    user_logs = db.query(models.UserLog).filter(models.UserLog.task_id == task.id).order_by(models.UserLog.timestamp).all()

    return {
        "id": task.id,
        "type": task.type,
        "status": task.status,
        "created_at": task.created_at,
        "logs": [l.message for l in logs],
        "responses": [ul.response for ul in user_logs]
    }