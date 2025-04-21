"""MCP‑style tool implementations and JSON schemas."""
from __future__ import annotations

from typing import Dict, List, Any

# Import all tools and their schemas
from .search import search, SEARCH_PARAMS_SCHEMA
from .wiki import wiki_search, WIKI_PARAMS_SCHEMA
from .weather import get_weather, WEATHER_PARAMS_SCHEMA
from .calculator import calculator, CALCULATOR_PARAMS_SCHEMA
from .pretty_print import (
    pretty_print_search_results,
    pretty_print_wiki_results,
    pretty_print_weather_results,
    pretty_print_calculator_results
)

# Tool registry used by LM Studio
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Perform a web search and return the top results.",
            "parameters": SEARCH_PARAMS_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wiki_search",
            "description": "Search Wikipedia and return summaries of relevant articles.",
            "parameters": WIKI_PARAMS_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information and forecast for a location.",
            "parameters": WEATHER_PARAMS_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a Python expression using math, numpy, and sympy libraries.",
            "parameters": CALCULATOR_PARAMS_SCHEMA,
        },
    },
]

TOOL_IMPLS = {
    "search": search,
    "wiki_search": wiki_search,
    "get_weather": get_weather,
    "calculator": calculator,
}

# Export all the necessary components
__all__ = [
    "TOOLS",
    "TOOL_IMPLS",
    "search",
    "wiki_search",
    "get_weather",
    "calculator",
    "pretty_print_search_results",
    "pretty_print_wiki_results",
    "pretty_print_weather_results",
    "pretty_print_calculator_results",
    "SEARCH_PARAMS_SCHEMA",
    "WIKI_PARAMS_SCHEMA",
    "WEATHER_PARAMS_SCHEMA",
    "CALCULATOR_PARAMS_SCHEMA",
]
