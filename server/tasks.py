import asyncio
import threading
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from . import models
from .database import get_db, SessionLocal

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def event_generator(task_id: int, db: Session):
    last_seen = set()
    while True:
        await asyncio.sleep(1)
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            yield {"event": "error", "data": f"❌ Task {task_id} not found."}
            return

        logs = db.query(models.UserLog).filter(models.UserLog.task_id == task_id).all()
        for log in logs:
            if log.id not in last_seen:
                yield {"event": "log", "data": log.message}
                last_seen.add(log.id)

        if task.status in ["completed", "failed"]:
            yield {"event": "end", "data": f"Task {task_id} {task.status}."}
            return


def run_hf_task(task_id: int):
    """
    DEBUG MODE: no Hugging Face call, just DB logging.
    """
    print(f"⚡ Threaded runner started for task {task_id}")
    db = SessionLocal()
    try:
        # First log
        db.add(models.UserLog(task_id=task_id, message="🔥 Runner reached DB"))
        db.commit()

        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            print(f"❌ Task {task_id} not found in DB")
            return

        # Pretend we did work
        task.status = "completed"
        db.add(models.UserLog(task_id=task_id, message="✅ Fake completion"))
        db.commit()
        print(f"✅ Task {task_id} marked completed")

    except Exception as e:
        print(f"❌ Exception in run_hf_task: {e}")
        db.add(models.UserLog(task_id=task_id, message=f"❌ Error: {str(e)}"))
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task:
            task.status = "failed"
        db.commit()
    finally:
        db.close()


@router.post("/run/{preset}")
async def run_task(
    preset: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    print("🚀 run_task endpoint hit")  # confirm request enters

    if preset not in ["structure", "file", "brainstorm"]:
        raise HTTPException(status_code=400, detail=f"❌ Invalid preset: {preset}")

    user_id = payload.get("user_id")
    context = payload.get("context", "")

    if not user_id:
        raise HTTPException(status_code=400, detail="❌ Missing user_id.")

    task = models.Task(user_id=user_id, type=preset, context=context, status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)

    print(f"🚀 Created task {task.id}, launching thread...")

    def runner_debug():
        print(f"⚡ Inside runner_debug for task {task.id}")
        db2 = SessionLocal()
        db2.add(models.UserLog(task_id=task.id, message="🔥 Runner_debug fired"))
        db2.commit()
        task_in_db = db2.query(models.Task).filter(models.Task.id == task.id).first()
        if task_in_db:
            task_in_db.status = "completed"
        db2.commit()
        db2.close()
        print(f"✅ Runner_debug finished for task {task.id}")

    threading.Thread(target=runner_debug, daemon=True).start()

    return {"task_id": task.id, "status": task.status}



@router.get("/{task_id}/stream")
async def stream_task(task_id: int, db: Session = Depends(get_db)):
    return EventSourceResponse(event_generator(task_id, db))


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="❌ Task not found.")

    logs = db.query(models.UserLog).filter(models.UserLog.task_id == task_id).all()
    responses = [log.response for log in logs if log.response]

    return {
        "id": task.id,
        "type": task.type,
        "status": task.status,
        "logs": [log.message for log in logs],
        "responses": responses,
    }
