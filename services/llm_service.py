import logging
from groq import Groq

logger = logging.getLogger(__name__)

# System prompt that primes the LLM for election law synthesis
_SYSTEM_PROMPT = """You are an expert AI assistant specializing in Indian elections, politics, and governance.
You have access to multiple data sources:
1. A knowledge graph with structured election law data (graph_context)
2. Semantically retrieved legal text from a vector database (vector_context)
3. Real-time web search results (web_context)

Your job is to synthesise ALL available data into a clear, accurate, helpful answer for the user.

Rules:
- Use knowledge graph and vector data when available for election law questions.
- Use web search results to answer general knowledge, political, and current affairs questions.
- If both graph data and web data are available, prefer graph data for legal accuracy but supplement with web data for context.
- If a conflict is flagged between data sources, explicitly acknowledge it in your answer.
- Always give a direct, helpful answer. Never say "I don't have information" if web results are available.
- Respond in plain prose; use bullet points only when they genuinely improve clarity.
- Tailor the complexity of the language to a general public audience.
- When citing web sources, mention the source naturally (e.g. "According to...").
- For factual questions (who is PM, what are election dates, etc.), give a direct answer first, then elaborate."""


class LLMService:
    """
    Synthesis layer using the Groq API (OpenAI-compatible).
    Accepts structured graph + vector + web context and returns a synthesised answer string.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_tokens = 1024

    async def synthesize(
        self,
        query_text: str,
        graph_context: dict,
        vector_context: list,
        conflict_detected: bool,
        web_context: list | None = None,
    ) -> tuple[str, str]:
        """
        Call the Groq API to generate a final answer.

        Returns:
            (answer_text, confidence)  where confidence is 'high' | 'medium' | 'low'
        """
        graph_str = _format_graph_context(graph_context)
        vector_str = _format_vector_context(vector_context)
        web_str = _format_web_context(web_context)

        conflict_note = (
            "\n\n⚠️  CONFLICT ALERT: One or more data sources disagree. "
            "Reflect this uncertainty clearly in your answer."
            if conflict_detected
            else ""
        )

        user_message = (
            f"User question: {query_text}\n\n"
            f"--- Graph Context ---\n{graph_str}\n\n"
            f"--- Retrieved Legal Text ---\n{vector_str}\n\n"
            f"--- Web Search Results ---\n{web_str}"
            f"{conflict_note}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )
            answer = response.choices[0].message.content.strip()
            confidence = _estimate_confidence(graph_context, vector_context, conflict_detected, web_context)
            return answer, confidence

        except Exception as exc:
            logger.error("Groq API error: %s", exc)
            raise


def _format_graph_context(ctx: dict) -> str:
    if not ctx:
        return "No graph data available."
    lines = []
    for key, value in ctx.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _format_vector_context(results: list) -> str:
    if not results:
        return "No relevant legal text retrieved."
    snippets = []
    for i, hit in enumerate(results, start=1):
        meta = hit.get("metadata", {})
        text = meta.get("text", "")
        act_id = meta.get("act_id", "unknown act")
        snippets.append(f"[{i}] ({act_id}): {text}")
    return "\n".join(snippets)


def _format_web_context(results: list | None) -> str:
    if not results:
        return "No web search results available."
    snippets = []
    for i, hit in enumerate(results, start=1):
        title = hit.get("title", "")
        snippet = hit.get("snippet", "")
        url = hit.get("url", "")
        source_line = f" (Source: {url})" if url else ""
        snippets.append(f"[Web {i}] {title}: {snippet}{source_line}")
    return "\n".join(snippets)


def _estimate_confidence(graph_ctx: dict, vector_results: list, conflict: bool, web_results: list | None = None) -> str:
    if conflict:
        return "low"
    has_graph = bool(graph_ctx and graph_ctx.get("affected_sections"))
    has_vector = bool(vector_results)
    has_web = bool(web_results)
    if has_graph and has_vector:
        return "high"
    if has_graph or has_vector:
        return "medium"
    if has_web:
        return "medium"
    return "low"
