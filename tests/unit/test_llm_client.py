#!/usr/bin/env python
"""
Unit tests for the LLM client functionality.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
import pytest
import requests

# Add the backend directory to the path so we can import the llm_client module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

import llm_client


@pytest.mark.unit
@pytest.mark.backend
class TestLLMClient(unittest.TestCase):
    """Test cases for the LLM client."""

    @patch('llm_client.requests.post')
    def test_llm_call_success(self, mock_post):
        """Test that the LLM call function works correctly."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello, how can I help you today?",
                        "tool_calls": []
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Call the function
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
        
        result = llm_client.llm_call(messages)
        
        # Verify the result
        self.assertIn("messages", result)
        self.assertEqual(len(result["messages"]), 3)
        self.assertEqual(result["messages"][0]["role"], "system")
        self.assertEqual(result["messages"][1]["role"], "user")
        self.assertEqual(result["messages"][2]["role"], "assistant")
        self.assertEqual(result["messages"][2]["content"], "Hello, how can I help you today?")
        
        # Verify the mock was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], f"{llm_client.LMSTUDIO_HOST}/v1/chat/completions")
        self.assertEqual(kwargs["json"]["messages"], messages)
        self.assertEqual(kwargs["json"]["stream"], False)

    @patch('llm_client.requests.post')
    def test_llm_call_with_tool_calls(self, mock_post):
        """Test that the LLM call function handles tool calls correctly."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'll search for information about Python.",
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "search",
                                    "arguments": json.dumps({
                                        "query": "Python programming language",
                                        "max_results": 3
                                    })
                                }
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Call the function
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about Python"}
        ]
        
        result = llm_client.llm_call(messages)
        
        # Verify the result
        self.assertIn("messages", result)
        self.assertEqual(len(result["messages"]), 3)
        self.assertEqual(result["messages"][2]["role"], "assistant")
        self.assertEqual(result["messages"][2]["content"], "I'll search for information about Python.")
        
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "search")
        self.assertEqual(result["tool_calls"][0]["args"]["query"], "Python programming language")
        self.assertEqual(result["tool_calls"][0]["args"]["max_results"], 3)

    @patch('llm_client.requests.post')
    def test_llm_call_retry_on_error(self, mock_post):
        """Test that the LLM call function retries on error."""
        # Set up the mock to fail on first call and succeed on second
        mock_response_error = MagicMock()
        mock_response_error.raise_for_status.side_effect = requests.exceptions.RequestException("API error")
        
        mock_response_success = MagicMock()
        mock_response_success.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello, how can I help you today?",
                        "tool_calls": []
                    }
                }
            ]
        }
        
        mock_post.side_effect = [mock_response_error, mock_response_success]
        
        # Call the function
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
        
        result = llm_client.llm_call(messages)
        
        # Verify the result
        self.assertIn("messages", result)
        self.assertEqual(result["messages"][2]["role"], "assistant")
        self.assertEqual(result["messages"][2]["content"], "Hello, how can I help you today?")
        
        # Verify the mock was called twice
        self.assertEqual(mock_post.call_count, 2)

    @patch('llm_client.requests.post')
    def test_llm_call_max_retries_exceeded(self, mock_post):
        """Test that the LLM call function handles max retries exceeded."""
        # Set up the mock to always fail
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API error")
        mock_post.return_value = mock_response
        
        # Call the function with a small max_retries value
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
        
        # Override the max_retries for testing
        original_max_retries = llm_client.MAX_RETRIES
        llm_client.MAX_RETRIES = 2
        
        try:
            with self.assertRaises(Exception) as context:
                llm_client.llm_call(messages)
            
            self.assertIn("Failed to get response from LLM after", str(context.exception))
            
            # Verify the mock was called the expected number of times
            self.assertEqual(mock_post.call_count, 3)  # Initial call + 2 retries
        finally:
            # Restore the original max_retries
            llm_client.MAX_RETRIES = original_max_retries


if __name__ == '__main__':
    unittest.main()

# New tests for temperature and max_tokens
@patch('backend.llm_client.requests.post')
def test_llm_call_uses_custom_temp_and_tokens(mock_post):
    """Test llm_call uses provided temperature and max_tokens."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "Test response"}}]}
    mock_post.return_value = mock_response

    custom_temp = 0.99
    custom_tokens = 555
    messages = [{"role": "user", "content": "Hello"}]

    # Directly import llm_call and config values for these new tests
    from backend.llm_client import llm_call
    
    llm_call(messages, temperature=custom_temp, max_tokens=custom_tokens)

    assert mock_post.call_count == 1
    called_args, called_kwargs = mock_post.call_args
    request_payload = called_kwargs['json']

    assert request_payload['temperature'] == custom_temp
    assert request_payload['max_tokens'] == custom_tokens

@patch('backend.llm_client.requests.post')
def test_llm_call_uses_default_temp_and_tokens_if_none(mock_post):
    """Test llm_call uses default temp/tokens if None are provided."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "Test response"}}]}
    mock_post.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    # Directly import llm_call and config values for these new tests
    from backend.llm_client import llm_call
    from backend.config import DEFAULT_TEMPERATURE, DEFAULT_MAX_MODEL_TOKENS

    llm_call(messages, temperature=None, max_tokens=None) # Explicitly pass None

    assert mock_post.call_count == 1
    called_args, called_kwargs = mock_post.call_args
    request_payload = called_kwargs['json']
    # The retry logic adds a small amount (0.05 * retries) if retries > 0.
    # For the first attempt (retries=0), temp_adjustment is 0.
    assert request_payload['temperature'] == DEFAULT_TEMPERATURE
    assert request_payload['max_tokens'] == DEFAULT_MAX_MODEL_TOKENS

@patch('backend.llm_client.requests.post')
def test_llm_call_uses_default_temp_and_tokens_implicitly(mock_post):
    """Test llm_call uses default temp/tokens if arguments are not passed."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "Test response"}}]}
    mock_post.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    # Directly import llm_call and config values for these new tests
    from backend.llm_client import llm_call
    from backend.config import DEFAULT_TEMPERATURE, DEFAULT_MAX_MODEL_TOKENS
    
    llm_call(messages) # Not passing temp/tokens

    assert mock_post.call_count == 1
    called_args, called_kwargs = mock_post.call_args
    request_payload = called_kwargs['json']
    assert request_payload['temperature'] == DEFAULT_TEMPERATURE
    assert request_payload['max_tokens'] == DEFAULT_MAX_MODEL_TOKENS
