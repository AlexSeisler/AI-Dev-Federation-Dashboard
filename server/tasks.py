import asyncio
import threading
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from . import models, hf_client
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
                yield {"event": "log", "data": log.response}
                last_seen.add(log.id)

        if task.status in ["completed", "failed"]:
            yield {"event": "end", "data": f"Task {task_id} {task.status}."}
            return


def run_hf_task(task_id: int, preset: str, context: str):
    """
    Background runner for Hugging Face completions with memory + logging.
    """
    print(f"⚡ Runner started for task {task_id} (preset={preset})")
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            print(f"❌ Task {task_id} not found in DB")
            return

        task.status = "running"
        db.add(models.UserLog(task_id=task.id, response="🚀 Task started"))
        db.commit()

        # 🔎 Pull last 5 messages from memory for this user
        memory_entries = (
            db.query(models.Memory)
            .filter(models.Memory.user_id == task.user_id)
            .order_by(models.Memory.created_at.desc())
            .limit(5)
            .all()
        )
        memory = [{"role": m.role, "content": m.content} for m in reversed(memory_entries)]

        # Call Hugging Face with preset + context + memory
        try:
            db.add(models.UserLog(task_id=task.id, response="📡 Sending request to Hugging Face..."))
            db.commit()

            result = hf_client.run_completion(preset, context, memory)
            content = result["content"]

            db.add(models.UserLog(task_id=task.id, response=f"✅ HF Response: {content[:200]}..."))

            # Save response to memory for continuity
            db.add(
                models.Memory(
                    user_id=task.user_id,
                    role="assistant",
                    content=content,
                    created_at=datetime.utcnow(),
                )
            )

            task.status = "completed"

        except Exception as e:
            error_msg = f"❌ HF call failed: {str(e)}"
            print(error_msg)
            db.add(models.UserLog(task_id=task.id, response=error_msg))
            task.status = "failed"

        db.commit()
        print(f"🏁 Task {task.id} finished with status={task.status}")

    except Exception as outer_e:
        print(f"❌ Runner crashed: {outer_e}")
        db.add(models.UserLog(task_id=task_id, response=f"❌ Runner crashed: {outer_e}"))
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

    print(f"🚀 Created task {task.id}, launching runner thread...")
    threading.Thread(target=run_hf_task, args=(task.id, preset, context), daemon=True).start()

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
        "logs": responses,
    }
