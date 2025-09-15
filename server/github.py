from fastapi import APIRouter, HTTPException
from typing import Optional
from server.github_service import GitHubService

router = APIRouter(prefix="/repo", tags=["GitHub"])
github_service = GitHubService()


def parse_repo_id(repo_id: str):
    """
    Split 'owner/repo' into (owner, repo).
    Example: 'AlexSeisler/AI-Dev-Federation-Dashboard'
    """
    try:
        owner, repo = repo_id.split("/")
        return owner, repo
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repo_id format. Use 'owner/repo'.")


# -------------------------------------------------
# 1️⃣ Repo Tree
# -------------------------------------------------
# server/github.py
@router.get("/tree")
async def get_repo_tree(repo_id: str, branch: str = "main", recursive: bool = True, path_prefix: Optional[str] = ""):
    try:
        owner, repo = parse_repo_id(repo_id)
        result = github_service.get_repo_tree(owner, repo, branch, recursive, path_prefix)
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] get_repo_tree failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve repo tree: {str(e)}")



# -------------------------------------------------
# 2️⃣ File Content
# -------------------------------------------------
@router.get("/file")
async def get_file_content(
    repo_id: str,
    file_path: str,
    branch: str = "main",
    start_line: int = 1,
    chunk_size: Optional[int] = None
):
    try:
        owner, repo = parse_repo_id(repo_id)
        result = github_service.get_file(
            owner,
            repo,
            file_path,
            branch,
            start_line=start_line,
            chunk_size=chunk_size
        )
        return result
    except Exception as e:
        print(f"[ERROR] get_file_content failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file content")
