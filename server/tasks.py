# server/tasks.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
import traceback
from datetime import datetime

from server.hf_client import run_completion
from server.github_service import GitHubService
from server.debug import debug_log

router = APIRouter(prefix="/tasks", tags=["tasks"])

# --- In-memory stores ---
TASKS: dict[int, dict] = {}
LOGS: dict[int, list] = {}
task_queues: dict[int, asyncio.Queue] = {}

# Simple auto-increment task ID
NEXT_TASK_ID = 1

# Initialize GitHub service
github_service = GitHubService()


# --- Helpers ---

async def stream_logs(log_queue: asyncio.Queue):
    """Helper to stream logs via SSE with initial heartbeat."""
    yield 'data: {"event": "connected"}\n\n'
    while True:
        message = await log_queue.get()
        if message is None:
            break
        yield f"data: {json.dumps(message)}\n\n"


def log_event(task_id: int, event: str, log_queue: asyncio.Queue | None = None):
    """Store log in memory and push to SSE queue."""
    entry = {"event": event, "timestamp": datetime.utcnow().isoformat()}
    LOGS[task_id].append(entry)

    if log_queue:
        asyncio.create_task(log_queue.put(entry))

    if task_id in task_queues:
        asyncio.create_task(task_queues[task_id].put(entry))

    debug_log(f"Task {task_id} - {event}")


async def run_hf_task(task_id: int, preset: str, context: str, log_queue: asyncio.Queue):
    """Runner logic with Hugging Face integration (no DB)."""
    try:
        TASKS[task_id]["status"] = "running"
        repo_context = ""

        # --- Handle presets ---
        if preset == "structure":
            log_event(task_id, "📂 Fetching repo tree...", log_queue)
            tree = github_service.get_repo_tree("AlexSeisler", "AI-Dev-Federation-Dashboard")
            repo_context = f"Repo Tree:\n{json.dumps(tree, indent=2)}"
        elif preset == "file":
            log_event(task_id, "📂 Fetching file src/App.tsx...", log_queue)
            code = github_service.get_file("AlexSeisler", "AI-Dev-Federation-Dashboard", "src/App.tsx")
            repo_context = f"File: src/App.tsx\n\n{code[:5000]}..."
        elif preset == "brainstorm":
            log_event(task_id, "📊 Starting brainstorm (no repo context)...", log_queue)
        else:
            log_event(task_id, f"⚠️ Unknown preset: {preset}", log_queue)

        # --- Hugging Face Call ---
        log_event(task_id, "📡 Sending request to Hugging Face...", log_queue)
        response_text = run_completion(preset, context or "", [], repo_context)

        # ✅ Console log (truncated for readability)
        preview = response_text[:200] + ("..." if len(response_text) > 200 else "")
        log_event(task_id, f"✅ HF Response: {preview}", log_queue)

        # ✅ Store full response for AI Output panel
        TASKS[task_id]["status"] = "completed"
        TASKS[task_id]["output"] = response_text

    except Exception as e:
        error_detail = f"Task failed: {type(e).__name__} - {e}"
        traceback.print_exc()
        log_event(task_id, f"❌ {error_detail}", log_queue)
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["output"] = error_detail

    finally:
        await log_queue.put(None)
        if task_id in task_queues:
            await task_queues[task_id].put(None)
        debug_log("Task finished", context={"task_id": task_id})


# --- API Routes ---

@router.post("/run/{preset}")
async def run_task(preset: str, context: dict | str | None = None):
    """Start a new runner task (demo in-memory)."""
    global NEXT_TASK_ID
    task_id = NEXT_TASK_ID
    NEXT_TASK_ID += 1

    TASKS[task_id] = {
        "id": task_id,
        "type": preset,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "context": context if isinstance(context, str) else json.dumps(context or {}),
        "output": None,
    }
    LOGS[task_id] = []

    log_queue = asyncio.Queue()
    task_queues[task_id] = log_queue
    asyncio.create_task(run_hf_task(task_id, preset, TASKS[task_id]["context"], log_queue))

    return {"task_id": task_id, "status": "started"}


@router.get("/{task_id}")
async def get_task(task_id: int):
    """Return task details with logs + full output."""
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        **task,
        "logs": LOGS.get(task_id, []),     # truncated entries for console
        "output": task.get("output", ""),  # full AI response
    }


@router.get("/{task_id}/stream")
async def stream_task(task_id: int, request: Request):
    """Stream logs for a running task (SSE)."""
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_id not in task_queues:
        task_queues[task_id] = asyncio.Queue()

    log_queue = task_queues[task_id]

    async def event_generator():
        # replay existing logs
        for log in LOGS.get(task_id, []):
            yield f"data: {json.dumps(log)}\n\n"
        # now stream new logs
        async for message in stream_logs(log_queue):
            yield message

    return StreamingResponse(event_generator(), media_type="text/event-stream")
