"""
Role-based access control guards.

Usage in routes:
    @router.get("/admin/dashboard", dependencies=[Depends(require_admin)])
    async def dashboard(): ...

    @router.post("/query", dependencies=[Depends(require_viewer)])
    async def query(): ...
"""

import logging

from fastapi import Depends, HTTPException, status

from auth.middleware import get_current_user

logger = logging.getLogger(__name__)


async def require_viewer(user: dict = Depends(get_current_user)) -> dict:
    """
    Allow access if the authenticated user has role 'viewer' OR 'admin'.
    Admins are a superset of viewers.
    """
    if user.get("role") not in ("viewer", "admin"):
        logger.warning("Access denied for user %s with role '%s'.", user.get("sub"), user.get("role"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Viewer role required.",
        )
    return user


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    Allow access only if the authenticated user has role 'admin'.
    """
    if user.get("role") != "admin":
        logger.warning("Admin access denied for user %s with role '%s'.", user.get("sub"), user.get("role"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required.",
        )
    return user
