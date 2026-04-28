"""
JWT creation and verification using python-jose.

Tokens are HS256-signed with a server-side secret.
Payload carries user_id, email, role, and a 24-hour expiry.
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError

logger = logging.getLogger(__name__)


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET environment variable is not set.")
    return secret


def _get_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


def create_access_token(user_id: str, email: str, role: str) -> str:
    """
    Sign a new JWT with a 24-hour expiry.

    Payload:
        sub   — user_id (UUID)
        email — user's email
        role  — 'admin' | 'viewer'
        exp   — expiry timestamp
        iat   — issued-at timestamp
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=24),
    }
    return jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT.

    Returns the payload dict on success, or None if the token is
    invalid, expired, or tampered with.
    """
    try:
        payload = jwt.decode(token, _get_secret(), algorithms=[_get_algorithm()])
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", exc)
        return None
