// Constants
const API_BASE_URL = 'http://localhost:5000/api';
const SESSION_ID_KEY = 'mcp_session_id';
const TOOL_PREFERENCES_KEY = 'tool_preferences';
const COMPUTER_USE_MODE_KEY = 'computer_use_mode';

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const resetButton = document.getElementById('reset-button');
const modeSwitch = document.getElementById('mode-switch');
const debugPanel = document.getElementById('debug-panel');
const debugContent = document.getElementById('debug-content');
const clearDebugButton = document.getElementById('clear-debug');
const timingPanel = document.getElementById('timing-panel');
const timingContent = document.getElementById('timing-content');
const statusElement = document.getElementById('status');
const toolsButton = document.getElementById('tools-button');
const toolsPanel = document.getElementById('tools-panel');
const toolsContent = document.getElementById('tools-content');
const computerUseButton = document.getElementById('computer-use-button');

// State
let isAdvancedMode = false;
let isProcessing = false;
let isToolsPanelVisible = false;
let isComputerUseMode = false;
let sessionId = getOrCreateSessionId();
let toolPreferences = {}; // Will store tool preferences

// Event Listeners
document.addEventListener('DOMContentLoaded', initializeApp);
sendButton.addEventListener('click', handleSendMessage);
userInput.addEventListener('keydown', handleInputKeydown);
resetButton.addEventListener('click', resetConversation);
modeSwitch.addEventListener('change', toggleAdvancedMode);
clearDebugButton.addEventListener('click', clearDebugInfo);
toolsButton.addEventListener('click', toggleToolsPanel);
computerUseButton.addEventListener('click', toggleComputerUseMode);

// Initialize the application
function initializeApp() {
    // Check if advanced mode was previously enabled
    const savedMode = localStorage.getItem('advanced_mode');
    if (savedMode === 'true') {
        modeSwitch.checked = true;
        toggleAdvancedMode();
    }

    // Check if tools panel was previously visible
    const savedToolsPanel = localStorage.getItem('tools_panel_visible');
    if (savedToolsPanel === 'true') {
        toggleToolsPanel();
    }

    // Check if Computer Use mode was previously enabled
    const savedComputerUseMode = localStorage.getItem(COMPUTER_USE_MODE_KEY);
    if (savedComputerUseMode === 'true') {
        toggleComputerUseMode();
    }

    // Focus on input
    userInput.focus();

    // Check API health
    checkApiHealth();

    // Load tool preferences
    loadToolPreferences();

    // Initialize highlight.js
    hljs.configure({
        ignoreUnescapedHTML: true
    });
}

// Get or create a session ID
function getOrCreateSessionId() {
    let id = localStorage.getItem(SESSION_ID_KEY);
    if (!id) {
        id = generateSessionId();
        localStorage.setItem(SESSION_ID_KEY, id);
    }
    return id;
}

// Generate a random session ID
function generateSessionId() {
    return 'session_' + Math.random().toString(36).substring(2, 15);
}

// Toggle advanced mode
function toggleAdvancedMode() {
    isAdvancedMode = modeSwitch.checked;
    document.body.classList.toggle('advanced-mode', isAdvancedMode);
    localStorage.setItem('advanced_mode', isAdvancedMode);

    // Show/hide debug panels
    debugPanel.style.display = isAdvancedMode ? 'block' : 'none';
    timingPanel.style.display = isAdvancedMode ? 'block' : 'none';
}

// Clear debug information
function clearDebugInfo() {
    debugContent.innerHTML = '';
}

// Handle input keydown (for Enter key)
function handleInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
}

// Handle sending a message
async function handleSendMessage() {
    const message = userInput.value.trim();
    if (!message || isProcessing) return;

    // Add user message to chat
    addMessageToChat('user', message);

    // Clear input
    userInput.value = '';

    // Process the message
    await processMessage(message);
}

// Process a message by sending it to the API
async function processMessage(message) {
    setProcessingState(true);

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message,
                session_id: sessionId,
                advanced_mode: isAdvancedMode,
                computer_use_mode: isComputerUseMode,
                tool_preferences: toolPreferences
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Process the response
        processResponse(data);
    } catch (error) {
        console.error('Error processing message:', error);
        addMessageToChat('system', `Error: ${error.message}`);
        setStatusMessage(`Error: ${error.message}`, 'error');
    } finally {
        setProcessingState(false);
    }
}

