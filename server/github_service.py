import os
import requests
import base64
import urllib.parse
from urllib.parse import urlparse
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
        if not self.tokens["finegrained"] and not self.tokens["classic"]:
            print("fine: ", self.tokens["finegrained"])
            print("classic: ", self.tokens["classic"])
            raise ValueError("Both GITHUB_FINE_TOKEN and GITHUB_TOKEN must be set")

        self.timeout = 10
        self.headers = {}

    def _build_headers(self, token, scheme="token"):
        return {
            "Authorization": f"{scheme} {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Dev-Federation-Dashboard",
        }

    def _request(self, method, url, **kwargs):
        owner = None
        try:
            parts = [p.lower() for p in urlparse(url).path.split("/") if p]
            if len(parts) > 1 and parts[0] == "repos" and parts[1] == "alexseisler":
                owner = "alexseisler"
        except Exception:
            pass

        # Decide which token + scheme
        if owner == "alexseisler" and self.tokens["finegrained"]:
            token = self.tokens["finegrained"]
            scheme = "Bearer"  # fine-grained PATs expect Bearer
        else:
            token = self.tokens["classic"]
            scheme = "token"   # classic tokens expect token

        self.headers = self._build_headers(token, scheme)

        # 🔎 Debug logging
        print(f"[GITHUB API REQUEST] {method} {url}")
        print(f"[GITHUB API HEADERS] {self.headers}")

        try:
            response = requests.request(method, url, headers=self.headers, timeout=self.timeout, **kwargs)
            print(f"[GITHUB API STATUS] {response.status_code}")
            if response.status_code != 200:
                print(f"[GITHUB API BODY] {response.text}")
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"[GITHUB API ERROR] {method} {url} failed: {str(e)}")
            raise

    def get_repo_tree(self, owner, repo, branch=None, recursive=True, path_prefix=None, limit=None, offset=None):
        owner = owner.lower()
        repo = repo.lower()

        # ✅ Step 1: Resolve default branch if not provided
        if not branch:
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            repo_data = self._request("GET", repo_url)
            branch = repo_data.get("default_branch", "main")
            print(f"[INFO] Using default branch: {branch}")

        # ✅ Step 2: Resolve branch → SHA
        sha = None
        try:
            branch_url = f"{self.base_url}/repos/{owner}/{repo}/branches/{branch}"
            branch_data = self._request("GET", branch_url)
            sha = branch_data["commit"]["sha"]
        except Exception as e:
            print(f"[WARN] Branch lookup failed at /branches, falling back to /commits: {str(e)}")
            try:
                commit_url = f"{self.base_url}/repos/{owner}/{repo}/commits/{branch}"
                commit_data = self._request("GET", commit_url)
                sha = commit_data["sha"]
            except Exception as e2:
                print(f"[ERROR] Could not resolve branch {branch}: {str(e2)}")
                raise RuntimeError(f"Branch resolution failed for {branch}")

        if not sha:
            raise RuntimeError(f"Could not resolve branch {branch} to SHA")

        # ✅ Step 3: Fetch tree using SHA
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{sha}?recursive={1 if recursive else 0}"
        tree_data = self._request("GET", url)["tree"]

        # ✅ Step 4: Apply filters if needed
        if path_prefix:
            tree_data = [item for item in tree_data if item["path"].startswith(path_prefix)]
        if offset is not None and limit is not None:
            tree_data = tree_data[offset:offset+limit]

        return tree_data



# ✅ Route wrapper with detailed error logging
@router.get("/tree")
async def get_repo_tree(repo_id: str, branch: str = "main", recursive: bool = True, path_prefix: Optional[str] = ""):
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
