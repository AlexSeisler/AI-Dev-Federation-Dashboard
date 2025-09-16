# server/debug.py
import logging
import traceback
import os
from fastapi import APIRouter, Query, Depends
from server.jwt_utils import decode_token, oauth2_scheme

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Setup logger
logger = logging.getLogger("debug")
logger.setLevel(logging.DEBUG)

# File handler (UTF-8 safe)
fh = logging.FileHandler("logs/debug.log", encoding="utf-8")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

# Console handler (force UTF-8 safe)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

# Force UTF-8 encoding for console too
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass  # fallback for older Python versions

logger.addHandler(ch)

router = APIRouter(prefix="/auth", tags=["debug"])


def debug_log(message: str, exc: Exception | None = None, context: dict | None = None):
    """Compact debug logging with optional traceback + structured context."""
    if exc:
        logger.error(f"{message} | {type(exc).__name__}: {exc}")
        logger.debug("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    else:
        logger.info(message)

    if context:
        logger.debug(f"Context: {context}")


@router.get("/debug")
async def debug_token(
    token: str = Query(None),
    bearer: str = Depends(oauth2_scheme),
):
    final_token = token or bearer
    if not final_token:
        return {"valid": False, "reason": "No token provided"}

    try:
        payload = decode_token(final_token)
        debug_log("JWT decode success", context=payload)
        return {"valid": True, "payload": payload}
    except Exception as e:
        debug_log("JWT decode failed", e)
        return {"valid": False, "reason": str(e)}
