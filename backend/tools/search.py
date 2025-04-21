"""Search tool implementation."""
from __future__ import annotations

from typing import Any, Dict, List

from duckduckgo_search import DDGS

def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Perform a DuckDuckGo text search and return a list of results."""
    with DDGS() as ddgs:
        results = ddgs.text(
            query,
            region="wt-wt",
            safesearch="moderate",
            timelimit="y",
            max_results=max_results,
        )
    return [
        {
            "title": r.get("title", "<no title>"),
            "url": r.get("href", "<no link>"),
            "snippet": r.get("body", ""),
        }
        for r in results
    ]

SEARCH_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query to send to DuckDuckGo.",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return (1‑25).",
            "default": 5,
            "minimum": 1,
            "maximum": 25,
        },
    },
    "required": ["query"],
}
