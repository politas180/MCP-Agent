"""Wikipedia search tool implementation."""
from __future__ import annotations

from typing import Any, Dict, List

import wikipedia

def wiki_search(query: str, max_results: int = 3, sentences: int = 3) -> Dict[str, Any]:
    """Search Wikipedia and return a summary of the top results."""
    try:
        # Search for Wikipedia pages
        search_results = wikipedia.search(query, results=max_results)

        if not search_results:
            return {"status": "no_results", "message": f"No Wikipedia results found for '{query}'"}

        results = []
        for title in search_results:
            try:
                # Get the page for each result
                page = wikipedia.page(title, auto_suggest=False)
                # Get a summary with specified number of sentences
                summary = wikipedia.summary(title, sentences=sentences, auto_suggest=False)

                results.append({
                    "title": page.title,
                    "url": page.url,
                    "summary": summary
                })
            except (wikipedia.exceptions.DisambiguationError,
                    wikipedia.exceptions.PageError,
                    wikipedia.exceptions.WikipediaException) as e:
                # Skip problematic pages but continue with others
                continue

        return {
            "status": "success",
            "query": query,
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

WIKI_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query to send to Wikipedia.",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of Wikipedia pages to return.",
            "default": 3,
            "minimum": 1,
            "maximum": 10,
        },
        "sentences": {
            "type": "integer",
            "description": "Number of sentences to include in each summary.",
            "default": 3,
            "minimum": 1,
            "maximum": 10,
        }
    },
    "required": ["query"],
}
