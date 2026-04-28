"""
Google OAuth 2.0 client configuration.

Uses authlib to build the consent URL and exchange authorization codes
for access tokens. All secrets are pulled from environment variables.
"""

import os
import logging

from authlib.integrations.starlette_client import OAuth

logger = logging.getLogger(__name__)

# Google's well-known OpenID Connect endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


def create_oauth() -> OAuth:
    """
    Build and return a configured authlib OAuth instance.
    Must be called AFTER dotenv is loaded so env vars are available.
    """
    oauth = OAuth()

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment."
        )

    oauth.register(
        name="google",
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url=GOOGLE_DISCOVERY_URL,
        client_kwargs={
            "scope": "openid email profile",
        },
    )

    return oauth
