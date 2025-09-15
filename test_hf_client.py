# test_hf_client.py
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_API_KEY")
assert HF_TOKEN, "❌ Missing HF_TOKEN in environment!"

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query(prompt: str):
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct:cerebras",  # ✅ Explicit provider
        "messages": [
            {"role": "system", "content": "You are DevBot, an AI assistant for analyzing repos."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
    }

    print("🔍 Sending payload to HF:", payload)
    resp = requests.post(API_URL, headers=HEADERS, json=payload)
    print("Status:", resp.status_code)
    print("Raw:", resp.text[:500])

    if resp.status_code != 200:
        raise RuntimeError(f"HF API failed: {resp.status_code} {resp.text}")

    return resp.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    test_prompt = "Summarize the key risks in a repo using SQLAlchemy and FastAPI."
    output = query(test_prompt)
    print("\n✅ Response from LLaMA 3.1 (Cerebras):\n", output)
