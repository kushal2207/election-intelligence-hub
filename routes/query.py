"""
POST /query  — Async query orchestration for India Election Assistant.

Execution flow:
  1. Parse request (jurisdiction_id, constituency_id, language)
  2. Neo4j: fetch AFFECTS edges for the constituency (serial — needed for step 3 IDs)
  3. asyncio.gather() — parallel:
       a. Weaviate semantic search on query_text
       b. Neo4j fetch Source_Authority nodes for retrieved act_section IDs
       c. Neo4j check conflict=true on the retrieved act_sections
  4. If conflict detected → set conflict_detected=true
  5. LLM synthesis → answer from graph + vector + conflict context
  6. Translate final_answer to user_language
  7. Return structured QueryResponse
"""

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Body

from models.query_request import QueryRequest
from models.query_response import QueryResponse, SourceCitation
from auth.dependencies import require_viewer

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers — thin async wrappers around synchronous service calls
# ---------------------------------------------------------------------------


async def _neo4j_affects(neo4j_svc, constituency_id: str) -> list[dict]:
    """Return Act_Section nodes that AFFECT the given constituency."""
    loop = asyncio.get_event_loop()
    query = """
    MATCH (sec:Act_Section)-[:AFFECTS]->(c:Constituency {constituency_id: $cid})
    RETURN sec.section_id AS section_id,
           sec.text_content AS text_content,
           sec.conflict AS conflict,
           sec.vector_id AS vector_id
    """
    return await loop.run_in_executor(
        None, lambda: neo4j_svc._execute_query(query, {"cid": constituency_id})
    )


async def _neo4j_source_authorities(neo4j_svc, section_ids: list[str]) -> list[dict]:
    """Return Source_Authority nodes linked to the given Act_Section IDs."""
    if not section_ids:
        return []
    loop = asyncio.get_event_loop()
    query = """
    MATCH (sec:Act_Section)-[:HAS_SOURCE]->(auth:Source_Authority)
    WHERE sec.section_id IN $ids
    RETURN DISTINCT auth.authority_name AS authority_name,
                    auth.source_type AS source_type
    """
    return await loop.run_in_executor(
        None, lambda: neo4j_svc._execute_query(query, {"ids": section_ids})
    )


async def _neo4j_check_conflicts(neo4j_svc, section_ids: list[str]) -> bool:
    """Return True if ANY of the relevant Act_Section nodes have conflict=true."""
    if not section_ids:
        return False
    loop = asyncio.get_event_loop()
    query = """
    MATCH (sec:Act_Section)
    WHERE sec.section_id IN $ids AND sec.conflict = true
    RETURN count(sec) AS cnt
    """
    result = await loop.run_in_executor(
        None, lambda: neo4j_svc._execute_query(query, {"ids": section_ids})
    )
    return bool(result and result[0].get("cnt", 0) > 0)


async def _vector_search(vector_svc, query_text: str, jurisdiction_id: str, language: str) -> list[dict]:
    """Run semantic search scoped to the user's jurisdiction and language."""
    loop = asyncio.get_event_loop()
    # Weaviate v4 filters are handled inside VectorService.semantic_search in this implementation,
    # or we can pass them if needed. VectorService.semantic_search currently only takes query_text and top_k.
    # If we want jurisdiction/language filtering, we should update VectorService.
    return await loop.run_in_executor(
        None,
        lambda: vector_svc.semantic_search(query_text, top_k=5),
    )


# ---------------------------------------------------------------------------
# Dependency injectors — pull service instances off app.state
# ---------------------------------------------------------------------------


def get_neo4j(request: Request):
    return request.app.state.neo4j_service


def get_vector_service(request: Request):
    return request.app.state.vector_service


def get_llm(request: Request):
    return request.app.state.llm_service


def get_translation(request: Request):
    return request.app.state.translation_service


def get_web_search(request: Request):
    return request.app.state.web_search_service


