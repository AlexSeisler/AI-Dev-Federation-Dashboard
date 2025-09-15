import requests

API_URL = "http://localhost:8080"

def get_token():
    resp = requests.post(
        f"{API_URL}/auth/login",
        json={"email": "admin@example.com", "password": "adminpass"},
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    return token


def run_task(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}/tasks/run/brainstorm"
    resp = requests.post(url, headers=headers)

    print("Run Task Response:", resp.status_code)
    print("Raw Text:", resp.text)   # <-- add this

    try:
        return resp.json().get("task_id"), headers
    except Exception as e:
        print("❌ JSON parse error:", e)
        return None, headers



def get_task(task_id, headers):
    url = f"{API_URL}/tasks/{task_id}"
    resp = requests.get(url, headers=headers)
    print("Get Task Response:", resp.status_code, resp.json())


if __name__ == "__main__":
    token = get_token()
    print("✅ Got JWT:", token[:40] + "...")

    task_id, headers = run_task(token)
    if task_id:
        print(f"\nFetching task {task_id}...\n")
        get_task(task_id, headers)
