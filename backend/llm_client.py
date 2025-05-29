"""Thin wrapper around Ollama's Python API."""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List

import ollama

from config import OLLAMA_HOST, OLLAMA_MODEL, DEFAULT_MAX_MODEL_TOKENS, DEFAULT_TEMPERATURE
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

def llm_call(messages: List[Dict[str, Any]], max_retries: int = 2, computer_use_mode: bool = False, temperature: float | None = None, max_tokens: int | None = None) -> Dict[str, Any]:
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
    
    # Initialize Ollama client
    client = ollama.Client(host=OLLAMA_HOST)

    while retries <= max_retries:
        try:
            # If this is a retry, slightly adjust the temperature to get a different response
            temp_adjustment = 0.05 * retries
            final_temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE
            final_max_tokens = max_tokens if max_tokens is not None else DEFAULT_MAX_MODEL_TOKENS
            current_temp = max(0.1, min(0.9, final_temperature + temp_adjustment))

            # Select the appropriate tools based on mode
            tools_to_use = COMPUTER_TOOLS if computer_use_mode else TOOLS

            # Change stream to True to enable streaming responses
            stream_response = client.chat(
                model=OLLAMA_MODEL,
                messages=cleaned_messages,
                tools=tools_to_use,
                stream=True,
                options={
                    'num_predict': final_max_tokens,
                    'temperature': current_temp,
                }
            )
            
            # Initialize variables to aggregate the response
            aggregated_content = ""
            aggregated_tool_calls = []
            role = "assistant"  # The role will always be 'assistant'
            
            # Iterate through the streamed response chunks
            for chunk in stream_response:
                # Extract the message from the chunk
                chunk_message = chunk.message
                
                # Aggregate content
                if hasattr(chunk_message, 'content') and chunk_message.content:
                    aggregated_content += chunk_message.content
                
                # Aggregate tool calls
                if hasattr(chunk_message, 'tool_calls') and chunk_message.tool_calls:
                    # Add any new tool calls to our aggregated list
                    for tool_call in chunk_message.tool_calls:
                        if tool_call not in aggregated_tool_calls:
                            aggregated_tool_calls.append(tool_call)
            
            # Construct the aggregated response message
            response_message = {
                "role": role,
                "content": aggregated_content
            }
            
            # Add tool_calls if there are any
            if aggregated_tool_calls:
                response_message["tool_calls"] = aggregated_tool_calls
            
            # Check if the response has problematic tokens
            if "<|im_" in aggregated_content:
                print(f"Detected problematic tokens in response, retrying ({retries+1}/{max_retries+1})")
                retries += 1
                if retries > max_retries:
                    break
                continue

            # Clean up the response
            return clean_llm_response(response_message)

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
