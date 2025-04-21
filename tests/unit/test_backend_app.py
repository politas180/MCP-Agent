#!/usr/bin/env python
"""
Unit tests for the backend Flask application.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
import pytest
import flask

# Add the backend directory to the path so we can import the app module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

import app as flask_app


@pytest.mark.unit
@pytest.mark.backend
class TestBackendApp(unittest.TestCase):
    """Test cases for the backend Flask application."""

    def setUp(self):
        """Set up the test client."""
        self.app = flask_app.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        """Test the health endpoint."""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'ok')

    @patch('app.llm_call')
    def test_chat_endpoint_new_session(self, mock_llm_call):
        """Test the chat endpoint with a new session."""
        # Set up the mock
        mock_llm_call.return_value = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ],
            "tool_calls": []
        }
        
        # Make the request
        response = self.client.post('/api/chat', json={
            "message": "Hello",
            "session_id": "test_session_123",
            "advanced_mode": False
        })
        
        data = json.loads(response.data)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("messages", data)
        self.assertEqual(len(data["messages"]), 2)
        self.assertEqual(data["messages"][0]["role"], "user")
        self.assertEqual(data["messages"][0]["content"], "Hello")
        self.assertEqual(data["messages"][1]["role"], "assistant")
        self.assertEqual(data["messages"][1]["content"], "Hi there! How can I help you today?")
        
        # Verify the session was created
        self.assertIn("test_session_123", flask_app.CONVERSATIONS)
        
        # Verify the mock was called correctly
        mock_llm_call.assert_called_once()
        args, kwargs = mock_llm_call.call_args
        self.assertEqual(kwargs["messages"][0]["role"], "system")
        self.assertEqual(kwargs["messages"][1]["role"], "user")
        self.assertEqual(kwargs["messages"][1]["content"], "Hello")

    @patch('app.llm_call')
    def test_chat_endpoint_existing_session(self, mock_llm_call):
        """Test the chat endpoint with an existing session."""
        # Set up an existing session
        session_id = "test_session_456"
        flask_app.CONVERSATIONS[session_id] = {
            "messages": [
                {"role": "system", "content": flask_app.get_system_prompt()},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ]
        }
        
        # Set up the mock
        mock_llm_call.return_value = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"},
                {"role": "user", "content": "What's the weather like?"},
                {"role": "assistant", "content": "I don't have real-time weather data. Would you like me to search for weather information?"}
            ],
            "tool_calls": []
        }
        
        # Make the request
        response = self.client.post('/api/chat', json={
            "message": "What's the weather like?",
            "session_id": session_id,
            "advanced_mode": False
        })
        
        data = json.loads(response.data)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("messages", data)
        self.assertEqual(len(data["messages"]), 4)
        self.assertEqual(data["messages"][2]["role"], "user")
        self.assertEqual(data["messages"][2]["content"], "What's the weather like?")
        self.assertEqual(data["messages"][3]["role"], "assistant")
        self.assertEqual(data["messages"][3]["content"], "I don't have real-time weather data. Would you like me to search for weather information?")
        
        # Verify the session was updated
        self.assertEqual(len(flask_app.CONVERSATIONS[session_id]["messages"]), 5)  # system + 4 messages
        
        # Verify the mock was called correctly
        mock_llm_call.assert_called_once()
        args, kwargs = mock_llm_call.call_args
        self.assertEqual(len(kwargs["messages"]), 4)  # system + 3 previous messages + new message
        self.assertEqual(kwargs["messages"][3]["role"], "user")
        self.assertEqual(kwargs["messages"][3]["content"], "What's the weather like?")

    def test_reset_endpoint(self):
        """Test the reset endpoint."""
        # Set up an existing session
        session_id = "test_session_789"
        flask_app.CONVERSATIONS[session_id] = {
            "messages": [
                {"role": "system", "content": flask_app.get_system_prompt()},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ]
        }
        
        # Make the request
        response = self.client.post('/api/reset', json={
            "session_id": session_id
        })
        
        data = json.loads(response.data)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "ok")
        
        # Verify the session was reset
        self.assertNotIn(session_id, flask_app.CONVERSATIONS)

    @patch('app.llm_call')
    @patch('app.TOOL_IMPLS')
    def test_chat_endpoint_with_tool_call(self, mock_tool_impls, mock_llm_call):
        """Test the chat endpoint with a tool call."""
        # Set up the mocks
        mock_search = MagicMock(return_value=[
            {
                "title": "Weather in London",
                "url": "https://example.com/weather/london",
                "snippet": "Current weather in London: 15°C, Cloudy"
            }
        ])
        mock_tool_impls.get.return_value = mock_search
        
        # Mock LLM response with a tool call
        mock_llm_call.return_value = {
            "messages": [
                {"role": "user", "content": "What's the weather in London?"},
                {"role": "assistant", "content": "I'll search for the weather in London."}
            ],
            "tool_calls": [
                {
                    "name": "search",
                    "args": {
                        "query": "current weather in London",
                        "max_results": 1
                    }
                }
            ]
        }
        
        # Make the request
        response = self.client.post('/api/chat', json={
            "message": "What's the weather in London?",
            "session_id": "test_session_tool",
            "advanced_mode": True
        })
        
        data = json.loads(response.data)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("messages", data)
        self.assertIn("debug_info", data)
        
        # Verify the tool was called
        mock_tool_impls.get.assert_called_with("search")
        mock_search.assert_called_with(query="current weather in London", max_results=1)
        
        # Verify debug info contains tool call information
        tool_calls = [d for d in data["debug_info"] if d["type"] == "tool_call"]
        self.assertTrue(len(tool_calls) > 0)
        self.assertEqual(tool_calls[0]["name"], "search")
        self.assertEqual(tool_calls[0]["args"]["query"], "current weather in London")


if __name__ == '__main__':
    unittest.main()
