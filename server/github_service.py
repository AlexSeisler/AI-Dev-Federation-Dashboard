import requests
from fastapi import HTTPException
import base64

class GitHubService:
    """
    Minimal read-only GitHub service for AI-Dev-Federation-Dashboard.
    Provides safe access to repo tree, file content, file structure, history, and branch SHA.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, owner: str = "AlexSeisler", repo: str = "AI-Dev-Federation-Dashboard", token: str = None):
        self.owner = owner
        self.repo = repo
        self.headers = {"Authorization": f"token {token}"} if token else {}

    def get_repo_tree(self, branch: str = "main", recursive: bool = True):
        """Fetch the repo tree (read-only)."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/git/trees/{branch}"
        if recursive:
            url += "?recursive=1"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"GitHub tree fetch failed: {resp.text}")
        return resp.json()

    def get_file(self, file_path: str, branch: str = "main"):
        """Fetch raw file content."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/contents/{file_path}?ref={branch}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"GitHub file fetch failed: {resp.text}")
        data = resp.json()
        if "content" not in data:
            raise HTTPException(status_code=500, detail="Invalid file response from GitHub")
        return base64.b64decode(data["content"]).decode("utf-8")

    def get_file_history(self, file_path: str, branch: str = "main"):
        """Fetch commit history for a file."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/commits?path={file_path}&sha={branch}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"GitHub history fetch failed: {resp.text}")
        return resp.json()




    def get_branch_sha(self, branch: str = "main"):
        """Get latest commit SHA for a branch."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/git/ref/heads/{branch}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"GitHub SHA fetch failed: {resp.text}")
        return resp.json()["object"]["sha"]

    def parse_file_structure(self, code: str):
        """
        Dummy parser for file structure.
        In a real system, this would call a parser (like LibCST).
        For demo, we just split functions/classes.
        """
        lines = code.splitlines()
        structure = []
        for i, line in enumerate(lines):
            if line.strip().startswith("def "):
                structure.append({"type": "function", "name": line.strip().split()[1].split("(")[0], "line": i + 1})
            elif line.strip().startswith("class "):
                structure.append({"type": "class", "name": line.strip().split()[1].split("(")[0], "line": i + 1})
        return structure
