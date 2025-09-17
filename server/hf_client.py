"""
hf_client.py — Hugging Face API Client
======================================

This module handles all interaction with the Hugging Face Inference Router API.

Responsibilities:
- Manage API authentication and environment configuration.
- Provide task-specific system presets (brainstorm, structure, file review).
- Send chat completion requests with retries, timeouts, and backoff.
- Normalize Hugging Face responses into plain strings.
- Integrate with DevBot’s execution pipeline.
"""

import os
import time
import json
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from server.debug import debug_log

# ----------------------------------------------------
# Environment & Config
# ----------------------------------------------------
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
HF_MAX_TOKENS = int(os.getenv("HF_MAX_TOKENS", "8192"))  # default: 8k

if not HF_API_KEY:
    raise ValueError("❌ HF_API_KEY not found. Check your .env file.")

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ----------------------------------------------------
# System Presets
# ----------------------------------------------------
SYSTEM_PRESETS = {
    "brainstorm": (
        "You are DevBot. Assist with strategic planning and brainstorming. "
        "Think step by step, propose improvements, and generate ideas."
    ),
    "structure": (
        "You are DevBot. Summarize the repository structure and analyze "
        "its architecture, highlighting key modules and responsibilities."
    ),
    "file": (
        "You are DevBot. Review the given file in detail, explain its logic, "
        "and suggest improvements or refactors where useful."
    ),
}

# ----------------------------------------------------
# Low-Level Helpers
# ----------------------------------------------------
def _query_hf(payload: Dict[str, Any], retries: int = 3, backoff: int = 2, timeout: int = 60) -> Dict[str, Any]:
    """POST request to Hugging Face API with retry, timeout, and backoff."""
    for attempt in range(retries):
        try:
            debug_log("HF API request", context={"attempt": attempt + 1, "model": payload.get("model")})
            resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=timeout)

            debug_log("HF API response status", context={"status_code": resp.status_code})
            if resp.status_code == 200:
                debug_log("HF API success", context={"length": len(resp.text)})
                return resp.json()

            debug_log("HF API error", context={"status": resp.status_code, "text": resp.text[:500]})

        except requests.Timeout:
            debug_log("HF API timeout", context={"timeout": timeout})
        except Exception as e:
            debug_log("HF API request failed", e)

        # Final retry exhausted
        if attempt == retries - 1:
            debug_log("HF API retries exhausted")
            raise RuntimeError(f"❌ HF API failed after {retries} attempts")

        wait = backoff * (2 ** attempt)
        debug_log("HF API retrying", context={"wait_seconds": wait})
        time.sleep(wait)

    raise RuntimeError("❌ HF API unreachable.")


def _extract_response(result: Dict[str, Any]) -> str:
    """Normalize Hugging Face API response into a string output."""
    try:
        if "choices" in result:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            if "delta" in choice and "content" in choice["delta"]:
                return choice["delta"]["content"]
            if "text" in choice:
                return choice["text"]

        if "generated_text" in result:
            return result["generated_text"]

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

    except Exception as e:
        debug_log("HF response extraction failed", e)

    debug_log("HF unexpected response format", context={"result": json.dumps(result)[:500]})
    return "[Error: unexpected response format]"

# ----------------------------------------------------
# Public API
# ----------------------------------------------------
def run_completion(
    preset: str,
    context: str,
    memory: Optional[List[Dict[str, str]]] = None,
    repo_context: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Run a Hugging Face chat completion request using the Router API.
    
    Args:
        preset: Task mode (brainstorm, structure, file).
        context: User input or task context string.
        memory: Optional conversation history (last 5 messages).
        repo_context: Optional repository metadata (tree, file content).
        max_tokens: Optional override for token limit.
    """
    if preset not in SYSTEM_PRESETS:
        debug_log("Invalid preset in run_completion", context={"preset": preset})
        raise ValueError(f"❌ Invalid preset: {preset}")

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PRESETS[preset]}]

    if repo_context:
        messages.append({"role": "system", "content": f"Repo Context:\n{repo_context}"})

    user_message = str(context) if context is not None else ""
    messages.append({"role": "user", "content": user_message})

    if memory:
        for m in memory[-5:]:
            messages.append({"role": m["role"], "content": str(m["content"])})

    payload = {
        "model": HF_MODEL,
        "messages": messages,
        "max_tokens": max_tokens or HF_MAX_TOKENS,
    }

    debug_log("HF Final Payload", context={
        "model": HF_MODEL,
        "messages": [{"role": msg["role"], "content": str(msg["content"])[:200]} for msg in messages],
    })

    result = _query_hf(payload)
    response = _extract_response(result)

    debug_log("HF Final Response", context={"response_preview": response[:300]})
    return response
