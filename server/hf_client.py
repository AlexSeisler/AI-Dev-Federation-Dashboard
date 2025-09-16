import os
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import json

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
HF_MAX_TOKENS = int(os.getenv("HF_MAX_TOKENS", "8192"))  # ✅ configurable max tokens, default 8k

if not HF_API_KEY:
    raise ValueError("❌ HF_API_KEY not found. Check your .env file.")

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# System presets for different task modes
SYSTEM_PRESETS = {
    # Matches frontend: "Alignment/Plan"
    "brainstorm": "You are DevBot. Assist with strategic planning and brainstorming. "
                  "Think step by step, propose improvements, and generate ideas.",

    # Matches frontend: "Structure Analysis"
    "structure": "You are DevBot. Summarize the repository structure and analyze "
                 "its architecture, highlighting key modules and responsibilities.",

    # Matches frontend: "File Analysis"
    "file": "You are DevBot. Review the given file in detail, explain its logic, "
            "and suggest improvements or refactors where useful."
}



def _query_hf(payload: Dict[str, Any], retries: int = 3, backoff: int = 2, timeout: int = 60) -> Dict[str, Any]:
    """Low-level request helper with retry + exponential backoff + timeout."""
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


def _extract_response(result: Dict[str, Any]) -> str:
    """Normalize Hugging Face response into a clean string."""
    try:
        # OpenAI-style: choices[0].message.content
        if "choices" in result and "message" in result["choices"][0]:
            return result["choices"][0]["message"]["content"]

        # HF-style: choices[0].delta.content (streaming chunks)
        if "choices" in result and "delta" in result["choices"][0]:
            return result["choices"][0]["delta"].get("content", "")

        # HF text completion: choices[0].text
        if "choices" in result and "text" in result["choices"][0]:
            return result["choices"][0]["text"]

        # Fallback: generated_text
        if "generated_text" in result:
            return result["generated_text"]

    except Exception as e:
        print(f"❌ Failed to extract response: {e}")

    # Debug: dump response if schema unknown
    print(f"⚠️ Unexpected HF API response format: {result}")
    return "[Error: unexpected response format]"


def run_completion(
    preset: str,
    context: str,
    memory: Optional[List[Dict[str, str]]] = None,
    repo_context: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Run a Hugging Face chat completion request using the Router API.
    """
    if preset not in SYSTEM_PRESETS:
        raise ValueError(f"❌ Invalid preset: {preset}")

    messages = [
        {"role": "system", "content": SYSTEM_PRESETS[preset]},
    ]

    if repo_context:
        messages.append({"role": "system", "content": f"Repo Context:\n{repo_context}"})

    messages.append({"role": "user", "content": context})

    # Add prior memory if present
    if memory:
        for m in memory[-5:]:  # only keep last 5 entries
            messages.append({"role": m["role"], "content": m["content"]})

    payload = {
        "model": HF_MODEL,
        "messages": messages,
        "max_tokens": max_tokens or HF_MAX_TOKENS,
    }
    print("🔍 HF Final Payload:", json.dumps(payload, indent=2)[:5000])

    result = _query_hf(payload)
    return _extract_response(result)
