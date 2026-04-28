"""
FastAPI dependency that extracts and verifies the Bearer JWT
from the Authorization header. Attaches the decoded user payload
to request.state.user for downstream handlers.
"""

import logging
from typing import Optional

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.jwt_handler import decode_access_token

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> dict:
    """
    Core auth dependency.

    Extracts the Bearer token, decodes it, and returns the user payload dict.
    Raises HTTP 401 if the token is missing, malformed, or expired.
    """
    # FastAPI's Depends does not inject HTTPBearer automatically when
    # the dependency is used via Depends(get_current_user), so we
    # also read the header manually as a fallback.
    token: Optional[str] = None

    if credentials and credentials.credentials:
        token = credentials.credentials
    else:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Attach to request.state for logging / audit trail access
    request.state.user = payload
    return payload
