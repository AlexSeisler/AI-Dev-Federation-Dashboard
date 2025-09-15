import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "google/flan-t5-large")

if not HF_API_KEY:
    raise ValueError("HF_API_KEY not found. Check your .env file.")

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


def run_completion(preset: str, context: str, memory: List[Dict[str, str]] = None) -> str:
    """
    Run a Hugging Face text completion (Flan-T5).
    """

    # Add memory context (flatten into text)
    memory_text = ""
    if memory:
        for m in memory[-5:]:
            memory_text += f"{m['role'].upper()}: {m['content']}\n"

    # System prompt per preset
    system_prompts = {
        "structure": "Summarize repo structure, describe key files/classes, and suggest improvements.",
        "file": "Review this file, identify purpose, risks, inefficiencies, and improvements.",
        "brainstorm": "Engage in brainstorming session about repo tradeoffs and improvements.",
    }

    if preset not in system_prompts:
        raise ValueError(f"Invalid preset: {preset}")

    # Final prompt (plain text)
    prompt = f"{system_prompts[preset]}\n\nContext:\n{context}\n\nConversation:\n{memory_text}\n\nAnswer:"

    # Hugging Face inference API payload
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 512},
    }

    resp = requests.post(API_URL, headers=HEADERS, json=payload)

    if resp.status_code != 200:
        raise RuntimeError(f"Hugging Face API call failed: {resp.status_code} {resp.text}")

    result = resp.json()

    # Flan-T5 returns a list of dicts with "generated_text"
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    else:
        return str(result)
