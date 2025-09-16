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

# Initialize GitHub service
github_service = GitHubService()


# --- Helpers --- #

async def stream_logs(log_queue: asyncio.Queue):
    """Helper to stream logs via SSE."""
    while True:
        message = await log_queue.get()
        if message is None:  # end of stream
            break
        yield f"data: {json.dumps(message)}\n\n"


def log_event(db: Session, task: Task, event: str, log_queue: asyncio.Queue):
    """Persist and stream log events."""
    log_entry = UserLog(task_id=task.id, response=event, timestamp=datetime.utcnow())
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    asyncio.create_task(log_queue.put({"event": event, "timestamp": log_entry.timestamp.isoformat()}))


# --- Main Task Runner --- #

async def run_hf_task(task: Task, preset: str, context: str, db: Session, user_id: int, log_queue: asyncio.Queue):
    """Runner logic with repo context + Hugging Face integration."""
    try:
        task.status = "running"
        db.commit()

        repo_context = ""

        # Parse context JSON if provided
        context_data = {}
        if context:
            try:
                context_data = json.loads(context)
            except Exception:
                context_data = {"raw": context}

        # Resolve repo owner/repo (default fallback)
        owner, repo = "AlexSeisler", "AI-Dev-Federation-Dashboard"
        if "repo_id" in context_data and "/" in context_data["repo_id"]:
            owner, repo = context_data["repo_id"].split("/", 1)

        # --- Handle presets dynamically ---
        if preset == "structure":
            log_event(db, task, "📂 Fetching repo tree...", log_queue)
            tree = github_service.get_repo_tree(owner, repo)
            repo_context += f"Repo Tree:\n{json.dumps(tree, indent=2)}\n"

        elif preset == "file":
            file_path = context_data.get("file_path", "src/App.tsx")
            log_event(db, task, f"📂 Fetching file {file_path}...", log_queue)
            code = github_service.get_file(owner, repo, file_path)
            repo_context += f"File: {file_path}\n\n{code[:5000]}...\n"

        elif preset == "brainstorm":   # ✅ updated to match frontend ID
            log_event(db, task, "📊 Starting alignment/plan task (no repo context)...", log_queue)

        else:
            log_event(db, task, f"⚠️ Unknown preset: {preset}", log_queue)


        # Save repo_context
        task.context = repo_context
        db.commit()

        # --- Hugging Face Call ---
        log_event(db, task, "📡 Sending request to Hugging Face...", log_queue)

        # Load last 5 memory entries
        memory_entries = (
            db.query(Memory)
            .filter(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
            .limit(5)
            .all()
        )
        memory_context = [
            {"role": m.role, "content": m.content}
            for m in memory_entries if m.content
        ]
        response_text = run_completion(preset, context, memory_context, repo_context)

        # Persist to memory (assistant role)
        memory_entry = Memory(
            user_id=user_id,
            role="assistant",
            content=response_text,
            created_at=datetime.utcnow()
        )
        db.add(memory_entry)
        db.commit()

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
async def run_task(
    preset: str,
    request: dict,   # <-- instead of just `context: str`
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Start a new runner task."""
    user_id = current_user.get("id")

    # Extract clean context
    context = ""
    if preset == "brainstorm":
        # ✅ Pass user text directly
        context = request.get("context", "").strip()
    else:
        # ✅ Repo/file presets use JSON
        ctx = request.get("context", {})
        if isinstance(ctx, dict):
            context = json.dumps(ctx)
        else:
            context = str(ctx)

    # Create DB task
    task = Task(
        user_id=user_id,
        type=preset,
        status="pending",
        created_at=datetime.utcnow(),
        context=context  # ✅ store clean context
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    log_queue = asyncio.Queue()
    asyncio.create_task(run_hf_task(task, preset, context, db, user_id, log_queue))

    return {"task_id": task.id, "status": "started"}




@router.get("/{task_id}/stream")
async def stream_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Stream logs for a running task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    log_queue = asyncio.Queue()

    # Replay existing logs
    existing_logs = db.query(UserLog).filter(UserLog.task_id == task_id).all()
    for log in existing_logs:
        await log_queue.put({"event": log.response, "timestamp": log.timestamp.isoformat()})

    return StreamingResponse(stream_logs(log_queue), media_type="text/event-stream")


@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
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
        "logs": [{"event": log.response, "timestamp": log.timestamp.isoformat()} for log in logs],
    }