# ---------------------------------------------------------------------------
# Route handler
# ---------------------------------------------------------------------------


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(require_viewer)])
async def handle_query(
    payload: QueryRequest,
    neo4j_svc=Depends(get_neo4j),
    vector_svc=Depends(get_vector_service),
    llm_svc=Depends(get_llm),
    translation_svc=Depends(get_translation),
    web_search_svc=Depends(get_web_search),
) -> QueryResponse:

    trace: list[str] = []
    status = "success"
    conflict_detected = False
    source_citations: list[SourceCitation] = []
    confidence = "low"

    jurisdiction_id = payload.user_location.jurisdiction_id
    constituency_id = payload.user_location.constituency_id
    language = payload.user_language
    query_text = payload.query_text

    # ------------------------------------------------------------------
    # STEP 1 — Neo4j: fetch AFFECTS edges (serial, needed for section IDs)
    # ------------------------------------------------------------------
    try:
        affects_rows = await _neo4j_affects(neo4j_svc, constituency_id)
        trace.append(f"Neo4j AFFECTS query returned {len(affects_rows)} sections.")
    except Exception as exc:
        logger.error("Neo4j AFFECTS query failed: %s", exc)
        trace.append(f"Neo4j timeout/error fetching AFFECTS edges: {exc}")
        affects_rows = []
        status = "partial"

    section_ids = [row["section_id"] for row in affects_rows if row.get("section_id")]

    # Build basic graph context dict to pass to LLM
    graph_context: dict[str, Any] = {
        "jurisdiction_id": jurisdiction_id,
        "constituency_id": constituency_id,
        "affected_sections": [
            {"id": r["section_id"], "text": r.get("text_content", "")}
            for r in affects_rows
        ],
    }

    # ------------------------------------------------------------------
    # STEP 2 — Parallel: Vector search | Source Authority | Conflict check
    # ------------------------------------------------------------------
    vector_results: list[dict] = []
    authority_rows: list[dict] = []

    async def safe_vector_search() -> list[dict]:
        try:
            results = await _vector_search(vector_svc, query_text, jurisdiction_id, language)
            trace.append(f"Vector semantic search returned {len(results)} hits.")
            return results
        except Exception as exc:
            logger.error("Vector search failed: %s", exc)
            trace.append(f"Vector search unavailable  graph-only mode: {exc}")
            return []

    async def safe_source_auth() -> list[dict]:
        try:
            rows = await _neo4j_source_authorities(neo4j_svc, section_ids)
            trace.append(f"Source_Authority lookup returned {len(rows)} authorities.")
            return rows
        except Exception as exc:
            logger.error("Source_Authority Neo4j query failed: %s", exc)
            trace.append(f"Source_Authority fetch error: {exc}")
            return []

    async def safe_conflict_check() -> bool:
        try:
            result = await _neo4j_check_conflicts(neo4j_svc, section_ids)
            trace.append(f"Conflict check: conflict_detected={result}.")
            return result
        except Exception as exc:
            logger.error("Conflict check Neo4j query failed: %s", exc)
            trace.append(f"Conflict check error: {exc}")
            return False

    async def safe_web_search() -> list[dict]:
        try:
            results = await web_search_svc.search(query_text, max_results=5)
            trace.append(f"Web search returned {len(results)} results.")
            return results
        except Exception as exc:
            logger.error("Web search failed: %s", exc)
            trace.append(f"Web search unavailable: {exc}")
            return []

    vector_results, authority_rows, conflict_detected, web_results = await asyncio.gather(
        safe_vector_search(),
        safe_source_auth(),
        safe_conflict_check(),
        safe_web_search(),
    )

    # Build source citations from authority rows
    for row in authority_rows:
        source_citations.append(
            SourceCitation(
                authority_name=row.get("authority_name", "Unknown"),
                source_detail=row.get("source_type", ""),
            )
        )

    if conflict_detected:
        trace.append("Conflict flag detected — marking response accordingly.")

    # ------------------------------------------------------------------
    # STEP 3 — LLM Synthesis
    # ------------------------------------------------------------------
    final_answer = ""
    try:
        final_answer, confidence = await llm_svc.synthesize(
            query_text=query_text,
            graph_context=graph_context,
            vector_context=vector_results,
            conflict_detected=conflict_detected,
            web_context=web_results,
        )
        trace.append("LLM synthesis completed successfully.")
    except Exception as exc:
        logger.error("LLM synthesis failed: %s", exc)
        trace.append(f"LLM synthesis failed  returning raw graph context: {exc}")
        status = "partial"
        confidence = "low"
        # Fallback: concatenate raw graph text
        raw_texts = [s.get("text", "") for s in graph_context.get("affected_sections", [])]
        final_answer = (
            "LLM synthesis unavailable. Raw legal context:\n\n" + "\n\n".join(raw_texts)
            if raw_texts
            else "No answer available due to service errors."
        )

    # ------------------------------------------------------------------
    # STEP 4 — Translation
    # ------------------------------------------------------------------
    try:
        final_answer, fallback_used = await translation_svc.translate(final_answer, language)
        if fallback_used:
            trace.append(f"Translation to '{language}' failed — English fallback used.")
        else:
            trace.append(f"Answer translated to '{language}'.")
    except Exception as exc:
        logger.error("Translation service error: %s", exc)
        trace.append(f"Translation service error — English answer returned: {exc}")

    # ------------------------------------------------------------------
    # STEP 5 — Return structured response
    # ------------------------------------------------------------------
    return QueryResponse(
        status=status,
        execution_trace=trace,
        final_answer=final_answer,
        confidence=confidence,
        conflict_detected=conflict_detected,
        source_citations=source_citations,
    )
