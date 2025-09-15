import requests
import time

API_URL = "http://localhost:8080"


def get_token():
    """
    Login with admin credentials and return JWT token.
    """
    resp = requests.post(
        f"{API_URL}/auth/login",
        json={"email": "admin@example.com", "password": "adminpass"},
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    return token


def run_task(token, preset="brainstorm", context="Summarize the repo risks."):
    """
    Start a new task with preset + context.
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}/tasks/run/{preset}"
    resp = requests.post(url, headers=headers, json={"user_id": 1, "context": context})

    print("Run Task Response:", resp.status_code)
    print("Raw:", resp.text)

    resp.raise_for_status()
    return resp.json().get("task_id"), headers


def get_task(task_id, headers):
    """
    Poll task details until completed/failed.
    """
    url = f"{API_URL}/tasks/{task_id}"
    while True:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        print("Task Status:", data["status"])

        if data["status"] in ["completed", "failed"]:
            print("\n✅ Final Task Data:", data)
            return data

        time.sleep(2)


def stream_logs(task_id, headers):
    """
    Connect to SSE stream for real-time logs.
    """
    url = f"{API_URL}/tasks/{task_id}/stream"
    with requests.get(url, headers=headers, stream=True) as resp:
        print("SSE Stream Status:", resp.status_code)
        for line in resp.iter_lines():
            if line:
                print("SSE:", line.decode("utf-8"))
            if b"event: end" in line:
                break


if __name__ == "__main__":
    token = get_token()
    print("✅ Got JWT:", token[:40] + "...")

    task_id, headers = run_task(token, "brainstorm", "Analyze repo for inefficiencies.")
    if task_id:
        print(f"\n📡 Streaming logs for task {task_id}...\n")
        stream_logs(task_id, headers)

        print(f"\n📊 Polling final task {task_id}...\n")
        get_task(task_id, headers)