// Process the API response
function processResponse(data) {
    // Add assistant messages to chat
    data.messages.forEach(msg => {
        if (msg.role === 'assistant') {
            addMessageToChat('assistant', msg.content);
        }
    });

    // Display timing information in advanced mode
    if (isAdvancedMode && data.timing) {
        displayTimingInfo(data.timing);
    }

    // Display debug information in advanced mode
    if (isAdvancedMode && data.debug_info) {
        displayDebugInfo(data.debug_info);
    }

    // Set status message
    setStatusMessage('Ready');

    // Scroll to bottom
    scrollToBottom();
}

// Add a message to the chat
function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Process markdown-like content (simple version)
    const formattedContent = formatContent(content);
    contentDiv.innerHTML = formattedContent;

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString();

    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);

    chatMessages.appendChild(messageDiv);

    // Apply syntax highlighting to code blocks
    contentDiv.querySelectorAll('pre code').forEach((block) => {
        try {
            hljs.highlightElement(block);

            // Add language label if available
            const language = block.className.match(/language-(\w+)/);
            if (language && language[1] && language[1] !== 'plaintext') {
                const pre = block.parentElement;
                const langLabel = document.createElement('div');
                langLabel.className = 'code-language';
                langLabel.textContent = language[1];
                pre.appendChild(langLabel);
            }
        } catch (e) {
            console.error('Syntax highlighting error:', e);
        }
    });

    // Render LaTeX expressions
    // Inline LaTeX
    contentDiv.querySelectorAll('.latex-inline').forEach((element) => {
        try {
            const latex = decodeURIComponent(element.getAttribute('data-latex'));
            // Clear the element content before rendering
            element.textContent = '';
            window.katex.render(latex, element, {
                throwOnError: false,
                displayMode: false
            });
        } catch (e) {
            console.error('LaTeX rendering error:', e);
            // Restore the original content if rendering fails
            element.textContent = '$' + decodeURIComponent(element.getAttribute('data-latex')) + '$';
        }
    });

    // Display LaTeX
    contentDiv.querySelectorAll('.latex-display').forEach((element) => {
        try {
            const latex = decodeURIComponent(element.getAttribute('data-latex'));
            // Clear the element content before rendering
            element.textContent = '';
            window.katex.render(latex, element, {
                throwOnError: false,
                displayMode: true
            });
        } catch (e) {
            console.error('LaTeX rendering error:', e);
            // Restore the original content if rendering fails
            element.textContent = '$$' + decodeURIComponent(element.getAttribute('data-latex')) + '$$';
        }
    });

    scrollToBottom();
}

// Clean up content from problematic tokens
function cleanContent(content) {
    if (!content) return '';

    // Remove any special tokens that might appear in the response
    content = content.replace(/<\|im_(start|end)\|>/g, '');

    // Remove any repeated newlines (more than 2)
    content = content.replace(/\n{3,}/g, '\n\n');

    // Trim whitespace
    content = content.trim();

    return content;
}

