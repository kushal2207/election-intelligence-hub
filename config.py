from pydantic import BaseModel, Field, validator
from pydantic.v1 import ValidationError
from typing import Optional
import os

class Settings(BaseModel):
    """
    Loads and validates all required environment variables for the application.
    All required fields must be set in the environment or .env file.
    """

    # --- Database/Services ---
    neo4j_uri: str = Field(..., description="Neo4j connection URI.")
    neo4j_user: str = Field(..., description="Neo4j username.")
    neo4j_password: str = Field(..., description="Neo4j password.")
    weaviate_url: str = Field(..., description="Weaviate cluster URL.")
    weaviate_api_key: str = Field(..., description="Weaviate API key.")
    anthropic_api_key: str = Field(..., description="Anthropic API key for LLM and Translation services.")

    # --- Auth ---
    google_client_id: str = Field(..., alias="GOOGLE_CLIENT_ID", description="Google Client ID for OAuth.")
    google_client_secret: str = Field(..., alias="GOOGLE_CLIENT_SECRET", description="Google Client Secret for OAuth.")
    google_redirect_uri: str = Field(..., alias="GOOGLE_REDIRECT_URI", description="Google OAuth redirect URI.")
    jwt_secret: str = Field(..., alias="JWT_SECRET", description="JWT signing secret.")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM", description="JWT signing algorithm.")

    @validator('*', pre=True)
    def check_required_env(cls, v):
        """Validator to ensure that all fields defined in the class are provided."""
        if v is None:
            raise ValueError(f"Missing required environment variable for {cls.__name__}.")
        return v

# Instantiate and validate the settings object once at runtime
# This acts as the single source of truth for environment configuration.
try:
    settings = Settings(_settings_file_config=True)
except ValidationError as e:
    # This exception is caught by the calling code (main.py)
    settings = None
    print(f"FATAL CONFIG ERROR: Could not load settings. Check your .env file and ensure all variables are present. Details: {e}")

# Helper function to safely access settings
def get_settings() -> Optional[Settings]:
    return settings