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
from tools import (TOOL_IMPLS, TOOLS, pretty_print_search_results,
                  pretty_print_wiki_results, pretty_print_weather_results,
                  pretty_print_calculator_results)

# Import Python execution tool
from computer_use import (COMPUTER_TOOLS, COMPUTER_TOOL_IMPLS,
                        pretty_print_execute_python_results)

app = Flask(__name__)
app.secret_key = "mcp-agent-secret-key"  # For session management
CORS(app)  # Enable CORS for all routes

# Session storage for conversations
CONVERSATIONS = {}

# Default tool preferences (all enabled by default)
TOOL_PREFERENCES = {}

# Computer Use mode sessions
COMPUTER_USE_SESSIONS = set()

def get_system_prompt() -> str:
    """Generate system prompt with current date and time information."""
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

    # Different prompts based on mode
    standard_prompt = (
        "You are an intelligent assistant. " + date_info +
        "If you need to perform a web search, Wikipedia search, get weather information, or perform calculations, "
        "call the appropriate tool. The calculator tool can evaluate mathematical expressions using math, numpy, and sympy libraries. "
        "Use as many tool calls as needed until you have the information required to answer the user conclusively."
    )

    computer_use_prompt = (
        "You are a Python code execution assistant. " + date_info +
        "Your primary function is to help users execute Python code. You can run any Python code using the execute_python tool. "
        "The code runs in a controlled environment with access to common libraries like os, sys, math, numpy, pandas, and matplotlib. "
        "You can help users with data analysis, visualization, automation tasks, and more through Python code execution."
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
        # Debug info for advanced mode
        if advanced_mode:
            response_data["debug_info"].append({
                "type": "llm_input",
                "content": messages[-5:] if len(messages) > 5 else messages
            })

        # Time the LLM call
        llm_start_time = time.time()
        # Pass the computer_use_mode flag to the LLM call
        assistant_msg = llm_call(messages, computer_use_mode=(session_id in COMPUTER_USE_SESSIONS))
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
                        # Python execution tool
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

        # Final assistant answer
        messages.append(assistant_msg)

        # Calculate total conversation time
        conversation_elapsed = time.time() - conversation_start_time
        response_data["timing"]["total"] = conversation_elapsed

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
    # Return the Python execution tool
    tools_info = []
    for tool in COMPUTER_TOOLS:
        name = tool['function']['name']
        description = tool['function']['description']
        tools_info.append({
            'name': name,
            'description': description
        })

    return jsonify({
        "status": "success",
        "tools": tools_info
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