// Format content with markdown-like syntax
function formatContent(content) {
    if (!content) return '';

    // First clean up the content
    content = cleanContent(content);

    // Store code blocks and LaTeX expressions to prevent conflicts with other formatting
    const codeBlocks = [];
    const inlineCodeBlocks = [];
    const latexInline = [];
    const latexDisplay = [];

    // Extract code blocks first
    content = content.replace(/```(\w*)([\s\S]*?)```/g, (_, lang, code) => {
        const id = `CODE_BLOCK_${codeBlocks.length}`;
        codeBlocks.push({ id, lang: lang || 'plaintext', code: code.trim() });
        return id;
    });

    // Extract inline code
    content = content.replace(/`([^`]+)`/g, (_, code) => {
        const id = `INLINE_CODE_${inlineCodeBlocks.length}`;
        inlineCodeBlocks.push({ id, code });
        return id;
    });

    // Extract LaTeX expressions
    // Display LaTeX: $$...$$
    content = content.replace(/\$\$(.*?)\$\$/g, (_, latex) => {
        const id = `LATEX_DISPLAY_${latexDisplay.length}`;
        latexDisplay.push({ id, latex });
        return id;
    });

    // Inline LaTeX: $...$
    content = content.replace(/\$(.*?)\$/g, (_, latex) => {
        const id = `LATEX_INLINE_${latexInline.length}`;
        latexInline.push({ id, latex });
        return id;
    });

    // Convert line breaks to paragraphs
    let formatted = content.split('\n\n').map(para => {
        if (para.trim() === '') return '';
        return `<p>${para}</p>`;
    }).join('');

    // Convert single line breaks within paragraphs
    formatted = formatted.replace(/<p>(.*?)\n(.*?)<\/p>/g, '<p>$1<br>$2</p>');

    // Format bold text
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Format italic text
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Restore code blocks with syntax highlighting
    codeBlocks.forEach(({ id, lang, code }) => {
        formatted = formatted.replace(id, `<pre><code class="language-${lang}">${code}</code></pre>`);
    });

    // Restore inline code
    inlineCodeBlocks.forEach(({ id, code }) => {
        formatted = formatted.replace(id, `<code>${code}</code>`);
    });

    // Restore LaTeX expressions
    // Inline LaTeX
    latexInline.forEach(({ id, latex }) => {
        formatted = formatted.replace(id, `<span class="latex-inline" data-latex="${encodeURIComponent(latex)}">$${latex}$</span>`);
    });

    // Display LaTeX
    latexDisplay.forEach(({ id, latex }) => {
        formatted = formatted.replace(id, `<span class="latex-display" data-latex="${encodeURIComponent(latex)}">$$${latex}$$</span>`);
    });

    return formatted;
}

// Display timing information
function displayTimingInfo(timing) {
    let html = `<div>Total processing time: ${timing.total.toFixed(2)}s</div>`;

    if (timing.llm_calls && timing.llm_calls.length > 0) {
        html += '<div>LLM calls:</div><ul>';
        timing.llm_calls.forEach((time, index) => {
            html += `<li>Call ${index + 1}: ${time.toFixed(2)}s</li>`;
        });
        html += '</ul>';
    }

    if (timing.tool_calls && timing.tool_calls.length > 0) {
        html += '<div>Tool calls:</div><ul>';
        timing.tool_calls.forEach(tool => {
            html += `<li>${tool.name}: ${tool.timing.toFixed(2)}s</li>`;
        });
        html += '</ul>';
    }

    timingContent.innerHTML = html;
}

// Display debug information
function displayDebugInfo(debugInfo) {
    let html = '';

    debugInfo.forEach(info => {
        const type = info.type;
        let content = '';

        switch (type) {
            case 'llm_input':
                content = `<div class="debug-item">
                    <div class="debug-header">LLM Input:</div>
                    <pre>${JSON.stringify(info.content, null, 2)}</pre>
                </div>`;
                break;
            case 'llm_response':
                content = `<div class="debug-item">
                    <div class="debug-header">LLM Response (${info.timing.toFixed(2)}s):</div>
                    <pre>${JSON.stringify(info.content, null, 2)}</pre>
                </div>`;
                break;
            case 'tool_call':
                content = `<div class="debug-item">
                    <div class="debug-header">Tool Call: ${info.name}</div>
                    <pre>${JSON.stringify(info.args, null, 2)}</pre>
                </div>`;
                break;
            case 'tool_result':
                content = `<div class="debug-item">
                    <div class="debug-header">Tool Result (${info.timing.toFixed(2)}s):</div>
                    <pre>${info.content}</pre>
                </div>`;
                break;
        }

        html += content;
    });

    debugContent.innerHTML += html;
}

// Set the processing state
function setProcessingState(processingState) {
    isProcessing = processingState;
    sendButton.disabled = processingState;
    userInput.disabled = processingState;

    if (processingState) {
        setStatusMessage('Processing...', 'loading');
    } else {
        setStatusMessage('Ready');
    }
}

// Set a status message
function setStatusMessage(message, type = 'info') {
    statusElement.textContent = message;
    statusElement.className = 'status ' + type;
}

// Reset the conversation
async function resetConversation(updateUI = true) {
    try {
        const response = await fetch(`${API_BASE_URL}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        // Only update UI if requested (default is true)
        if (updateUI) {
            // Set appropriate welcome message based on mode
            if (isComputerUseMode) {
                chatMessages.innerHTML = `
                    <div class="message system">
                        <div class="message-content">
                            <p><strong>Computer Use Mode Activated</strong></p>
                            <p>You can now control your computer using Python. The agent has access to tools for executing Python code, getting system information, listing files, and reading files.</p>
                            <p>Example commands:</p>
                            <ul>
                                <li>"What's my current system information?"</li>
                                <li>"List the files in my current directory"</li>
                                <li>"Read the contents of a specific file"</li>
                                <li>"Execute some Python code to automate a task"</li>
                            </ul>
                            <p><small>Note: Be careful when executing code that modifies your system. The agent has safety measures but use with caution.</small></p>
                        </div>
                    </div>
                `;
            } else {
                // Standard welcome message
                chatMessages.innerHTML = `
                    <div class="message system">
                        <div class="message-content">
                            <p>Welcome to MCP Agent! How can I help you today?</p>
                            <p><small>Note: This application uses a local LLM which may occasionally produce unexpected responses. If you receive strange output, try asking your question again or resetting the conversation.</small></p>
                        </div>
                    </div>
                `;
            }

            // Clear debug and timing info
            if (isAdvancedMode) {
                debugContent.innerHTML = '';
                timingContent.innerHTML = '';
            }

            // Reset tool preferences
            loadToolPreferences();

            setStatusMessage('Conversation reset');
        }
    } catch (error) {
        console.error('Error resetting conversation:', error);
        setStatusMessage(`Error: ${error.message}`, 'error');
    }
}

