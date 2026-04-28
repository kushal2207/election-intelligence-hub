"""
main.py — FastAPI application entrypoint.

Environment variables required (set in .env or system environment):
  NEO4J_URI              e.g. bolt://localhost:7687
  NEO4J_USER             e.g. neo4j
  NEO4J_PASSWORD         e.g. your_password
  WEAVIATE_URL           e.g. https://my-cluster.weaviate.network
  WEAVIATE_API_KEY       e.g. xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  ANTHROPIC_API_KEY      e.g. sk-ant-xxxxxxxxxxxx
  GOOGLE_CLIENT_ID       e.g. xxxx.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET   e.g. GOCSPX-xxxxxxxx
  GOOGLE_REDIRECT_URI    e.g. http://localhost:8000/auth/callback
  JWT_SECRET             e.g. a long random string
  JWT_ALGORITHM           (optional, default HS256)
"""

import logging
import os
import warnings

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

warnings.filterwarnings("ignore", category=DeprecationWarning, module="authlib")

from routes.query import router as query_router
from routes.auth import router as auth_router
from services.neo4j_service import Neo4jService
from services.vector_service import VectorService
from services.llm_service import LLMService
from services.translation_service import TranslationService
from services.web_search_service import WebSearchService
from auth.google_oauth import create_oauth

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Required environment variable '{key}' is not set.")
    return value


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise and teardown heavy services once at startup/shutdown."""
    logger.info("Initialising services...")

    neo4j_uri = _require_env("NEO4J_URI")
    neo4j_user = _require_env("NEO4J_USER")
    neo4j_password = _require_env("NEO4J_PASSWORD")
    weaviate_url = _require_env("WEAVIATE_URL")
    weaviate_api_key = _require_env("WEAVIATE_API_KEY")
    groq_api_key = _require_env("GROQ_API_KEY")

    # --- Core services ---
    app.state.neo4j_service = Neo4jService(neo4j_uri, neo4j_user, neo4j_password)
    app.state.vector_service = VectorService(weaviate_url, weaviate_api_key)
    app.state.vector_service.create_collection()
    app.state.llm_service = LLMService(api_key=groq_api_key)
    app.state.translation_service = TranslationService(api_key=groq_api_key)
    app.state.web_search_service = WebSearchService()

    # --- Auth: Google OAuth ---
    app.state.oauth = create_oauth()
    app.state.google_redirect_uri = _require_env("GOOGLE_REDIRECT_URI")

    # --- Neo4j: ensure User node constraint exists ---
    try:
        app.state.neo4j_service._execute_query(
            "CREATE CONSTRAINT user_google_id_unique IF NOT EXISTS "
            "FOR (u:User) REQUIRE u.google_id IS UNIQUE"
        )
        app.state.neo4j_service._execute_query(
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS "
            "FOR (u:User) REQUIRE u.user_id IS UNIQUE"
        )
        logger.info("Neo4j User constraints ensured.")
    except Exception as exc:
        logger.warning("Could not create Neo4j User constraints (may already exist): %s", exc)

    logger.info("All services ready.")
    yield

    logger.info("Shutting down services...")
    app.state.neo4j_service.close()
    app.state.vector_service.close()
    logger.info("Neo4j and Weaviate connections closed.")


app = FastAPI(
    title="India Election Knowledge Graph Assistant",
    description="Async query orchestration over Neo4j + Weaviate with Claude synthesis and Google OAuth.",
    version="2.0.0",
    lifespan=lifespan,
)

# Session middleware required by authlib for OAuth state parameter storage
app.add_middleware(SessionMiddleware, secret_key=_require_env("JWT_SECRET"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.29.46:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(query_router, prefix="/api/v1", tags=["Query"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}
