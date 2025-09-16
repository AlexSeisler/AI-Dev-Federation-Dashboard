from fastapi import APIRouter, Depends, HTTPException, Request
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
from server.jwt_utils import get_current_user, decode_token
from server.debug import debug_log  # ✅ new

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Initialize GitHub service
github_service = GitHubService()

# ✅ global dict to hold per-task queues
task_queues: dict[int, asyncio.Queue] = {}

# --- Helpers --- #

async def stream_logs(log_queue: asyncio.Queue):
    """Helper to stream logs via SSE with initial heartbeat."""
    # ✅ send heartbeat immediately
    yield 'data: {"event": "connected"}\n\n'

    while True:
        message = await log_queue.get()
        if message is None:
            break
        yield f"data: {json.dumps(message)}\n\n"


def log_event(db: Session, task: Task, event: str, log_queue: asyncio.Queue | None = None):
    """Persist and stream log events."""
    log_entry = UserLog(task_id=task.id, response=event, timestamp=datetime.utcnow())
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    # ✅ Stream into provided queue
    if log_queue:
        asyncio.create_task(
            log_queue.put({"event": event, "timestamp": log_entry.timestamp.isoformat()})
        )

    # ✅ Also stream into global queue if it exists
    if task.id in task_queues:
        try:
            asyncio.create_task(
                task_queues[task.id].put({"event": event, "timestamp": log_entry.timestamp.isoformat()})
            )
        except Exception as e:
            debug_log("Failed to enqueue SSE log", e)

    # ✅ mirror to debug log
    debug_log(f"Task {task.id} - {event}", context={"task_id": task.id, "event": event})

# --- Main Task Runner --- #

async def run_hf_task(task: Task, preset: str, context: str, db: Session, user_id: int, log_queue: asyncio.Queue):
    """Runner logic with repo context + Hugging Face integration."""
    try:
        debug_log("Task started", context={"task_id": task.id, "preset": preset})
        task.status = "running"
        db.commit()

        repo_context = ""

        # --- Normalize user context ---
        debug_log("Normalizing user context", context={"raw": context})
        user_context_str = ""
        if context:
            try:
                parsed = json.loads(context) if isinstance(context, str) else context
                if isinstance(parsed, dict):
                    if "raw" in parsed:
                        user_context_str = str(parsed["raw"])
                    elif "context" in parsed:
                        user_context_str = str(parsed["context"])
                    elif "file_path" in parsed or "repo_id" in parsed:
                        user_context_str = f"Repo: {parsed.get('repo_id','')}, File: {parsed.get('file_path','')}"
                    else:
                        user_context_str = json.dumps(parsed)
                else:
                    user_context_str = str(parsed)
            except Exception as e:
                debug_log("Failed JSON parse of context", e)
                user_context_str = str(context)

        if not user_context_str:
            user_context_str = "No user input provided."
        debug_log("User context resolved", context={"context": user_context_str})

        # Resolve repo owner/repo (default fallback)
        owner, repo = "AlexSeisler", "AI-Dev-Federation-Dashboard"
        if isinstance(user_context_str, dict) and "repo_id" in user_context_str and "/" in user_context_str["repo_id"]:
            owner, repo = user_context_str["repo_id"].split("/", 1)
        debug_log("Repo resolved", context={"owner": owner, "repo": repo})

        # --- Handle presets dynamically ---
        if preset == "structure":
            log_event(db, task, "📂 Fetching repo tree...", log_queue)
            tree = github_service.get_repo_tree(owner, repo)
            repo_context += f"Repo Tree:\n{json.dumps(tree, indent=2)}\n"
            debug_log("Repo tree fetched", context={"entries": len(tree)})

        elif preset == "file":
            file_path = user_context_str.get("file_path", "src/App.tsx") if isinstance(user_context_str, dict) else "src/App.tsx"
            log_event(db, task, f"📂 Fetching file {file_path}...", log_queue)
            code = github_service.get_file(owner, repo, file_path)
            repo_context += f"File: {file_path}\n\n{code[:5000]}...\n"
            debug_log("File fetched", context={"file_path": file_path, "len": len(code)})

        elif preset == "brainstorm":
            log_event(db, task, "📊 Starting alignment/plan task (no repo context)...", log_queue)
            debug_log("Brainstorm mode", context={})

        else:
            log_event(db, task, f"⚠️ Unknown preset: {preset}", log_queue)
            debug_log("Unknown preset", context={"preset": preset})

        task.context = repo_context
        db.commit()
        debug_log("Repo context saved", context={"len": len(repo_context)})

        # --- Hugging Face Call ---
        log_event(db, task, "📡 Sending request to Hugging Face...", log_queue)
        debug_log("Sending request to HF", context={"preset": preset})

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
        debug_log("Loaded memory context", context={"entries": len(memory_context)})

        # Ensure context is plain text (no double-wrapped JSON)
        clean_context = user_context_str
        if isinstance(user_context_str, dict):
            clean_context = user_context_str.get("raw") or user_context_str.get("context") or json.dumps(user_context_str)

        response_text = run_completion(preset, clean_context, memory_context, repo_context)

        debug_log("HF response received", context={"len": len(response_text)})

        # Save assistant response to memory
        memory_entry = Memory(
            user_id=user_id,
            role="assistant",
            content=response_text,
            created_at=datetime.utcnow(),
        )
        db.add(memory_entry)
        db.commit()
        debug_log("Assistant response persisted", context={"memory_id": memory_entry.id})

        log_event(db, task, f"✅ HF Response: {response_text[:200]}...", log_queue)

        task.status = "completed"
        db.commit()
        debug_log("Task marked completed", context={"task_id": task.id})

    except Exception as e:
        error_detail = f"Task failed: {type(e).__name__} - {e}"
        traceback.print_exc()
        log_event(db, task, f"❌ {error_detail}", log_queue)
        debug_log("Task failed", e, context={"task_id": task.id})
        task.status = "failed"
        db.commit()

    finally:
        await log_queue.put(None)
        if task.id in task_queues:
            await task_queues[task.id].put(None)
        debug_log("Task finished (cleanup)", context={"task_id": task.id})

