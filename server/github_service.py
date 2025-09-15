import requests
from requests.exceptions import RequestException
from fastapi import APIRouter, HTTPException
from typing import Optional
from server.config import settings

router = APIRouter(prefix="/repo", tags=["repo"])


class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.tokens = {
            "finegrained": settings.github_fine_token,
            "classic": settings.github_token,
        }
        self.timeout = 10

    def _request(self, method, url, use_auth=True, **kwargs):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Dev-Federation-Dashboard",
        }

        if use_auth and (self.tokens["finegrained"] or self.tokens["classic"]):
            token = self.tokens["finegrained"] or self.tokens["classic"]
            scheme = "Bearer" if self.tokens["finegrained"] else "token"
            headers["Authorization"] = f"{scheme} {token}"

        print(f"[GITHUB API REQUEST] {method} {url} (auth={use_auth})")
        try:
            response = requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
            print(f"[GITHUB API STATUS] {response.status_code}")
            if response.status_code != 200:
                print(f"[GITHUB API BODY] {response.text[:500]}")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"[GITHUB API ERROR] {method} {url} failed: {str(e)}")
            raise

    def get_repo_tree(
        self,
        owner,
        repo,
        branch=None,
        recursive=True,
        path_prefix=None,
        limit=None,
        offset=None,
    ):
        # ✅ Step 1: Repo metadata
        repo_url = f"{self.base_url}/repos/{owner}/{repo}"
        repo_data = self._request("GET", repo_url, use_auth=False)
        default_branch = repo_data.get("default_branch", "main")

        if not branch:
            branch = default_branch
        print(f"[INFO] Using branch: {branch}")

        # ✅ Step 2: Resolve SHA
        sha = None
        try:
            commit_url = f"{self.base_url}/repos/{owner}/{repo}/commits/{branch}"
            commit_data = self._request("GET", commit_url, use_auth=False)
            sha = commit_data["sha"]
        except Exception as e1:
            print(f"[WARN] commit lookup failed: {e1}")
            try:
                branch_url = f"{self.base_url}/repos/{owner}/{repo}/branches/{branch}"
                branch_data = self._request("GET", branch_url, use_auth=False)
                sha = branch_data["commit"]["sha"]
            except Exception as e2:
                print(f"[WARN] branch lookup failed: {e2}")
                ref_url = f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/{branch}"
                ref_data = self._request("GET", ref_url, use_auth=False)
                sha = ref_data["object"]["sha"]

        if not sha:
            raise RuntimeError(f"Could not resolve branch {branch} to SHA")

        # ✅ Step 3: Get tree
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{sha}?recursive={1 if recursive else 0}"
        raw_tree = self._request("GET", url, use_auth=False).get("tree", [])

        # ✅ Step 4: Apply filters
        if path_prefix:
            raw_tree = [item for item in raw_tree if item["path"].startswith(path_prefix)]
        if offset is not None and limit is not None:
            raw_tree = raw_tree[offset:offset + limit]

        # ✅ Step 5: Condense
        condensed = [
            {"path": item["path"], "type": item["type"], "size": item.get("size", 0)}
            for item in raw_tree
        ]

        return {
            "repo": f"{owner}/{repo}",
            "branch": branch,
            "count": len(condensed),
            "files": condensed,
        }

    def get_file_content(self, owner, repo, path, branch=None, max_chars: int = 20000):
        """
        Fetch raw file content with a safety limit (~5000 tokens).
        Truncates from the bottom if the file is too long.
        """
        if not branch:
            # resolve default branch
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            repo_data = self._request("GET", repo_url, use_auth=False)
            branch = repo_data.get("default_branch", "main")

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        file_data = self._request("GET", url, use_auth=False)

        import base64
        content = base64.b64decode(file_data["content"]).decode("utf-8", errors="ignore")

        if len(content) > max_chars:
            print(f"[WARN] Truncating file {path}: {len(content)} → {max_chars} chars")
            content = content[:max_chars]

        return {
            "repo": f"{owner}/{repo}",
            "branch": branch,
            "path": path,
            "size": len(content),
            "content": content,
        }


# ✅ Routes
@router.get("/tree")
async def get_repo_tree(
    repo_id: str,
    branch: str = "main",
    recursive: bool = True,
    path_prefix: Optional[str] = "",
):
    try:
        owner, repo = repo_id.split("/")
        service = GitHubService()
        return service.get_repo_tree(owner, repo, branch, recursive, path_prefix)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve repo tree: {str(e)}")


@router.get("/file")
async def get_repo_file(
    repo_id: str,
    path: str,
    branch: str = "main",
):
    try:
        owner, repo = repo_id.split("/")
        service = GitHubService()
        return service.get_file_content(owner, repo, path, branch)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")
