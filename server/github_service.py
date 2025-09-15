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
        self.headers = {}

    def _request(self, method, url, use_auth=True, **kwargs):
        # If repo is public, allow unauthenticated calls
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
                print(f"[GITHUB API BODY] {response.text}")
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
        # ✅ Step 1: Always fetch repo metadata (no auth needed for public repos)
        repo_url = f"{self.base_url}/repos/{owner}/{repo}"
        repo_data = self._request("GET", repo_url, use_auth=False)
        default_branch = repo_data.get("default_branch", "main")

        if not branch:
            branch = default_branch
        print(f"[INFO] Using branch: {branch}")

        # ✅ Step 2: Resolve branch SHA (try commits → branches → refs)
        sha = None
        try:
            commit_url = f"{self.base_url}/repos/{owner}/{repo}/commits/{branch}"
            commit_data = self._request("GET", commit_url, use_auth=False)
            sha = commit_data["sha"]
            print(f"[INFO] Resolved branch {branch} → {sha} via /commits")
        except Exception as e1:
            print(f"[WARN] /commits failed: {e1}")
            try:
                branch_url = f"{self.base_url}/repos/{owner}/{repo}/branches/{branch}"
                branch_data = self._request("GET", branch_url, use_auth=False)
                sha = branch_data["commit"]["sha"]
                print(f"[INFO] Resolved branch {branch} → {sha} via /branches")
            except Exception as e2:
                print(f"[WARN] /branches failed: {e2}")
                try:
                    ref_url = f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/{branch}"
                    ref_data = self._request("GET", ref_url, use_auth=False)
                    sha = ref_data["object"]["sha"]
                    print(f"[INFO] Resolved branch {branch} → {sha} via /git/refs")
                except Exception as e3:
                    print(f"[ERROR] Could not resolve branch {branch}: {e3}")
                    raise RuntimeError(f"Branch resolution failed for {branch}")

        if not sha:
            raise RuntimeError(f"Could not resolve branch {branch} to SHA")

        # ✅ Step 3: Fetch tree using SHA
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{sha}?recursive={1 if recursive else 0}"
        tree_data = self._request("GET", url, use_auth=False)["tree"]

        # ✅ Step 4: Apply filters if needed
        if path_prefix:
            tree_data = [item for item in tree_data if item["path"].startswith(path_prefix)]
        if offset is not None and limit is not None:
            tree_data = tree_data[offset:offset + limit]

        return tree_data


# ✅ Route wrapper with detailed error logging
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
        result = service.get_repo_tree(owner, repo, branch, recursive, path_prefix)
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] get_repo_tree failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve repo tree: {str(e)}")