// Check API health
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            setStatusMessage('Connected to API');
        } else {
            setStatusMessage('API connection issue', 'warning');
        }
    } catch (error) {
        console.error('API health check failed:', error);
        setStatusMessage('API not available', 'error');
    }
}

// Scroll chat to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Toggle tools panel visibility
function toggleToolsPanel() {
    isToolsPanelVisible = !isToolsPanelVisible;
    document.body.classList.toggle('tools-visible', isToolsPanelVisible);
    localStorage.setItem('tools_panel_visible', isToolsPanelVisible);

    // If we're showing the panel and haven't loaded tools yet, load them
    if (isToolsPanelVisible && toolsContent.children.length === 0) {
        loadToolPreferences();
    }
}

// Toggle Computer Use mode
function toggleComputerUseMode() {
    isComputerUseMode = !isComputerUseMode;
    computerUseButton.classList.toggle('active', isComputerUseMode);
    localStorage.setItem(COMPUTER_USE_MODE_KEY, isComputerUseMode);

    // Update the welcome message based on mode
    if (isComputerUseMode) {
        // Clear chat messages except for a new welcome message
        chatMessages.innerHTML = `
            <div class="message system">
                <div class="message-content">
                    <p><strong>Computer Use Mode Activated</strong></p>
                    <p>You can now control your computer using Python. The agent has access to tools for executing Python code, getting system information, listing files, and reading files.</p>
                    <p>Example commands:</p>
                    <ul>
                        <li>"What's my current system information?"</li>
                        <li>"List the files in my current directory"</li>
                        <li>"Read the contents of a specific file"</li>
                        <li>"Execute some Python code to automate a task"</li>
                    </ul>
                    <p><small>Note: Be careful when executing code that modifies your system. The agent has safety measures but use with caution.</small></p>
                </div>
            </div>
        `;
        setStatusMessage('Computer Use Mode Activated');
    } else {
        // Return to normal mode
        chatMessages.innerHTML = `
            <div class="message system">
                <div class="message-content">
                    <p>Welcome to MCP Agent! How can I help you today?</p>
                    <p><small>Note: This application uses a local LLM which may occasionally produce unexpected responses. If you receive strange output, try asking your question again or resetting the conversation.</small></p>
                </div>
            </div>
        `;
        setStatusMessage('Computer Use Mode Deactivated');
    }

    // Reset conversation on the server
    resetConversation(false); // Don't update UI again

    // Clear and reload the tools panel to show the appropriate tools for the current mode
    if (isToolsPanelVisible) {
        // Clear existing tools
        toolsContent.innerHTML = '';
        // Load the appropriate tools for the current mode
        loadToolPreferences();
    }
}

