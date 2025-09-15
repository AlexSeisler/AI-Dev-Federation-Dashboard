import os
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

if not HF_API_KEY:
    raise ValueError("❌ HF_API_KEY not found. Check your .env file.")

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# System prompts for presets
SYSTEM_PRESETS = {
    "structure": "You are DevBot. Summarize repo structure, describe key files/classes, and suggest improvements.",
    "file": "You are DevBot. Review this file, identify purpose, risks, inefficiencies, and improvements.",
    "brainstorm": "You are DevBot. Engage in brainstorming session about repo tradeoffs and improvements.",
}


def _query_hf(payload: Dict[str, Any], retries: int = 3, backoff: int = 2, timeout: int = 60) -> Dict[str, Any]:
    """
    Low-level request helper with retry + exponential backoff + timeout.
    """
    for attempt in range(retries):
        try:
            print(f"📡 HF API attempt {attempt+1}/{retries} with model={payload.get('model')}")
            resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=timeout)

            print(f"HF API status={resp.status_code}")
            if resp.status_code == 200:
                print(f"✅ HF API success (len={len(resp.text)})")
                return resp.json()

            print(f"⚠️ HF API error {resp.status_code}: {resp.text[:300]}")

        except requests.Timeout:
            print(f"⏰ HF API request timed out after {timeout}s")

        except Exception as e:
            print(f"❌ HF API request failed: {e}")

        # Last attempt → raise error
        if attempt == retries - 1:
            raise RuntimeError(f"❌ HF API failed after {retries} attempts")

        # Retry with backoff
        wait = backoff * (2 ** attempt)
        print(f"🔄 Retrying in {wait}s...")
        time.sleep(wait)

    raise RuntimeError("❌ HF API unreachable.")


def run_completion(
    preset: str,
    context: str,
    memory: Optional[List[Dict[str, str]]] = None,
    max_tokens: int = 1024,
) -> Dict[str, Any]:
    """
    Run a Hugging Face chat completion request using the Router API.

    Args:
        preset: One of 'structure', 'file', 'brainstorm'.
        context: Repo/file text context.
        memory: Optional conversation memory [{"role": "user"/"assistant", "content": "..."}].
        max_tokens: Output token cap (default=1024, can raise to 2048).

    Returns:
        dict with structured fields:
            {
                "content": str,
                "raw": dict (HF API response),
            }
    """
    if preset not in SYSTEM_PRESETS:
        raise ValueError(f"❌ Invalid preset: {preset}")

    messages = [
        {"role": "system", "content": SYSTEM_PRESETS[preset]},
        {"role": "user", "content": context},
    ]

    # Add prior memory if present
    if memory:
        for m in memory[-5:]:  # only keep last 5 entries
            messages.append({"role": m["role"], "content": m["content"]})

    payload = {
        "model": HF_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    result = _query_hf(payload)

    try:
        content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(f"❌ Unexpected HF API response: {result}")

    return {"content": content, "raw": result}
