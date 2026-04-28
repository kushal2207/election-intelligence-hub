"""
Web search service — Uses DuckDuckGo Instant Answer API for free web search.
Falls back to a simple httpx-based scraper of DuckDuckGo HTML if the API
returns no results.
"""

import logging
import asyncio
import httpx
import re
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class WebSearchService:
    """
    Lightweight web search that queries DuckDuckGo for real-time information.
    No API key required.
    """

    def __init__(self):
        self.timeout = 8.0

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search the web for the given query and return a list of results.

        Each result dict has keys:
            - title: str
            - snippet: str
            - url: str (may be empty for instant answers)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._search_sync(query, max_results))

    def _search_sync(self, query: str, max_results: int) -> list[dict]:
        results = []

        # --- Strategy 1: DuckDuckGo Instant Answer API ---
        try:
            resp = httpx.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                timeout=self.timeout,
                follow_redirects=True,
            )
            if resp.status_code == 200:
                data = resp.json()

                # Abstract (main instant answer)
                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", ""),
                        "snippet": data["Abstract"],
                        "url": data.get("AbstractURL", ""),
                    })

                # Answer field (direct factual answers)
                if data.get("Answer"):
                    results.append({
                        "title": "Direct Answer",
                        "snippet": data["Answer"],
                        "url": "",
                    })

                # Related topics
                for topic in data.get("RelatedTopics", [])[:max_results]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:80],
                            "snippet": topic.get("Text", ""),
                            "url": topic.get("FirstURL", ""),
                        })

        except Exception as exc:
            logger.warning("DuckDuckGo API failed: %s", exc)

        # --- Strategy 2: DuckDuckGo HTML scrape fallback ---
        if len(results) < 2:
            try:
                html_results = self._scrape_ddg_html(query, max_results)
                results.extend(html_results)
            except Exception as exc:
                logger.warning("DuckDuckGo HTML scrape failed: %s", exc)

        # Deduplicate
        seen = set()
        unique = []
        for r in results[:max_results]:
            key = r["snippet"][:100]
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    def _scrape_ddg_html(self, query: str, max_results: int) -> list[dict]:
        """Scrape DuckDuckGo HTML search results as a fallback."""
        results = []
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            resp = httpx.get(url, headers=headers, timeout=self.timeout, follow_redirects=True)
            if resp.status_code == 200:
                html = resp.text
                # Extract result snippets using regex
                # DuckDuckGo HTML results are in <a class="result__a"> and <a class="result__snippet">
                titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html)
                snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html)
                urls = re.findall(r'class="result__url"[^>]*href="([^"]*)"', html)

                for i in range(min(len(titles), len(snippets), max_results)):
                    clean_title = re.sub(r'<[^>]+>', '', titles[i]).strip()
                    clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                    result_url = urls[i] if i < len(urls) else ""
                    if clean_snippet:
                        results.append({
                            "title": clean_title,
                            "snippet": clean_snippet,
                            "url": result_url,
                        })
        except Exception as exc:
            logger.warning("DDG HTML scrape error: %s", exc)

        return results
