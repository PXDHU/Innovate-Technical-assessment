// ===================================
// HITL CHAT FUNCTIONALITY
// ===================================

/**
 * HITL Chat State
 */
const hitlChatState = {
    currentValidation: null,
    missingAttributes: [],
    currentQuestionIndex: 0,
    responses: {},
    isWaitingForResponse: false
};

/**
 * Attribute labels and placeholders for better UX
 */
const attributeInfo = {
    'standard': {
        label: 'IEC Standard',
        placeholder: 'e.g., IEC 60502-1',
        question: 'Please provide the IEC standard (e.g., IEC 60502-1):'
    },
    'voltage': {
        label: 'Voltage Rating',
        placeholder: 'e.g., 0.6/1 kV',
        question: 'Please provide the voltage rating (e.g., 0.6/1 kV):'
    },
    'conductor_material': {
        label: 'Conductor Material',
        placeholder: 'Cu or Al',
        question: 'Please provide the conductor material (Cu or Al):'
    },
    'conductor_class': {
        label: 'Conductor Class',
        placeholder: 'Class 1 or Class 2',
        question: 'Please provide the conductor class (Class 1 or Class 2):'
    },
    'csa': {
        label: 'Cross-Sectional Area',
        placeholder: 'e.g., 10',
        question: 'Please provide the cross-sectional area in mm² (e.g., 10):'
    },
    'insulation_material': {
        label: 'Insulation Material',
        placeholder: 'PVC, XLPE, or EPR',
        question: 'Please provide the insulation material (PVC, XLPE, or EPR):'
    },
    'insulation_thickness': {
        label: 'Insulation Thickness',
        placeholder: 'e.g., 1.0',
        question: 'Please provide the insulation thickness in mm (e.g., 1.0):'
    }
};

/**
 * Initialize HITL chat with validation data
 */
function initHitlChat(validation) {
    hitlChatState.currentValidation = validation;
    hitlChatState.missingAttributes = validation.missing_attributes || [];
    hitlChatState.currentQuestionIndex = 0;
    hitlChatState.responses = {};
    hitlChatState.isWaitingForResponse = false;

    // Show chat section
    const chatSection = document.getElementById('hitl-chat-section');
    const chatMessages = document.getElementById('hitl-chat-messages');
    const chatInputContainer = document.getElementById('hitl-chat-input-container');
    const chatInput = document.getElementById('hitl-chat-input');

    chatSection.style.display = 'block';
    chatMessages.innerHTML = '';

    // Add initial message
    addChatMessage('ai', `I've detected ${hitlChatState.missingAttributes.length} missing attributes that are required for validation. Let me ask you about them one by one.`);

    // Small delay before asking first question
    setTimeout(() => {
        askNextQuestion();
    }, 800);
}

/**
 * Add a message to the chat
 */
function addChatMessage(type, text, label = null) {
    const chatMessages = document.getElementById('hitl-chat-messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;

    if (label) {
        const labelSpan = document.createElement('span');
        labelSpan.className = 'chat-label';
        labelSpan.textContent = label;
        messageDiv.appendChild(labelSpan);
    }

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'chat-bubble';
    bubbleDiv.textContent = text;

    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    const chatContainer = document.getElementById('hitl-chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Add typing indicator
 */
function addTypingIndicator() {
    const chatMessages = document.getElementById('hitl-chat-messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message typing ai';
    messageDiv.id = 'typing-indicator';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'chat-bubble';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';

    bubbleDiv.appendChild(typingDiv);
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    const chatContainer = document.getElementById('hitl-chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

/**
 * Ask the next question
 */
function askNextQuestion() {
    if (hitlChatState.currentQuestionIndex >= hitlChatState.missingAttributes.length) {
        // All questions answered
        completeHitlChat();
        return;
    }

    const attribute = hitlChatState.missingAttributes[hitlChatState.currentQuestionIndex];
    const info = attributeInfo[attribute] || {
        question: `Please provide the ${attribute}:`,
        label: attribute
    };

    // Show typing indicator
    addTypingIndicator();

    setTimeout(() => {
        removeTypingIndicator();
        addChatMessage('ai', info.question, 'System');

        // Show input field
        const chatInputContainer = document.getElementById('hitl-chat-input-container');
        const chatInput = document.getElementById('hitl-chat-input');
        chatInputContainer.style.display = 'block';
        chatInput.placeholder = info.placeholder || `Enter ${info.label}`;
        chatInput.focus();

        hitlChatState.isWaitingForResponse = true;
    }, 600);
}

/**
 * Handle user response
 */
function handleChatResponse(response) {
    if (!hitlChatState.isWaitingForResponse) {
        return;
    }

    const attribute = hitlChatState.missingAttributes[hitlChatState.currentQuestionIndex];
    const info = attributeInfo[attribute] || { label: attribute };

    // Add user message
    addChatMessage('user', response, 'You');

    // Store response
    hitlChatState.responses[attribute] = response;

    // Hide input temporarily
    const chatInputContainer = document.getElementById('hitl-chat-input-container');
    chatInputContainer.style.display = 'none';
    hitlChatState.isWaitingForResponse = false;

    // Show confirmation
    setTimeout(() => {
        addChatMessage('ai', `✓ Got it! ${info.label}: ${response}`, 'System');

        // Move to next question
        hitlChatState.currentQuestionIndex++;
        setTimeout(() => {
            askNextQuestion();
        }, 800);
    }, 400);
}

/**
 * Complete HITL chat and show submit button
 */
function completeHitlChat() {
    const chatInputContainer = document.getElementById('hitl-chat-input-container');
    const chatComplete = document.getElementById('hitl-chat-complete');

    chatInputContainer.style.display = 'none';

    // Show completion message
    addTypingIndicator();
    setTimeout(() => {
        removeTypingIndicator();
        addChatMessage('ai', `Perfect! I've collected all the information. Click the button below to submit your responses and complete the validation.`, 'System');

        // Show submit button
        chatComplete.style.display = 'block';
    }, 600);
}

/**
 * Submit all HITL responses
 */
async function submitAllHitlResponses() {
    const submitBtn = document.getElementById('submit-all-hitl-btn');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
        updateWorkflow('validate', 'active');

        // Submit HITL responses
        const result = await submitHitlResponses(
            hitlChatState.currentValidation.validation_id,
            hitlChatState.responses
        );

        // Complete workflow
        updateWorkflow('complete', 'active');
        await new Promise(resolve => setTimeout(resolve, 300));

        // Hide chat section
        document.getElementById('hitl-chat-section').style.display = 'none';

        // Display updated results
        displayResults(result);

        // Refresh history
        await loadHistory();

        showToast('HITL responses submitted successfully! ✓', 'success');

    } catch (error) {
        console.error('HITL submission error:', error);
        showToast(error.message || 'HITL submission failed', 'error');
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
}

// ===================================
// EVENT LISTENERS
// ===================================

// Initialize chat form handler when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('hitl-chat-form');
    const chatInput = document.getElementById('hitl-chat-input');
    const submitAllBtn = document.getElementById('submit-all-hitl-btn');

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const response = chatInput.value.trim();
            if (response) {
                handleChatResponse(response);
                chatInput.value = '';
            }
        });
    }

    if (submitAllBtn) {
        submitAllBtn.addEventListener('click', submitAllHitlResponses);
    }
});
