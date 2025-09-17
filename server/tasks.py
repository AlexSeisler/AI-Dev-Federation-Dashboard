"""
tasks.py — Task Management API
==============================

This module provides the **task execution layer** for the AI Dev Federation Dashboard backend.

Responsibilities:
- Define API routes for running and monitoring tasks (`/tasks`).
- Handle task lifecycle (pending → running → completed/failed).
- Manage in-memory task state and logs.
- Stream logs/results back to the frontend via Server-Sent Events (SSE).
- Integrate with external services (GitHubService + Hugging Face client).

"""

import asyncio
import json
import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from server.hf_client import run_completion
from server.github_service import GitHubService
from server.debug import debug_log

# ----------------------------------------------------
# Router Setup
# ----------------------------------------------------
router = APIRouter(prefix="/tasks", tags=["tasks"])

# ----------------------------------------------------
# In-Memory Task Stores (demo implementation)
# ----------------------------------------------------
TASKS: dict[int, dict] = {}
LOGS: dict[int, list] = {}
task_queues: dict[int, asyncio.Queue] = {}

NEXT_TASK_ID = 1  # Simple auto-increment counter
github_service = GitHubService()

# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
async def stream_logs(log_queue: asyncio.Queue):
    """Yield log messages via SSE (with initial heartbeat)."""
    yield 'data: {"event": "connected"}\n\n'
    while True:
        message = await log_queue.get()
        if message is None:
            break
        yield f"data: {json.dumps(message)}\n\n"


def log_event(task_id: int, event: str, log_queue: asyncio.Queue | None = None):
    """Append log entry to memory + push to SSE queues."""
    entry = {"event": event, "timestamp": datetime.utcnow().isoformat()}
    LOGS[task_id].append(entry)

    # Push to specific queue (if provided)
    if log_queue:
        asyncio.create_task(log_queue.put(entry))
    # Push to global task queue
    if task_id in task_queues:
        asyncio.create_task(task_queues[task_id].put(entry))

    debug_log(f"Task {task_id} - {event}")


async def run_hf_task(task_id: int, preset: str, context: str, log_queue: asyncio.Queue):
    """Run a task with Hugging Face + optional GitHub context."""
    try:
        TASKS[task_id]["status"] = "running"
        repo_context = ""

        # Preset routing
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

        # Hugging Face call
        log_event(task_id, "📡 Sending request to Hugging Face...", log_queue)
        response_text = run_completion(preset, context or "", [], repo_context)

        # Preview in logs (truncated for readability)
        preview = response_text[:200] + ("..." if len(response_text) > 200 else "")
        log_event(task_id, f"✅ HF Response: {preview}", log_queue)

        # Store result
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

# ----------------------------------------------------
# API Routes
# ----------------------------------------------------
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
        "logs": LOGS.get(task_id, []),
        "output": task.get("output", ""),
    }


@router.get("/{task_id}/stream")
async def stream_task(task_id: int, request: Request):
    """Stream logs for a running task (Server-Sent Events)."""
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_id not in task_queues:
        task_queues[task_id] = asyncio.Queue()

    log_queue = task_queues[task_id]

    async def event_generator():
        # Replay existing logs
        for log in LOGS.get(task_id, []):
            yield f"data: {json.dumps(log)}\n\n"
        # Stream new logs
        async for message in stream_logs(log_queue):
            yield message

    return StreamingResponse(event_generator(), media_type="text/event-stream")