// Load tool preferences from the server
async function loadToolPreferences() {
    try {
        // Determine which endpoint to use based on mode
        let endpoint = `${API_BASE_URL}/tools?session_id=${sessionId}`;

        // If in Computer Use mode, get the Computer Use tools instead
        if (isComputerUseMode) {
            endpoint = `${API_BASE_URL}/computer-use-tools`;
        }

        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        if (data.status === 'success') {
            if (isComputerUseMode && data.tools) {
                // For Computer Use mode, we get a list of tools with names and descriptions
                // Convert to the format expected by renderToolsPanel
                toolPreferences = {};
                data.tools.forEach(tool => {
                    toolPreferences[tool.name] = true; // Enable all by default
                });
            } else if (data.tools) {
                // For regular mode, we get the existing preferences
                toolPreferences = data.tools;
            }

            // Save to localStorage
            localStorage.setItem(TOOL_PREFERENCES_KEY, JSON.stringify(toolPreferences));

            // Render the tools panel
            renderToolsPanel(toolPreferences);
        }
    } catch (error) {
        console.error('Error loading tool preferences:', error);
        setStatusMessage(`Error: ${error.message}`, 'error');
    }
}

// Render the tools panel with toggles
function renderToolsPanel(tools) {
    // Clear existing content
    toolsContent.innerHTML = '';

    // Create a toggle for each tool
    Object.entries(tools).forEach(([toolName, isEnabled]) => {
        const toolItem = document.createElement('div');
        toolItem.className = 'tool-item';

        // Get a user-friendly name and description
        const displayName = getToolDisplayName(toolName);
        const description = getToolDescription(toolName);

        // Create the tool info section
        const toolInfo = document.createElement('div');
        toolInfo.className = 'tool-info';

        const nameElement = document.createElement('div');
        nameElement.className = 'tool-name';
        nameElement.textContent = displayName;

        const descElement = document.createElement('div');
        descElement.className = 'tool-description';
        descElement.textContent = description;

        toolInfo.appendChild(nameElement);
        toolInfo.appendChild(descElement);

        // Create the toggle switch
        const toggleContainer = document.createElement('label');
        toggleContainer.className = 'switch';

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.checked = isEnabled;
        toggleInput.addEventListener('change', () => toggleTool(toolName, toggleInput.checked));

        const toggleSlider = document.createElement('span');
        toggleSlider.className = 'slider round';

        toggleContainer.appendChild(toggleInput);
        toggleContainer.appendChild(toggleSlider);

        // Add everything to the tool item
        toolItem.appendChild(toolInfo);
        toolItem.appendChild(toggleContainer);

        // Add to the tools panel
        toolsContent.appendChild(toolItem);
    });
}

// Toggle a specific tool on/off
async function toggleTool(toolName, isEnabled) {
    try {
        // Update local state
        toolPreferences[toolName] = isEnabled;

        // Save to localStorage
        localStorage.setItem(TOOL_PREFERENCES_KEY, JSON.stringify(toolPreferences));

        // Only send to server for general agent tools
        // Computer Use tools are managed locally only
        if (!isComputerUseMode) {
            const response = await fetch(`${API_BASE_URL}/tools?session_id=${sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tools: { [toolName]: isEnabled }
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
        }

        // Show a brief status message
        setStatusMessage(`Tool '${getToolDisplayName(toolName)}' ${isEnabled ? 'enabled' : 'disabled'}`);
        setTimeout(() => setStatusMessage('Ready'), 2000);

    } catch (error) {
        console.error('Error toggling tool:', error);
        setStatusMessage(`Error: ${error.message}`, 'error');
    }
}

// Get a user-friendly display name for a tool
function getToolDisplayName(toolName) {
    const displayNames = {
        // Standard tools
        'search': 'Web Search',
        'wiki_search': 'Wikipedia',
        'get_weather': 'Weather',
        'calculator': 'Calculator',

        // Computer Use tools
        'execute_python': 'Python Execution',
        'get_system_info': 'System Info',
        'list_files': 'File Explorer',
        'read_file': 'File Reader'
    };

    return displayNames[toolName] || toolName;
}

// Get a description for a tool
function getToolDescription(toolName) {
    const descriptions = {
        // Standard tools
        'search': 'Search the web using DuckDuckGo',
        'wiki_search': 'Search Wikipedia for information',
        'get_weather': 'Get weather information for a location',
        'calculator': 'Evaluate mathematical expressions',

        // Computer Use tools
        'execute_python': 'Execute Python code for computer control tasks',
        'get_system_info': 'Get information about your system',
        'list_files': 'List files and directories in a specified path',
        'read_file': 'Read the contents of a file'
    };

    return descriptions[toolName] || 'No description available';
}
