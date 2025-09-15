# server/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import json
import traceback

from server.database import get_db
from server.models import Task, UserLog, Memory
from server.github_service import GitHubService
from server.hf_client import run_completion
from server.jwt_utils import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Initialize GitHub service (read-only)
github_service = GitHubService()

# --- Runner Task Execution --- #

async def stream_logs(log_queue: asyncio.Queue):
    """Helper to stream logs via SSE."""
    while True:
        message = await log_queue.get()
        if message is None:  # end of stream
            break
        yield f"data: {json.dumps(message)}\n\n"

def log_event(db: Session, task: Task, event: str, log_queue: asyncio.Queue):
    """Persist and stream log events."""
    log_entry = UserLog(task_id=task.id, event=event, timestamp=datetime.utcnow())
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    asyncio.create_task(log_queue.put({"event": event, "timestamp": log_entry.timestamp.isoformat()}))

async def run_hf_task(task: Task, preset: str, context: str, db: Session, user_id: int, log_queue: asyncio.Queue):
    """Main runner logic with repo context + Hugging Face integration."""
    try:
        task.status = "running"
        db.commit()

        # --- Repo Context Fetching --- #
        repo_context = ""
        if preset == "structure":
            log_event(db, task, "📂 Fetching repo tree...", log_queue)
            tree = github_service.get_repo_tree()
            repo_context += f"Repo Tree:\n{json.dumps(tree, indent=2)}\n"

            log_event(db, task, "📂 Analyzing file structure...", log_queue)
            # For demo, parse App.tsx as an example
            code = github_service.get_file("src/App.tsx")
            structure = github_service.parse_file_structure(code)
            repo_context += f"File Structure (App.tsx):\n{json.dumps(structure, indent=2)}\n"

        elif preset == "file":
            log_event(db, task, "📂 Fetching example file...", log_queue)
            code = github_service.get_file("src/App.tsx")
            repo_context += f"File: src/App.tsx\n\n{code[:1000]}...\n"  # cap at 1k chars

            log_event(db, task, "📂 Parsing file structure...", log_queue)
            structure = github_service.parse_file_structure(code)
            repo_context += f"File Structure:\n{json.dumps(structure, indent=2)}\n"

        elif preset == "brainstorm":
            log_event(db, task, "📂 Fetching repo tree for brainstorm...", log_queue)
            tree = github_service.get_repo_tree()
            repo_context += f"Repo Tree:\n{json.dumps(tree, indent=2)}\n"

        # Persist repo context in task
        task.context = repo_context
        db.commit()

        # --- Hugging Face Call --- #
        log_event(db, task, "📡 Sending request to Hugging Face...", log_queue)

        # Load memory
        memory_entries = db.query(Memory).filter(Memory.user_id == user_id).order_by(Memory.created_at.desc()).limit(5).all()
        memory_context = "\n".join([m.response for m in memory_entries if m.response])

        response_text = run_completion(preset, context, memory_context, repo_context)

        # Persist to memory
        memory_entry = Memory(user_id=user_id, response=response_text, created_at=datetime.utcnow())
        db.add(memory_entry)
        db.commit()

        # Final log
        log_event(db, task, f"✅ HF Response: {response_text[:200]}...", log_queue)

        task.status = "completed"
        db.commit()

    except Exception as e:
        error_detail = f"Task failed: {type(e).__name__} - {e}"
        traceback.print_exc()
        log_event(db, task, f"❌ {error_detail}", log_queue)
        task.status = "failed"
        db.commit()

    finally:
        await log_queue.put(None)  # end SSE stream

# --- API Routes --- #

@router.post("/run/{preset}")
async def run_task(preset: str, context: str = "", db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Start a new runner task."""
    user_id = current_user["id"]

    # Create DB task
    task = Task(user_id=user_id, type=preset, status="pending", created_at=datetime.utcnow(), context=context)
    db.add(task)
    db.commit()
    db.refresh(task)

    log_queue = asyncio.Queue()
    asyncio.create_task(run_hf_task(task, preset, context, db, user_id, log_queue))

    return {"task_id": task.id, "status": "started"}

@router.get("/{task_id}/stream")
async def stream_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Stream logs for a running task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    log_queue = asyncio.Queue()
    # Replay existing logs
    existing_logs = db.query(UserLog).filter(UserLog.task_id == task_id).all()
    for log in existing_logs:
        await log_queue.put({"event": log.event, "timestamp": log.timestamp.isoformat()})

    return StreamingResponse(stream_logs(log_queue), media_type="text/event-stream")

@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Fetch task details + logs."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    logs = db.query(UserLog).filter(UserLog.task_id == task_id).all()
    return {
        "id": task.id,
        "type": task.type,
        "status": task.status,
        "context": task.context,
        "logs": [{"event": log.event, "timestamp": log.timestamp.isoformat()} for log in logs]
    }
