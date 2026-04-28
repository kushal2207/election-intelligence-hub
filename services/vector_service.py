"""
services/vector_service.py

Weaviate-backed vector store for semantic search over election knowledge.

Requires env vars:
  WEAVIATE_URL     e.g. https://my-cluster.weaviate.network
  WEAVIATE_API_KEY e.g. xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Collection schema
-----------------
Name       : ElectionKnowledge
Vectorizer : none  (we supply pre-computed vectors from sentence-transformers)
Properties :
  text            (text)    – raw source text
  type            (text)    – e.g. "act_section" | "event" | "candidate"
  jurisdiction_id (text)    – UUID of the Jurisdiction node
  act_id          (text)    – UUID of the Election_Act node (nullable)
  language        (text)    – BCP-47 language code, e.g. "en", "hi"
"""

from __future__ import annotations

import logging
import os
from typing import Any

import weaviate
import weaviate.classes as wvc
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "ElectionKnowledge"
_MODEL_NAME = "all-MiniLM-L6-v2"

# ──────────────────────────────────────────────────────────────────────────────
# Helper: property definitions (shared between create & guard-check)
# ──────────────────────────────────────────────────────────────────────────────
_PROPERTY_DEFS = [
    wvc.config.Property(name="text",            data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="type",            data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="jurisdiction_id", data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="act_id",          data_type=wvc.config.DataType.TEXT),
    wvc.config.Property(name="language",        data_type=wvc.config.DataType.TEXT),
]


class VectorService:
    """Thin async-friendly wrapper around Weaviate v4 Python client."""

    def __init__(self, url: str, api_key: str) -> None:
        """
        Connect to Weaviate and warm up the embedding model.

        Args:
            url:     Full Weaviate cluster URL (e.g. https://…weaviate.network)
            api_key: Weaviate API key (for Weaviate Cloud / Serverless)
        """
        auth = weaviate.auth.AuthApiKey(api_key=api_key)
        self._client = weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=auth,
        )
        logger.info("Connected to Weaviate at %s", url)

        # Load embedding model once at startup (cached on disk after first run)
        logger.info("Loading sentence-transformer model '%s' …", _MODEL_NAME)
        self._model = SentenceTransformer(_MODEL_NAME)
        logger.info("Embedding model ready.")

    # ──────────────────────────────────────────────────────────────────────────
    # Collection management
    # ──────────────────────────────────────────────────────────────────────────

    def create_collection(self) -> None:
        """
        Create the 'ElectionKnowledge' collection if it does not already exist.
        Idempotent – safe to call every time the app starts.
        """
        if self._client.collections.exists(_COLLECTION_NAME):
            logger.info("Collection '%s' already exists – skipping creation.", _COLLECTION_NAME)
            return

        self._client.collections.create(
            name=_COLLECTION_NAME,
            # We supply our own vectors, so no Weaviate-side vectorizer needed
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            properties=_PROPERTY_DEFS,
        )
        logger.info("Collection '%s' created successfully.", _COLLECTION_NAME)

    # ──────────────────────────────────────────────────────────────────────────
    # Write
    # ──────────────────────────────────────────────────────────────────────────

    def upsert_vector(
        self,
        id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        """
        Embed *text* and upsert (insert-or-replace) one object into Weaviate.

        Args:
            id:       Deterministic UUID string (e.g. the Act_Section UUID from Neo4j)
            text:     Source text to embed
            metadata: Dict with keys: type, jurisdiction_id, act_id, language
                      Any missing key is stored as an empty string.
        """
        vector: list[float] = self._model.encode(text).tolist()

        properties = {
            "text":            text,
            "type":            metadata.get("type", ""),
            "jurisdiction_id": metadata.get("jurisdiction_id", ""),
            "act_id":          metadata.get("act_id", ""),
            "language":        metadata.get("language", "en"),
        }

        collection = self._client.collections.get(_COLLECTION_NAME)

        # Weaviate v4: use uuid parameter for deterministic IDs
        collection.data.insert(
            properties=properties,
            vector=vector,
            uuid=id,
        )
        logger.debug("Upserted vector for id=%s", id)

    # ──────────────────────────────────────────────────────────────────────────
    # Read
    # ──────────────────────────────────────────────────────────────────────────

    def semantic_search(
        self,
        query_text: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Embed *query_text* and perform a nearest-neighbour search.

        Returns:
            A list of up to *top_k* dicts, each containing:
              - text, type, jurisdiction_id, act_id, language  (stored properties)
              - score  (certainty distance, higher = more relevant)
              - id     (Weaviate UUID)
        """
        query_vector: list[float] = self._model.encode(query_text).tolist()

        collection = self._client.collections.get(_COLLECTION_NAME)

        response = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_metadata=wvc.query.MetadataQuery(certainty=True, distance=True),
        )

        results = []
        for obj in response.objects:
            results.append({
                "id":              str(obj.uuid),
                "text":            obj.properties.get("text", ""),
                "type":            obj.properties.get("type", ""),
                "jurisdiction_id": obj.properties.get("jurisdiction_id", ""),
                "act_id":          obj.properties.get("act_id", ""),
                "language":        obj.properties.get("language", "en"),
                "score":           obj.metadata.certainty if obj.metadata else None,
            })

        logger.debug("semantic_search returned %d results for query='%s'", len(results), query_text[:60])
        return results

    # ──────────────────────────────────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    def close(self) -> None:
        """Gracefully close the Weaviate connection."""
        self._client.close()
        logger.info("Weaviate client closed.")
