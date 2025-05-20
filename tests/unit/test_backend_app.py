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

# Import constants and functions for context management tests
from backend.config import MAX_MODEL_TOKENS
from backend.app import estimate_tokens, CONVERSATIONS as APP_CONVERSATIONS # Use APP_CONVERSATIONS to avoid conflict

@pytest.mark.unit
@pytest.mark.backend
@pytest.mark.context_management
class TestContextManagement(unittest.TestCase):
    """Test cases for token-based context management."""

    def setUp(self):
        """Set up the test client and clear conversations."""
        self.app_instance = flask_app.app
        self.app_instance.config['TESTING'] = True
        self.client = self.app_instance.test_client()
        APP_CONVERSATIONS.clear() # Clear global conversations before each test
        self.session_id = "test_context_session"
        # Initialize conversation with a system prompt for this session
        # This simulates what get_or_create_conversation would do
        system_prompt_dict = flask_app.get_system_prompt()
        APP_CONVERSATIONS[self.session_id] = [{"role": "system", "content": system_prompt_dict["standard"]}]


    def tearDown(self):
        """Clean up conversations after each test."""
        APP_CONVERSATIONS.clear()

    def _create_message(self, role: str, content: str, tool_calls: list | None = None, tool_call_id: str | None = None) -> dict:
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        if tool_call_id:
            msg["tool_call_id"] = tool_call_id
        return msg

    def _get_total_tokens(self, messages: list[dict]) -> int:
        total_tokens = 0
        for msg in messages:
            total_tokens += estimate_tokens(msg.get("content", ""))
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                total_tokens += estimate_tokens(json.dumps(msg.get("tool_calls")))
        return total_tokens

    @patch('backend.app.llm_call')
    def test_context_truncation_simple(self, mock_llm_call: MagicMock):
        mock_llm_call.return_value = {"role": "assistant", "content": "Dummy response"}
        
        # Create messages that significantly exceed the 0.75 * MAX_MODEL_TOKENS threshold
        # MAX_MODEL_TOKENS is 8192. Threshold is 6144.
        # System prompt is ~100 tokens.
        # Let's make messages that are each about 1000 tokens (250 chars * 4)
        # 7 such messages + system prompt = ~7100 tokens, should be truncated.
        
        long_content = "a" * (1000 * 4) # Approx 1000 tokens
        
        # Add to global CONVERSATIONS for the session_id
        current_conversation = APP_CONVERSATIONS[self.session_id]
        current_conversation.append(self._create_message("user", "User message 1 " + long_content))
        current_conversation.append(self._create_message("assistant", "Assistant message 1 " + long_content))
        current_conversation.append(self._create_message("user", "User message 2 " + long_content)) # This is the one to be dropped
        current_conversation.append(self._create_message("assistant", "Assistant message 2 " + long_content))
        current_conversation.append(self._create_message("user", "User message 3 " + long_content))
        current_conversation.append(self._create_message("assistant", "Assistant message 3 " + long_content))
        
        # This is the *new* user message that triggers the call
        final_user_message_content = "User message FINAL " + long_content 
        
        self.client.post('/api/chat', json={"message": final_user_message_content, "session_id": self.session_id})
        
        called_messages = mock_llm_call.call_args[0][0]
        
        self.assertTrue(len(called_messages) < len(current_conversation) +1) # +1 for the new user message before truncation
        self.assertEqual(called_messages[0]["role"], "system")
        self.assertEqual(called_messages[-1]["content"], final_user_message_content) # Last user message must be present
        
        # Check that "User message 2" (and its assistant reply) are likely dropped
        # The exact number depends on precise token counts, but User message 2 should be gone.
        # Original history before final_user_message: sys, u1, a1, u2, a2, u3, a3 (7 messages)
        # Total to LLM (including final_user_message): sys, u3, a3, final_user_message (4 messages if 2 pairs are dropped)
        # Each message is ~1000 tokens. System ~100. Threshold ~6144.
        # sys(100) + u1(1000) + a1(1000) + u2(1000) + a2(1000) + u3(1000) + a3(1000) = 6100 (for history)
        # final_user_message_content (1000)
        # current_tokens for history: sys(100). Reversed history: a3, u3, a2, u2, a1, u1
        # a3 (1000) -> current_tokens = 1100. History = [a3]
        # u3 (1000) -> current_tokens = 2100. History = [u3, a3]
        # a2 (1000) -> current_tokens = 3100. History = [a2, u3, a3]
        # u2 (1000) -> current_tokens = 4100. History = [u2, a2, u3, a3]
        # a1 (1000) -> current_tokens = 5100. History = [a1, u2, a2, u3, a3]
        # u1 (1000) -> current_tokens = 6100. History = [u1, a1, u2, a2, u3, a3] (This fits TOKEN_THRESHOLD)
        # Now add last_user_message (1000). Total with history = 7100.
        # This exceeds MAX_MODEL_TOKENS (8192*0.75 = 6144 for history, but the hard check is MAX_MODEL_TOKENS = 8192)
        # The loop `while new_messages_history and (current_tokens + last_user_message_tokens > MAX_MODEL_TOKENS):`
        # Here, current_tokens is for history (6100) + system (100) = 6200.
        # last_user_message_tokens = 1000. Total = 7200. This is < MAX_MODEL_TOKENS (8192).
        # So, no history should be dropped by the *second* loop.
        # The first loop (TOKEN_THRESHOLD = 6144 for history accumulation):
        # sys_tokens = estimate_tokens(APP_CONVERSATIONS[self.session_id][0]['content']) -> ~100
        # current_tokens = sys_tokens.
        # History: u1,a1,u2,a2,u3,a3. Reversed: a3,u3,a2,u2,a1,u1
        # msg a3 (1000). current_tokens = 100+1000=1100. history_list=[a3]
        # msg u3 (1000). current_tokens = 1100+1000=2100. history_list=[u3,a3]
        # msg a2 (1000). current_tokens = 2100+1000=3100. history_list=[a2,u3,a3]
        # msg u2 (1000). current_tokens = 3100+1000=4100. history_list=[u2,a2,u3,a3]
        # msg a1 (1000). current_tokens = 4100+1000=5100. history_list=[a1,u2,a2,u3,a3]
        # msg u1 (1000). current_tokens = 5100+1000=6100. history_list=[u1,a1,u2,a2,u3,a3]
        # All history fits TOKEN_THRESHOLD.
        # So, called_messages should be [system, u1, a1, u2, a2, u3, a3, final_user_message]
        # This means my initial comment about User message 2 being dropped was based on a miscalculation of what current_tokens represents in the loop.
        # Let's re-evaluate. The `current_tokens` in the history loop *starts* with system_message tokens.
        # current_tokens = estimate_tokens(system_message.get("content", "")) -> this is how it is in app.py
        # So, if system is 100 tokens, and threshold is 6144. Available for history is 6044.
        # 5 messages of 1000 tokens = 5000. (a3,u3,a2,u2,a1). Total 5100 with system.
        # 6th message (u1) of 1000 tokens would make history 6000. Total 6100 with system. This fits.
        # So all 6 history messages should be kept.
        # Expected messages: system, u1, a1, u2, a2, u3, a3, final_user_msg. Length should be 8.
        # The history_messages are messages[1:-1]. Original messages: sys, u1, a1, u2, a2, u3, a3, final_user_msg (added by POST)
        # So before context management, messages = [sys, u1,a1,u2,a2,u3,a3, final_user_msg]
        # history_messages = [u1,a1,u2,a2,u3,a3]. Reversed: [a3,u3,a2,u2,a1,u1]
        # sys_tokens = estimate_tokens(APP_CONVERSATIONS[self.session_id][0]['content'])
        # current_tokens = sys_tokens
        # loop:
        #   a3 (1000): current_tokens += 1000. new_history = [a3]
        #   u3 (1000): current_tokens += 1000. new_history = [u3, a3]
        #   a2 (1000): current_tokens += 1000. new_history = [a2, u3, a3]
        #   u2 (1000): current_tokens += 1000. new_history = [u2, a2, u3, a3]
        #   a1 (1000): current_tokens += 1000. new_history = [a1, u2, a2, u3, a3]
        #   u1 (1000): current_tokens += 1000. new_history = [u1, a1, u2, a2, u3, a3]
        # All these fit under TOKEN_THRESHOLD (6144) because sys_tokens + 6*1000 = ~6100.
        # last_user_message_tokens = 1000.
        # current_tokens (after history loop) is ~6100.
        # Check for `current_tokens + last_user_message_tokens > MAX_MODEL_TOKENS` (8192)
        # 6100 + 1000 = 7100. This is NOT > 8192. So the second loop does not run.
        # Final messages: [system] + new_history + [last_user_message]
        # = [system, u1, a1, u2, a2, u3, a3, final_user_message_content_obj]. Length = 8.
        
        # Let's make one message much larger to force truncation by the first loop.
        # System (100) + 5*1000 (5000) = 5100. This is < 6144.
        # If 6th history message makes it exceed 6044 for history part.
        # Let's use 5 messages of 1000 tokens, and 1 of 1500.
        APP_CONVERSATIONS[self.session_id] = [{"role": "system", "content": system_prompt_dict["standard"]}] # Reset
        current_conversation = APP_CONVERSATIONS[self.session_id]
        current_conversation.append(self._create_message("user", "User message 1 " + "b"*(1500*4))) # u1 (1500) - oldest in history
        current_conversation.append(self._create_message("assistant", "Assistant message 1 " + "b"*(1000*4))) # a1 (1000)
        current_conversation.append(self._create_message("user", "User message 2 " + "b"*(1000*4))) # u2 (1000)
        current_conversation.append(self._create_message("assistant", "Assistant message 2 " + "b"*(1000*4))) # a2 (1000)
        current_conversation.append(self._create_message("user", "User message 3 " + "b"*(1000*4))) # u3 (1000)
        current_conversation.append(self._create_message("assistant", "Assistant message 3 " + "b"*(1000*4))) # a3 (1000) - newest in history
        # History: u1(1500), a1(1000), u2(1000), a2(1000), u3(1000), a3(1000). Total = 6500.
        # Reversed history: a3,u3,a2,u2,a1,u1
        # current_tokens = sys_tokens (~100)
        # a3(1000): current_tokens=1100. hist=[a3]
        # u3(1000): current_tokens=2100. hist=[u3,a3]
        # a2(1000): current_tokens=3100. hist=[a2,u3,a3]
        # u2(1000): current_tokens=4100. hist=[u2,a2,u3,a3]
        # a1(1000): current_tokens=5100. hist=[a1,u2,a2,u3,a3]
        # u1(1500): current_tokens=5100+1500 = 6600. This is > TOKEN_THRESHOLD (6144). So u1 is dropped.
        # new_messages_history will be [a1,u2,a2,u3,a3] (reversed: [a3,u3,a2,u2,a1])
        # called_messages should be: [system, a1,u2,a2,u3,a3, final_user_msg]. Length 7.
        # Original conversation length before POST: 7. After POST: 8.
        # Expected length of called_messages: 1 (sys) + 5 (hist) + 1 (last_user) = 7.
        
        self.client.post('/api/chat', json={"message": "Final user message", "session_id": self.session_id})
        called_messages = mock_llm_call.call_args[0][0]

        self.assertEqual(len(called_messages), 7) # System + 5 history + last user
        self.assertEqual(called_messages[0]["role"], "system")
        self.assertEqual(called_messages[-1]["content"], "Final user message")
        self.assertEqual(called_messages[1]["content"], "Assistant message 1 " + "b"*(1000*4)) # a1 should be the first history message
        
        final_tokens = self._get_total_tokens(called_messages)
        self.assertLessEqual(final_tokens, MAX_MODEL_TOKENS) # Should be well within hard limit
        # It should also be close to TOKEN_THRESHOLD + last_user_tokens, or less if history was small
        # current_tokens after history loop = 5100. last_user_tokens for "Final user message" is small.
        # So total should be around 5100 + small. This is < TOKEN_THRESHOLD.

    @patch('backend.app.llm_call')
    def test_context_no_truncation_if_within_limit(self, mock_llm_call: MagicMock):
        mock_llm_call.return_value = {"role": "assistant", "content": "Dummy response"}
        
        current_conversation = APP_CONVERSATIONS[self.session_id]
        current_conversation.append(self._create_message("user", "User message 1"))
        current_conversation.append(self._create_message("assistant", "Assistant message 1"))
        
        # Expected messages to llm_call: system, user1, assistant1, "Final short message"
        # All these should fit easily.
        
        self.client.post('/api/chat', json={"message": "Final short message", "session_id": self.session_id})
        called_messages = mock_llm_call.call_args[0][0]
        
        self.assertEqual(len(called_messages), 4)
        self.assertEqual(called_messages[0]["role"], "system")
        self.assertEqual(called_messages[1]["content"], "User message 1")
        self.assertEqual(called_messages[2]["content"], "Assistant message 1")
        self.assertEqual(called_messages[3]["content"], "Final short message")

    @patch('backend.app.llm_call')
    def test_long_tool_result_truncation(self, mock_llm_call: MagicMock):
        mock_llm_call.return_value = {"role": "assistant", "content": "Dummy response"}
        
        long_tool_content = "t" * 2500 # Exceeds 2000 char limit for tool content in context
        
        current_conversation = APP_CONVERSATIONS[self.session_id]
        current_conversation.append(self._create_message("user", "User message 1"))
        current_conversation.append(self._create_message("assistant", "Assistant message 1", tool_calls=[{"id": "tc1", "function": {"name": "some_tool", "arguments": "{}"}}]))
        current_conversation.append(self._create_message("tool", long_tool_content, tool_call_id="tc1"))
        
        self.client.post('/api/chat', json={"message": "Final user message", "session_id": self.session_id})
        called_messages = mock_llm_call.call_args[0][0]
        
        # Expected: sys, user1, assistant1, truncated_tool_msg, final_user_msg
        self.assertEqual(len(called_messages), 5)
        found_tool_msg = False
        for msg in called_messages:
            if msg["role"] == "tool":
                found_tool_msg = True
                self.assertTrue(msg["content"].startswith(long_tool_content[:2000]))
                self.assertIn("[Content truncated to save context space]", msg["content"])
                break
        self.assertTrue(found_tool_msg, "Tool message not found in context")

    @patch('backend.app.llm_call')
    def test_very_long_last_user_message_truncation(self, mock_llm_call: MagicMock):
        mock_llm_call.return_value = {"role": "assistant", "content": "Dummy response"}
        
        # MAX_MODEL_TOKENS = 8192. MAX_SINGLE_MESSAGE_CHAR_LIMIT = int(8192 * 3.5) = 28672 chars
        excessively_long_content = "e" * (int(MAX_MODEL_TOKENS * 3.5) + 100)
        
        self.client.post('/api/chat', json={"message": excessively_long_content, "session_id": self.session_id})
        called_messages = mock_llm_call.call_args[0][0]
        
        self.assertEqual(len(called_messages), 2) # System + truncated user message
        self.assertEqual(called_messages[0]["role"], "system")
        self.assertEqual(called_messages[1]["role"], "user")
        self.assertTrue(called_messages[1]["content"].startswith(excessively_long_content[:int(MAX_MODEL_TOKENS * 3.5)]))
        self.assertIn("[User message content truncated as it was excessively long]", called_messages[1]["content"])

    @patch('backend.app.llm_call')
    def test_system_prompt_and_recent_user_message_always_present(self, mock_llm_call: MagicMock):
        mock_llm_call.return_value = {"role": "assistant", "content": "Dummy response"}

        # Create a long conversation that will definitely be truncated
        current_conversation = APP_CONVERSATIONS[self.session_id]
        original_system_content = current_conversation[0]["content"]
        
        for i in range(10): # Add 10 pairs of user/assistant messages, each large
            current_conversation.append(self._create_message("user", f"History User {i} " + "h"*(1000*4)))
            current_conversation.append(self._create_message("assistant", f"History Assistant {i} " + "h"*(1000*4)))
        
        final_user_msg_content = "The very last user message."
        self.client.post('/api/chat', json={"message": final_user_msg_content, "session_id": self.session_id})
        called_messages = mock_llm_call.call_args[0][0]
        
        self.assertGreater(len(called_messages), 2) # Should have at least sys, some history, and user
        self.assertEqual(called_messages[0]["role"], "system")
        self.assertEqual(called_messages[0]["content"], original_system_content)
        self.assertEqual(called_messages[-1]["role"], "user")
        self.assertEqual(called_messages[-1]["content"], final_user_msg_content)
        # Ensure some recent history is present, e.g. "History Assistant 9"
        found_recent_history = any(msg["role"] == "assistant" and "History Assistant 9" in msg["content"] for msg in called_messages)
        self.assertTrue(found_recent_history, "Most recent history not found")


    @patch('backend.app.llm_call')
    def test_context_management_with_max_tokens_exceeded_by_last_user_msg(self, mock_llm_call: MagicMock):
        mock_llm_call.return_value = {"role": "assistant", "content": "Dummy response"}

        # Fill history close to MAX_MODEL_TOKENS (8192), but below TOKEN_THRESHOLD (6144) for history part
        # System prompt ~100 tokens.
        # Let history be ~6000 tokens, so total with system is ~6100 (fits TOKEN_THRESHOLD for history part)
        # Then add a large last user message that pushes total over MAX_MODEL_TOKENS (8192)
        # This should trigger the *second* truncation loop.
        
        current_conversation = APP_CONVERSATIONS[self.session_id]
        current_conversation.append(self._create_message("user", "Old User Message " + "o"*(2000*4))) # 2000 tokens
        current_conversation.append(self._create_message("assistant", "Old Assistant Message " + "o"*(2000*4))) # 2000 tokens
        current_conversation.append(self._create_message("user", "Recent User Message " + "r"*(2000*4))) # 2000 tokens
        # History part is 6000 tokens. With system (~100), total is ~6100. This fits TOKEN_THRESHOLD for history.
        
        # Now, a large last user message. Total tokens for this message: ~2500 tokens.
        # 6100 (history+sys) + 2500 (last_user) = 8600. This exceeds MAX_MODEL_TOKENS (8192).
        # The oldest message ("Old User Message") should be dropped.
        large_final_user_message = "Final Large User Message " + "L"*(2500*4 - len("Final Large User Message ")) 
        
        self.client.post('/api/chat', json={"message": large_final_user_message, "session_id": self.session_id})
        called_messages = mock_llm_call.call_args[0][0]
        
        # Expected: System, Old Assistant, Recent User, Final Large User. (4 messages)
        # "Old User Message" should be dropped.
        self.assertEqual(len(called_messages), 4) 
        self.assertEqual(called_messages[0]["role"], "system")
        self.assertNotIn("Old User Message", [m.get("content","") for m in called_messages])
        self.assertIn("Old Assistant Message", called_messages[1].get("content",""))
        self.assertIn("Recent User Message", called_messages[2].get("content",""))
        self.assertEqual(called_messages[-1]["content"], large_final_user_message)
        
        final_tokens = self._get_total_tokens(called_messages)
        self.assertLessEqual(final_tokens, MAX_MODEL_TOKENS)


    @patch('backend.app.llm_call')
    def test_empty_history(self, mock_llm_call: MagicMock):
        mock_llm_call.return_value = {"role": "assistant", "content": "Dummy response"}
        # APP_CONVERSATIONS[self.session_id] already contains system prompt from setUp.
        
        self.client.post('/api/chat', json={"message": "First user message", "session_id": self.session_id})
        called_messages = mock_llm_call.call_args[0][0]
        
        self.assertEqual(len(called_messages), 2) # System + first user message
        self.assertEqual(called_messages[0]["role"], "system")
        self.assertEqual(called_messages[1]["role"], "user")
        self.assertEqual(called_messages[1]["content"], "First user message")


if __name__ == '__main__':
    unittest.main()
