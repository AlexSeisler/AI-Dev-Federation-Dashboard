from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import traceback

from . import models, database, auth, hf_client

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Utility: DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SSE event generator
async def event_generator(task_id: int, db: Session):
    last_count = 0
    while True:
        logs = db.query(models.Log).filter(models.Log.task_id == task_id).order_by(models.Log.timestamp).all()
        if len(logs) > last_count:
            new_logs = logs[last_count:]
            for log in new_logs:
                yield f"data: {log.message}\n\n"
            last_count = len(logs)
        await asyncio.sleep(1)


def run_hf_task(task: models.Task, db_session_factory):
    """Run Hugging Face task in background using a fresh DB session"""
    db = db_session_factory()
    try:
        # Step 1: Update status → running
        task.status = "running"
        db.merge(task)
        db.commit()

        # Step 2: Add log
        log = models.Log(task_id=task.id, message=f"Running preset: {task.type}")
        db.add(log)
        db.commit()

        # Step 3: Pull memory for context
        memory_entries = (
            db.query(models.Memory)
            .filter(models.Memory.user_id == task.user_id)
            .order_by(models.Memory.queue_num.desc())
            .limit(5)
            .all()
        )
        memory_context = [
            {"role": "user", "content": m.data.get("content", "")} for m in memory_entries
        ]

        # Step 4: Call Hugging Face
        try:
            log = models.Log(task_id=task.id, message="Calling Hugging Face API...")
            db.add(log)
            db.commit()

            response = hf_client.run_completion(task.type, context="", memory=memory_context)

            log = models.Log(
                task_id=task.id,
                message=f"Hugging Face responded: {str(response)[:200]}..."
            )
            db.add(log)
            db.commit()

        except Exception as e:
            error_msg = f"Hugging Face call failed: {str(e)}"
            log = models.Log(task_id=task.id, message=error_msg)
            db.add(log)
            db.commit()
            raise

        # Step 5: Save response to UserLog
        user_log = models.UserLog(
            task_id=task.id,
            response=response,
            timestamp=datetime.utcnow(),
        )
        db.add(user_log)

        # Step 6: Add to Memory
        new_memory = models.Memory(
            user_id=task.user_id,
            data={"role": "assistant", "content": response},
            queue_num=(memory_entries[0].queue_num + 1 if memory_entries else 1),
        )
        db.add(new_memory)

        # Step 7: Update status → completed
        task.status = "completed"
        db.merge(task)

        # Final log
        log = models.Log(task_id=task.id, message="Task completed successfully")
        db.add(log)

        db.commit()

    except Exception as e:
        task.status = "failed"
        db.merge(task)
        db.commit()

        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        log = models.Log(task_id=task.id, message=error_msg)
        db.add(log)
        db.commit()

        print("❌ Task failed:", error_msg)

    finally:
        db.close()



@router.post("/run/{preset}")
def run_task(
    preset: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    if preset not in ["structure", "file", "brainstorm"]:
        raise HTTPException(status_code=400, detail="Invalid preset")

    # Create task
    task = models.Task(
        user_id=user.id,
        type=preset,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Insert initial log
    log = models.Log(task_id=task.id, message=f"Task {preset} created")
    db.add(log)
    db.commit()

    # ✅ Schedule background Hugging Face call with fresh DB session
    background_tasks.add_task(run_hf_task, task, database.SessionLocal)

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
        "responses": [ul.response for ul in user_logs],
    }
