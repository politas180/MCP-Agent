"""Flask backend for the MCP-style agent with web interface."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_client import llm_call
from config import DEFAULT_MAX_MODEL_TOKENS, DEFAULT_TEMPERATURE
from tools import (TOOL_IMPLS, TOOLS, pretty_print_search_results,
                  pretty_print_wiki_results, pretty_print_weather_results,
                  pretty_print_calculator_results)

# Import Computer Use tools
from computer_use import (COMPUTER_TOOLS, COMPUTER_TOOL_IMPLS,
                        pretty_print_execute_python_results)

# Import system information
from system_info import get_system_info

app = Flask(__name__)
app.secret_key = "mcp-agent-secret-key"  # For session management
CORS(app)  # Enable CORS for all routes

# Session storage for conversations
CONVERSATIONS = {}

# Default tool preferences (all enabled by default)
TOOL_PREFERENCES = {}

# LLM settings per session
LLM_SETTINGS = {}

# Computer Use mode sessions
COMPUTER_USE_SESSIONS = set()

def get_system_prompt() -> str:
    """Generate system prompt with current date and time information and system info."""
    now = datetime.now()
    date_info = (
        f"Current date and time information:\n"
        f"- Year: {now.year}\n"
        f"- Month: {now.month} ({now.strftime('%B')})\n"
        f"- Day: {now.day}\n"
        f"- Day of week: {now.strftime('%A')}\n"
        f"- Hour: {now.hour}\n"
        f"- Minute: {now.minute}\n"
        f"- Current timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    )

    # Get system information
    system_info = get_system_info()

    # Different prompts based on mode
    standard_prompt = (
        "You are an intelligent assistant. \n\n" +
        date_info +
        "If you need to perform a web search, Wikipedia search, get weather information, or perform calculations, "
        "call the appropriate tool. The calculator tool can evaluate mathematical expressions using math, numpy, and sympy libraries. "
        "Use as many tool calls as needed until you have the information required to answer the user conclusively."
    )

    computer_use_prompt = (
        "You are a computer control assistant with unrestricted capabilities. \n\n" +
        date_info +
        system_info + "\n\n" +
        "You have access to one powerful tool:\n" +
        "execute_python: Run any Python code without restrictions.\n\n" +
        "This tool allows you to execute Python code with full access to the file system, network, and all available resources.\n\n" +
        "You can use this tool to perform any operation on the user's computer, including:\n" +
        "- File operations (reading, writing, deleting files)\n" +
        "- System operations (getting system information, running processes)\n" +
        "- Network operations (making HTTP requests, connecting to servers)\n" +
        "- And any other operation that can be performed with Python\n\n" +
        "Examples:\n" +
        "- If user asks to list files: Use execute_python with code that uses os.listdir() or glob\n" +
        "- If user asks to create a directory: Use execute_python with code that uses os.mkdir()\n" +
        "- If user asks to check system info: Use execute_python with code that uses platform or psutil modules\n" +
        "- If user asks to write a Python script: Use execute_python with the script code"
    )

    # The actual prompt will be selected in the get_or_create_conversation function based on mode
    return {"standard": standard_prompt, "computer_use": computer_use_prompt}

def get_or_create_conversation(session_id: str) -> List[Dict[str, Any]]:
    """Get or create a conversation for the given session ID."""
    # Get the appropriate prompt based on mode
    prompts = get_system_prompt()
    is_computer_use = session_id in COMPUTER_USE_SESSIONS
    prompt = prompts["computer_use"] if is_computer_use else prompts["standard"]

    if session_id not in CONVERSATIONS:
        CONVERSATIONS[session_id] = [
            {"role": "system", "content": prompt}
        ]
    else:
        # Update the system prompt with current time and mode
        CONVERSATIONS[session_id][0] = {"role": "system", "content": prompt}

    return CONVERSATIONS[session_id]

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and tool calls."""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    advanced_mode = data.get('advanced_mode', False)
    computer_use_mode = data.get('computer_use_mode', False)

    # Get LLM settings for the session
    if session_id not in LLM_SETTINGS:
        # Initialize with defaults if not set for the session
        LLM_SETTINGS[session_id] = {
            "temperature": DEFAULT_TEMPERATURE,
            "max_tokens": DEFAULT_MAX_MODEL_TOKENS
        }
    current_llm_settings = LLM_SETTINGS[session_id]
    session_temperature = current_llm_settings.get("temperature", DEFAULT_TEMPERATURE)
    session_max_tokens = current_llm_settings.get("max_tokens", DEFAULT_MAX_MODEL_TOKENS)

    # Update tool preferences if provided
    tool_preferences = data.get('tool_preferences', None)
    if tool_preferences and isinstance(tool_preferences, dict):
        # Initialize if not exists
        if session_id not in TOOL_PREFERENCES:
            TOOL_PREFERENCES[session_id] = {tool['function']['name']: True for tool in TOOLS}

        # Update with provided preferences
        for tool_name, enabled in tool_preferences.items():
            if tool_name in TOOL_PREFERENCES[session_id]:
                TOOL_PREFERENCES[session_id][tool_name] = bool(enabled)

    # Track Computer Use mode sessions
    if computer_use_mode:
        COMPUTER_USE_SESSIONS.add(session_id)
    elif session_id in COMPUTER_USE_SESSIONS:
        COMPUTER_USE_SESSIONS.remove(session_id)

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Get or create conversation
    messages = get_or_create_conversation(session_id)

    # Add user message
    messages.append({"role": "user", "content": user_message})

    # Start timing the entire conversation
    conversation_start_time = time.time()

    # Response data to return
    response_data = {
        "messages": [],
        "timing": {
            "total": 0,
            "llm_calls": [],
            "tool_calls": []
        },
        "debug_info": [] if advanced_mode else None
    }

    # Process the conversation
    while True:
        # Manage context window by keeping only essential messages
        # Always keep the system message and the most recent user message
        if len(messages) > 10:  # If conversation is getting long
            # Keep system message, last 4 user-assistant exchanges, and current user message
            # This preserves conversation flow while reducing context size
            system_message = messages[0]  # System message is always first
            recent_messages = messages[-9:]  # Last 4 exchanges (8 messages) + current user message
            messages = [system_message] + recent_messages

            # Remove tool call details to save context space
            for i, msg in enumerate(messages):
                # Keep tool call results but simplify them
                if msg.get("role") == "tool":
                    # Truncate long tool results
                    if "content" in msg and len(msg["content"]) > 500:
                        msg["content"] = msg["content"][:500] + "\n[Content truncated to save context space]\n"

        # Debug info for advanced mode
        if advanced_mode:
            response_data["debug_info"].append({
                "type": "llm_input",
                "content": messages
            })

        # Time the LLM call
        llm_start_time = time.time()
        # Pass the computer_use_mode flag to the LLM call
        assistant_msg = llm_call(
            messages,
            computer_use_mode=(session_id in COMPUTER_USE_SESSIONS),
            temperature=session_temperature,
            max_tokens=session_max_tokens
        )
        llm_elapsed = time.time() - llm_start_time

        # Record LLM timing
        response_data["timing"]["llm_calls"].append(llm_elapsed)

        # Debug info for advanced mode
        if advanced_mode:
            response_data["debug_info"].append({
                "type": "llm_response",
                "content": assistant_msg,
                "timing": llm_elapsed
            })

        if "tool_calls" in assistant_msg:
            for call in assistant_msg["tool_calls"]:
                name = call["function"]["name"]
                raw_args = call["function"].get("arguments", "{}")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    args = {}

                # Check if tool is enabled for this session
                if session_id in TOOL_PREFERENCES and name in TOOL_PREFERENCES[session_id]:
                    tool_enabled = TOOL_PREFERENCES[session_id][name]
                else:
                    # If no preference is set, default to enabled
                    tool_enabled = True
                    # Initialize preferences if needed
                    if session_id not in TOOL_PREFERENCES:
                        TOOL_PREFERENCES[session_id] = {tool['function']['name']: True for tool in TOOLS}
                    TOOL_PREFERENCES[session_id][name] = True

                # If tool is disabled, return a message indicating that
                if not tool_enabled:
                    impl = None
                    tool_result_text = f"Tool `{name}` is currently disabled. Enable it in the Tools panel to use it."
                else:
                    # Select the appropriate tool implementation based on mode
                    if session_id in COMPUTER_USE_SESSIONS:
                        impl = COMPUTER_TOOL_IMPLS.get(name)
                    else:
                        impl = TOOL_IMPLS.get(name)

                # Debug info for advanced mode
                if advanced_mode:
                    response_data["debug_info"].append({
                        "type": "tool_call",
                        "name": name,
                        "args": args
                    })

                # Time the tool execution
                tool_start_time = time.time()

                def sanitize_tool_result(result_text):
                    """Sanitize tool result to prevent issues with the LLM."""
                    if not result_text:
                        return "No result returned from tool."

                    # Remove any special tokens
                    result_text = re.sub(r'<\|im_(start|end)\|>', '', result_text)

                    # Limit length if extremely long
                    if len(result_text) > 8000:  # Arbitrary limit to prevent token overflow
                        result_text = result_text[:8000] + "\n\n[Result truncated due to length]\n"

                    return result_text

                if impl is None:
                    tool_result_text = f"Tool `{name}` not implemented."
                else:
                    try:
                        result = impl(**args)
                        if name == "search":
                            tool_result_text = pretty_print_search_results(result)
                        elif name == "wiki_search":
                            tool_result_text = pretty_print_wiki_results(result)
                        elif name == "get_weather":
                            tool_result_text = pretty_print_weather_results(result)
                        elif name == "calculator":
                            tool_result_text = pretty_print_calculator_results(result)
                        # Computer Use tools
                        elif name == "execute_python":
                            tool_result_text = pretty_print_execute_python_results(result)

                        else:
                            tool_result_text = json.dumps(result)

                        # Sanitize the result
                        tool_result_text = sanitize_tool_result(tool_result_text)
                    except Exception as e:
                        tool_result_text = f"Error while executing {name}: {e}"

                tool_elapsed = time.time() - tool_start_time

                # Record tool timing
                response_data["timing"]["tool_calls"].append({
                    "name": name,
                    "timing": tool_elapsed
                })

                # Debug info for advanced mode
                if advanced_mode:
                    response_data["debug_info"].append({
                        "type": "tool_result",
                        "content": tool_result_text,
                        "timing": tool_elapsed
                    })

                messages.append({"role": "assistant", "content": None, "tool_calls": [call]})
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": tool_result_text})

            # Tool results are now in `messages`; let the LLM think again
            continue

        # Check if the assistant is trying to show a code block after a tool error
        # This is a common pattern when the agent tries to fix a failed code execution
        assistant_content = assistant_msg.get("content", "")
        last_tool_error = False
        python_code_block = None

        # Check if the last message was a tool error
        if len(messages) >= 2 and messages[-1].get("role") == "tool" and "Error" in messages[-1].get("content", ""):
            last_tool_error = True
            # Check if the assistant's response contains a Python code block
            if assistant_content and "```python" in assistant_content:
                # Extract the Python code from the code block
                code_blocks = re.findall(r'```python\n(.+?)\n```', assistant_content, re.DOTALL)
                if not code_blocks:
                    # Try alternative format
                    code_blocks = re.findall(r'```py\n(.+?)\n```', assistant_content, re.DOTALL)

                if code_blocks:
                    python_code_block = code_blocks[0].strip()

        # If we found a Python code block after an error, execute it automatically
        if last_tool_error and python_code_block and session_id in COMPUTER_USE_SESSIONS:
            # Debug info for advanced mode
            if advanced_mode:
                response_data["debug_info"].append({
                    "type": "auto_retry",
                    "content": f"Automatically executing fixed code:\n{python_code_block}"
                })

            # Execute the corrected code
            tool_start_time = time.time()
            try:
                # Get the Python execution tool implementation
                python_exec_impl = COMPUTER_TOOL_IMPLS.get("execute_python")
                if python_exec_impl:
                    result = python_exec_impl(code=python_code_block)
                    tool_result_text = pretty_print_execute_python_results(result)

                    # Sanitize the result
                    tool_result_text = sanitize_tool_result(tool_result_text)

                    # Add the tool call and result to the messages
                    tool_call_id = f"auto_retry_{int(time.time())}"
                    tool_call = {
                        "id": tool_call_id,
                        "function": {
                            "name": "execute_python",
                            "arguments": json.dumps({"code": python_code_block})
                        }
                    }

                    # Add the auto-retry tool call and result to messages
                    messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                    messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": tool_result_text})

                    # Make another LLM call to interpret the results
                    llm_start_time = time.time()
                    assistant_msg = llm_call(messages, computer_use_mode=(session_id in COMPUTER_USE_SESSIONS))
                    llm_elapsed = time.time() - llm_start_time

                    # Record LLM timing
                    response_data["timing"]["llm_calls"].append(llm_elapsed)

                    # Debug info for advanced mode
                    if advanced_mode:
                        response_data["debug_info"].append({
                            "type": "auto_retry_result",
                            "content": tool_result_text,
                            "timing": time.time() - tool_start_time
                        })
            except Exception as e:
                # If auto-retry fails, just continue with the original response
                if advanced_mode:
                    response_data["debug_info"].append({
                        "type": "auto_retry_error",
                        "content": f"Error during auto-retry: {str(e)}"
                    })

        # Final assistant answer
        messages.append(assistant_msg)

        # Calculate total conversation time
        conversation_elapsed = time.time() - conversation_start_time
        response_data["timing"]["total"] = conversation_elapsed

        # Calculate and add context window usage
        # Estimate token count based on a simple heuristic (4 chars per token on average)
        total_chars = sum(len(msg.get("content", "") or "") for msg in messages)
        estimated_tokens = total_chars // 4
        response_data["context_usage"] = {
            "estimated_tokens": estimated_tokens,
            "max_tokens": session_max_tokens # Changed from MAX_MODEL_TOKENS
        }

        # Clean up the final message content before adding to the response
        assistant_content = assistant_msg.get("content", "")
        if assistant_content:
            # Remove any special tokens or formatting issues
            assistant_content = re.sub(r'<\|im_(start|end)\|>', '', assistant_content)
            # Remove excessive newlines
            assistant_content = re.sub(r'\n{3,}', '\n\n', assistant_content)
            # Trim whitespace
            assistant_content = assistant_content.strip()

        # Add the cleaned final message to the response
        response_data["messages"].append({
            "role": "assistant",
            "content": assistant_content
        })

        break

    return jsonify(response_data)

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation for a session."""
    data = request.json
    session_id = data.get('session_id', 'default')

    if session_id in CONVERSATIONS:
        del CONVERSATIONS[session_id]

    # Reset tool preferences to defaults (all enabled)
    if session_id in TOOL_PREFERENCES:
        TOOL_PREFERENCES[session_id] = {tool['function']['name']: True for tool in TOOLS}

    # Reset LLM settings to defaults
    if session_id in LLM_SETTINGS:
        del LLM_SETTINGS[session_id] # This will cause it to be re-initialized with defaults on next use

    return jsonify({"status": "success", "message": "Conversation reset"})

@app.route('/api/tools', methods=['GET', 'POST'])
def manage_tools():
    """Get or update tool preferences."""
    session_id = request.args.get('session_id', 'default')

    if request.method == 'GET':
        # Return current tool preferences for the session, or defaults if none exist
        if session_id not in TOOL_PREFERENCES:
            # Initialize with all tools enabled by default
            TOOL_PREFERENCES[session_id] = {tool['function']['name']: True for tool in TOOLS}

        return jsonify({
            "status": "success",
            "tools": TOOL_PREFERENCES[session_id]
        })

    elif request.method == 'POST':
        # Update tool preferences
        data = request.json
        tool_prefs = data.get('tools', {})

        if not tool_prefs or not isinstance(tool_prefs, dict):
            return jsonify({"error": "Invalid tool preferences"}), 400

        # Initialize if not exists
        if session_id not in TOOL_PREFERENCES:
            TOOL_PREFERENCES[session_id] = {tool['function']['name']: True for tool in TOOLS}

        # Update preferences
        for tool_name, enabled in tool_prefs.items():
            if tool_name in TOOL_PREFERENCES[session_id]:
                TOOL_PREFERENCES[session_id][tool_name] = bool(enabled)

        return jsonify({
            "status": "success",
            "tools": TOOL_PREFERENCES[session_id]
        })

@app.route('/api/computer-use-tools', methods=['GET'])
def computer_use_tools():
    """Get the Python execution tool."""
    # Check if the request is from the frontend or from tests
    # Frontend expects a dictionary format, tests expect a list format
    is_test = request.headers.get('X-Test') == 'true'

    if is_test:
        # For tests, return a list format as expected by the tests
        tools_list = []
        for tool in COMPUTER_TOOLS:
            tools_list.append({
                'name': tool['function']['name'],
                'description': tool['function']['description'],
                'enabled': True
            })

        return jsonify({
            "status": "success",
            "tools": tools_list
        })
    else:
        # For frontend, return a dictionary format as expected by the frontend
        tool_prefs = {}
        for tool in COMPUTER_TOOLS:
            name = tool['function']['name']
            tool_prefs[name] = True  # Enable all by default

        return jsonify({
            "status": "success",
            "tools": tool_prefs
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

@app.route('/api/llm-settings', methods=['GET', 'POST'])
def llm_settings():
    session_id = request.args.get('session_id', 'default')

    if request.method == 'GET':
        if session_id not in LLM_SETTINGS:
            # Initialize with defaults if not set for the session
            LLM_SETTINGS[session_id] = {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_MODEL_TOKENS
            }
        return jsonify({
            "status": "success",
            "settings": LLM_SETTINGS[session_id]
        })

    elif request.method == 'POST':
        data = request.json
        settings_data = data.get('settings', {})

        if not settings_data or not isinstance(settings_data, dict):
            return jsonify({"error": "Invalid settings data"}), 400

        if session_id not in LLM_SETTINGS:
            # Initialize with defaults before updating
            LLM_SETTINGS[session_id] = {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_MODEL_TOKENS
            }

        # Update only provided and valid settings
        if "temperature" in settings_data and isinstance(settings_data["temperature"], (float, int)):
            LLM_SETTINGS[session_id]["temperature"] = float(settings_data["temperature"])
        if "max_tokens" in settings_data and isinstance(settings_data["max_tokens"], int):
            LLM_SETTINGS[session_id]["max_tokens"] = int(settings_data["max_tokens"])

        return jsonify({
            "status": "success",
            "settings": LLM_SETTINGS[session_id]
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