# --- API Routes --- #

@router.post("/run/{preset}")
async def run_task(
    preset: str,
    context: dict = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Start a new runner task."""
    debug_log("Run task request", context={"preset": preset, "user": current_user.get("id")})
    user_id = current_user.get("id")

    # Store raw context as JSON only if needed
    if isinstance(context, dict):
        stored_context = json.dumps(context)
    elif isinstance(context, str):
        stored_context = context
    else:
        stored_context = ""

    task = Task(
        user_id=user_id,
        type=preset,
        status="pending",
        created_at=datetime.utcnow(),
        context=stored_context,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    debug_log("Task created", context={"task_id": task.id})

    if stored_context:
        db.add(Memory(
            user_id=user_id,
            role="user",
            content=stored_context,
            created_at=datetime.utcnow(),
        ))
        db.commit()
        debug_log("User context persisted", context={"task_id": task.id})

    log_queue = asyncio.Queue()
    task_queues[task.id] = log_queue  # ✅ save queue globally
    asyncio.create_task(run_hf_task(task, preset, stored_context, db, user_id, log_queue))

    return {"task_id": task.id, "status": "started"}


@router.get("/{task_id}/stream")
async def stream_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    """Stream logs for a running task with query param JWT fallback."""
    token = request.query_params.get("token")
    debug_log("Stream request", context={"task_id": task_id, "has_token": bool(token)})
    current_user = None

    if token:
        current_user = decode_token(token)
        debug_log("Stream JWT token decoded", context={"task_id": task_id})
    else:
        current_user = await get_current_user(request)

    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # ✅ Use the global queue created in run_task
    if task_id not in task_queues:
        task_queues[task_id] = asyncio.Queue()
    log_queue = task_queues[task_id]

    # ✅ Generator: replay old logs first, then stream new ones
    async def event_generator():
        # replay existing logs
        existing_logs = (
            db.query(UserLog).filter(UserLog.task_id == task_id).order_by(UserLog.timestamp.asc()).all()
        )
        for log in existing_logs:
            yield f"data: {json.dumps({'event': log.response, 'timestamp': log.timestamp.isoformat()})}\n\n"

        debug_log("Replayed existing logs", context={"task_id": task_id, "count": len(existing_logs)})

        # now stream live logs
        async for message in stream_logs(log_queue):
            yield message

    return StreamingResponse(event_generator(), media_type="text/event-stream")
