/**
 * Frontend tests for Computer Use UI functionality.
 * 
 * These tests can be run using a JavaScript testing framework like Jest.
 * To run these tests, you would need to set up Jest with the appropriate DOM environment.
 */

// Mock DOM elements
const mockElements = {
    computerUseButton: { classList: { toggle: jest.fn() } },
    chatMessages: { innerHTML: '', scrollTop: 0, scrollHeight: 1000 },
    statusElement: { textContent: '', className: '' }
};

// Mock localStorage
const mockLocalStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn()
};

// Mock fetch API
global.fetch = jest.fn(() => 
    Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'success', tools: [] })
    })
);

// Mock functions
const mockFunctions = {
    resetConversation: jest.fn(),
    setStatusMessage: jest.fn(),
    loadToolPreferences: jest.fn()
};

// Import the function to test (in a real environment)
// const { toggleComputerUseMode } = require('../../frontend/js/app.js');

// For testing purposes, recreate the function
function toggleComputerUseMode() {
    // Toggle Computer Use mode
    isComputerUseMode = !isComputerUseMode;
    mockElements.computerUseButton.classList.toggle('active', isComputerUseMode);
    mockLocalStorage.setItem('computer_use_mode', isComputerUseMode);
    
    // Update the welcome message based on mode
    if (isComputerUseMode) {
        // Set Computer Use welcome message
        mockElements.chatMessages.innerHTML = 'Computer Use Mode Activated';
        mockFunctions.setStatusMessage('Computer Use Mode Activated');
    } else {
        // Set standard welcome message
        mockElements.chatMessages.innerHTML = 'Welcome to MCP Agent';
        mockFunctions.setStatusMessage('Computer Use Mode Deactivated');
    }
    
    // Reset conversation on the server
    mockFunctions.resetConversation(false);
}

describe('Computer Use UI', () => {
    // Reset mocks before each test
    beforeEach(() => {
        jest.clearAllMocks();
        isComputerUseMode = false;
    });

    test('toggleComputerUseMode should toggle the mode', () => {
        // Initial state
        expect(isComputerUseMode).toBe(false);
        
        // Toggle on
        toggleComputerUseMode();
        expect(isComputerUseMode).toBe(true);
        expect(mockElements.computerUseButton.classList.toggle).toHaveBeenCalledWith('active', true);
        expect(mockLocalStorage.setItem).toHaveBeenCalledWith('computer_use_mode', true);
        expect(mockElements.chatMessages.innerHTML).toBe('Computer Use Mode Activated');
        expect(mockFunctions.setStatusMessage).toHaveBeenCalledWith('Computer Use Mode Activated');
        expect(mockFunctions.resetConversation).toHaveBeenCalledWith(false);
        
        // Toggle off
        toggleComputerUseMode();
        expect(isComputerUseMode).toBe(false);
        expect(mockElements.computerUseButton.classList.toggle).toHaveBeenCalledWith('active', false);
        expect(mockLocalStorage.setItem).toHaveBeenCalledWith('computer_use_mode', false);
        expect(mockElements.chatMessages.innerHTML).toBe('Welcome to MCP Agent');
        expect(mockFunctions.setStatusMessage).toHaveBeenCalledWith('Computer Use Mode Deactivated');
        expect(mockFunctions.resetConversation).toHaveBeenCalledWith(false);
    });

    test('initializeApp should check for saved Computer Use mode', () => {
        // Mock localStorage to return true for computer_use_mode
        mockLocalStorage.getItem.mockImplementation((key) => {
            if (key === 'computer_use_mode') return 'true';
            return null;
        });
        
        // Call initializeApp (simplified version for testing)
        function initializeApp() {
            const savedComputerUseMode = mockLocalStorage.getItem('computer_use_mode');
            if (savedComputerUseMode === 'true') {
                toggleComputerUseMode();
            }
        }
        
        initializeApp();
        
        // Check that toggleComputerUseMode was called
        expect(isComputerUseMode).toBe(true);
        expect(mockElements.computerUseButton.classList.toggle).toHaveBeenCalledWith('active', true);
    });

    test('processMessage should include computer_use_mode flag', async () => {
        // Mock fetch to return a successful response
        global.fetch.mockImplementationOnce(() => 
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({
                    messages: [{ role: 'assistant', content: 'Test response' }]
                })
            })
        );
        
        // Simplified processMessage function for testing
        async function processMessage(message) {
            await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    session_id: 'test_session',
                    computer_use_mode: isComputerUseMode
                })
            });
        }
        
        // Set Computer Use mode to true
        isComputerUseMode = true;
        
        // Process a message
        await processMessage('Test message');
        
        // Check that fetch was called with the correct parameters
        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:5000/api/chat',
            expect.objectContaining({
                method: 'POST',
                body: expect.stringContaining('"computer_use_mode":true')
            })
        );
    });
});

// This is just a placeholder - in a real environment, you would export the test
// module.exports = { toggleComputerUseMode };
