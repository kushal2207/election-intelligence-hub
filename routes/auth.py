"""
Authentication routes — Google OAuth 2.0 flow.

GET  /auth/google    → redirect user to Google consent screen
GET  /auth/callback  → receive code, exchange for token, MERGE user in Neo4j, return JWT
"""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
import json
import urllib.parse

from auth.jwt_handler import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Neo4j user MERGE helper
# ---------------------------------------------------------------------------

async def _merge_user(neo4j_svc, google_id: str, email: str, name: str, picture: str) -> dict:
    """
    MERGE on google_id so first login creates the node and subsequent
    logins only update last_login. Returns the full user record.
    """
    loop = asyncio.get_event_loop()

    query = """
    MERGE (u:User {google_id: $google_id})
    ON CREATE SET
        u.user_id     = $user_id,
        u.email       = $email,
        u.name        = $name,
        u.picture     = $picture,
        u.role        = 'viewer',
        u.created_at  = datetime(),
        u.last_login  = datetime()
    ON MATCH SET
        u.email       = $email,
        u.name        = $name,
        u.picture     = $picture,
        u.last_login  = datetime()
    RETURN u.user_id   AS user_id,
           u.email     AS email,
           u.name      AS name,
           u.picture   AS picture,
           u.role      AS role
    """

    params = {
        "google_id": google_id,
        "user_id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "picture": picture,
    }

    result = await loop.run_in_executor(
        None, lambda: neo4j_svc._execute_query(query, params)
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create or retrieve user in Neo4j.",
        )

    return result[0]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/google")
async def login_via_google(request: Request):
    """
    Step 1: Build Google consent URL and redirect the user.
    Uses the request's host so that it works from both localhost and LAN IPs.
    """
    oauth = request.app.state.oauth
    # Dynamically build redirect URI based on the incoming request host
    request_host = request.headers.get("host", "localhost:8000")
    redirect_uri = f"http://{request_host}/auth/callback"
    logger.info("OAuth redirect_uri: %s", redirect_uri)

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(request: Request):
    """
    Step 2–4:
      - Exchange authorization code for access token
      - Fetch Google user profile
      - MERGE user in Neo4j
      - Sign and return JWT
    """
    oauth = request.app.state.oauth

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as exc:
        logger.error("Google token exchange failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {exc}",
        )

    # Extract user info from the ID token (OpenID Connect)
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not retrieve user info from Google.",
        )

    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name", "")
    picture = user_info.get("picture", "")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google profile missing required fields (sub, email).",
        )

    # MERGE into Neo4j
    neo4j_svc = request.app.state.neo4j_service
    user_record = await _merge_user(neo4j_svc, google_id, email, name, picture)

    # Sign JWT
    access_token = create_access_token(
        user_id=user_record["user_id"],
        email=user_record["email"],
        role=user_record["role"],
    )

    # Dynamically resolve frontend host from the request so LAN access works
    request_host = request.headers.get("host", "localhost:8000").split(":")[0]
    frontend_url = f"http://{request_host}:5173/login"
    user_json = json.dumps({
        "user_id": user_record["user_id"],
        "email": user_record["email"],
        "name": user_record["name"],
        "role": user_record["role"],
        "picture": user_record["picture"],
    })
    
    url = f"{frontend_url}?token={access_token}&user={urllib.parse.quote(user_json)}"
    return RedirectResponse(url=url)
