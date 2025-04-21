"""Thin wrapper around LM Studio's OpenAI‑compatible HTTP API."""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List

import requests

from config import LMSTUDIO_HOST, LMSTUDIO_MODEL, MAX_MODEL_TOKENS, TEMPERATURE
from tools import TOOLS
from computer_use import COMPUTER_TOOLS

__all__ = ["llm_call"]


def clean_llm_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Clean up problematic LLM responses."""
    # Clean up content if present
    if "content" in response and response["content"]:
        # Remove any special tokens that might appear in the response
        content = response["content"]
        # Remove special tokens like <|im_start|>, <|im_end|>, etc.
        content = re.sub(r'<\|im_(start|end)\|>', '', content)
        # Remove any repeated newlines (more than 2)
        content = re.sub(r'\n{3,}', '\n\n', content)
        # Trim whitespace
        content = content.strip()
        response["content"] = content

    return response

def llm_call(messages: List[Dict[str, Any]], max_retries: int = 2, computer_use_mode: bool = False) -> Dict[str, Any]:
    """Send a chat/completions request and return the assistant message.

    Args:
        messages: List of message objects to send to the LLM
        max_retries: Maximum number of retries on failure

    Returns:
        The assistant's response message
    """
    # Ensure the messages are properly formatted
    cleaned_messages = []
    for msg in messages:
        # Create a new copy of the message
        cleaned_msg = {"role": msg["role"]}

        # Clean up content if present
        if "content" in msg and msg["content"]:
            cleaned_msg["content"] = msg["content"]
        else:
            cleaned_msg["content"] = None

        # Add tool_calls if present
        if "tool_calls" in msg:
            cleaned_msg["tool_calls"] = msg["tool_calls"]

        # Add tool_call_id if present
        if "tool_call_id" in msg:
            cleaned_msg["tool_call_id"] = msg["tool_call_id"]

        cleaned_messages.append(cleaned_msg)

    # Try the request with retries
    retries = 0
    last_error = None

    while retries <= max_retries:
        try:
            # If this is a retry, slightly adjust the temperature to get a different response
            temp_adjustment = 0.05 * retries
            current_temp = max(0.1, min(0.9, TEMPERATURE + temp_adjustment))

            # Select the appropriate tools based on mode
            tools_to_use = COMPUTER_TOOLS if computer_use_mode else TOOLS

            resp = requests.post(
                f"{LMSTUDIO_HOST}/v1/chat/completions",
                json={
                    "model": LMSTUDIO_MODEL,
                    "messages": cleaned_messages,
                    "tools": tools_to_use,
                    "stream": False,
                    "max_tokens": MAX_MODEL_TOKENS,
                    "temperature": current_temp,
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            response = data["choices"][0]["message"]  # type: ignore[index]

            # Check if the response has problematic tokens
            if "content" in response and response["content"] and "<|im_" in response["content"]:
                print(f"Detected problematic tokens in response, retrying ({retries+1}/{max_retries+1})")
                retries += 1
                if retries > max_retries:
                    break
                continue

            # Clean up the response
            return clean_llm_response(response)

        except Exception as e:
            last_error = e
            print(f"Error in LLM call (attempt {retries+1}/{max_retries+1}): {e}")
            retries += 1
            if retries <= max_retries:
                # Wait a bit before retrying
                time.sleep(1)
            else:
                break

    # If we get here, all retries failed
    print(f"All {max_retries+1} attempts failed. Last error: {last_error}")
    return {
        "role": "assistant",
        "content": "I'm sorry, I encountered an error processing your request. Please try again."
    }
