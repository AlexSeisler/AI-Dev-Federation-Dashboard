import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from typing import List, Dict

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")

if not HF_API_KEY:
    raise ValueError("HF_API_KEY not found. Check your .env file.")

# Initialize Hugging Face Inference Client
client = InferenceClient(
    provider="featherless-ai",
    api_key=HF_API_KEY,
)


def run_completion(preset: str, context: str, memory: List[Dict[str, str]] = None) -> str:
    """
    Run a Hugging Face completion with preset + context + memory.
    
    :param preset: Type of task (structure, file, brainstorm)
    :param context: Repo/file content or task input
    :param memory: List of previous conversation turns [{role, content}]
    :return: Generated response string
    """
    messages = []

    # Inject memory (last 3–5 entries)
    if memory:
        for m in memory[-5:]:
            messages.append({"role": m["role"], "content": m["content"]})

    # Add system preset
    system_prompts = {
        "structure": "You are DevBot. Summarize repo structure, describe key files/classes, and suggest improvements.",
        "file": "You are DevBot. Review this file, identify purpose, risks, inefficiencies, and improvements.",
        "brainstorm": "You are DevBot. Engage in brainstorming session about repo tradeoffs and improvements.",
    }

    if preset not in system_prompts:
        raise ValueError(f"Invalid preset: {preset}")

    messages.append({"role": "system", "content": system_prompts[preset]})

    # Add recruiter input context
    if context:
        messages.append({"role": "user", "content": context})

    # Run Hugging Face call
    completion = client.chat.completions.create(
        model=HF_MODEL,
        messages=messages,
    )

    return completion.choices[0].message["content"]