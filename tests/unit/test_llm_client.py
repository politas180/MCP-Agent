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

# Add the backend directory to the path so we can import the llm_client module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

import llm_client


@pytest.mark.unit
@pytest.mark.backend
class TestLLMClient(unittest.TestCase):
    """Test cases for the LLM client."""

    @patch('llm_client.ollama.Client')
    def test_llm_call_success(self, mock_client_class):
        """Test that the LLM call function works correctly."""
        # Set up the mock
        mock_client_instance = mock_client_class.return_value
        mock_response = MagicMock()
        mock_response.message = {
            "role": "assistant",
            "content": "Hello, how can I help you today?",
            "tool_calls": []
        }
        mock_client_instance.chat.return_value = mock_response
        
        # Call the function
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
        
        result = llm_client.llm_call(messages)
        
        # Verify the result
        self.assertEqual(result["role"], "assistant")
        self.assertEqual(result["content"], "Hello, how can I help you today?")
        
        # Verify the mock was called correctly
        mock_client_instance.chat.assert_called_once()
        args, kwargs = mock_client_instance.chat.call_args
        self.assertEqual(kwargs["model"], llm_client.OLLAMA_MODEL)
        self.assertEqual(kwargs["messages"], messages)
        self.assertEqual(kwargs["stream"], False)
        self.assertEqual(kwargs["options"]["temperature"], llm_client.DEFAULT_TEMPERATURE)
        self.assertEqual(kwargs["options"]["num_predict"], llm_client.DEFAULT_MAX_MODEL_TOKENS)

    @patch('llm_client.ollama.Client')
    def test_llm_call_with_tool_calls(self, mock_client_class):
        """Test that the LLM call function handles tool calls correctly."""
        # Set up the mock
        mock_client_instance = mock_client_class.return_value
        mock_response = MagicMock()
        mock_response.message = {
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
        mock_client_instance.chat.return_value = mock_response
        
        # Call the function
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about Python"}
        ]
        
        result = llm_client.llm_call(messages)
        
        # Verify the result
        self.assertEqual(result["role"], "assistant")
        self.assertEqual(result["content"], "I'll search for information about Python.")
        
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["function"]["name"], "search")
        self.assertIn("Python programming language", result["tool_calls"][0]["function"]["arguments"])

    @patch('llm_client.ollama.Client')
    def test_llm_call_retry_on_error(self, mock_client_class):
        """Test that the LLM call function retries on error."""
        # Set up the mock to fail on first call and succeed on second
        mock_client_instance = mock_client_class.return_value
        
        # First call raises an exception
        mock_client_instance.chat.side_effect = [
            Exception("API error"),
            MagicMock(message={
                "role": "assistant",
                "content": "Hello, how can I help you today?",
                "tool_calls": []
            })
        ]
        
        # Call the function
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
        
        result = llm_client.llm_call(messages)
        
        # Verify the result
        self.assertEqual(result["role"], "assistant")
        self.assertEqual(result["content"], "Hello, how can I help you today?")
        
        # Verify the mock was called twice
        self.assertEqual(mock_client_instance.chat.call_count, 2)

    @patch('llm_client.ollama.Client')
    def test_llm_call_max_retries_exceeded(self, mock_client_class):
        """Test that the LLM call function handles max retries exceeded."""
        # Set up the mock to always fail
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.chat.side_effect = Exception("API error")
        
        # Call the function with a small max_retries value
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
        
        # Call with max_retries=0 to fail immediately
        result = llm_client.llm_call(messages, max_retries=0)
        
        # Verify the result contains the error message
        self.assertEqual(result["role"], "assistant")
        self.assertEqual(result["content"], "I'm sorry, I encountered an error processing your request. Please try again.")
        
        # Verify the mock was called the expected number of times
        self.assertEqual(mock_client_instance.chat.call_count, 1)  # Initial call only, no retries


# New tests for temperature and max_tokens
@patch('llm_client.ollama.Client')
def test_llm_call_uses_custom_temp_and_tokens(mock_client_class):
    """Test llm_call uses provided temperature and max_tokens."""
    mock_client_instance = mock_client_class.return_value
    mock_response = MagicMock()
    mock_response.message = {"role": "assistant", "content": "Test response"}
    mock_client_instance.chat.return_value = mock_response

    custom_temp = 0.99
    custom_tokens = 555
    messages = [{"role": "user", "content": "Hello"}]

    # Directly import llm_call
    from llm_client import llm_call
    
    llm_call(messages, temperature=custom_temp, max_tokens=custom_tokens)

    assert mock_client_instance.chat.call_count == 1
    called_args, called_kwargs = mock_client_instance.chat.call_args
    options = called_kwargs['options']

    assert options['temperature'] == custom_temp
    assert options['num_predict'] == custom_tokens

@patch('llm_client.ollama.Client')
def test_llm_call_uses_default_temp_and_tokens_if_none(mock_client_class):
    """Test llm_call uses default temp/tokens if None are provided."""
    mock_client_instance = mock_client_class.return_value
    mock_response = MagicMock()
    mock_response.message = {"role": "assistant", "content": "Test response"}
    mock_client_instance.chat.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    # Directly import llm_call and config values for these new tests
    from llm_client import llm_call
    from config import DEFAULT_TEMPERATURE, DEFAULT_MAX_MODEL_TOKENS

    llm_call(messages, temperature=None, max_tokens=None) # Explicitly pass None

    assert mock_client_instance.chat.call_count == 1
    called_args, called_kwargs = mock_client_instance.chat.call_args
    options = called_kwargs['options']
    # The retry logic adds a small amount (0.05 * retries) if retries > 0.
    # For the first attempt (retries=0), temp_adjustment is 0.
    assert options['temperature'] == DEFAULT_TEMPERATURE
    assert options['num_predict'] == DEFAULT_MAX_MODEL_TOKENS

@patch('llm_client.ollama.Client')
def test_llm_call_uses_default_temp_and_tokens_implicitly(mock_client_class):
    """Test llm_call uses default temp/tokens if arguments are not passed."""
    mock_client_instance = mock_client_class.return_value
    mock_response = MagicMock()
    mock_response.message = {"role": "assistant", "content": "Test response"}
    mock_client_instance.chat.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    # Directly import llm_call and config values for these new tests
    from llm_client import llm_call
    from config import DEFAULT_TEMPERATURE, DEFAULT_MAX_MODEL_TOKENS
    
    llm_call(messages) # Not passing temp/tokens

    assert mock_client_instance.chat.call_count == 1
    called_args, called_kwargs = mock_client_instance.chat.call_args
    options = called_kwargs['options']
    assert options['temperature'] == DEFAULT_TEMPERATURE
    assert options['num_predict'] == DEFAULT_MAX_MODEL_TOKENS
