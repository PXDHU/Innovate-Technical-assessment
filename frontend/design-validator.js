// ===================================================================
// CABLE DESIGN VALIDATOR - JAVASCRIPT
// Complete HITL Workflow Implementation
// ===================================================================

const API_BASE_URL = 'http://localhost:8000';

// ===================================================================
// STATE MANAGEMENT
// ===================================================================
const state = {
    currentValidation: null,
    hitlMode: false,
    missingAttributes: [],
    hitlResponses: {},
    currentAttributeIndex: 0,
    originalUserInput: ''
};

// ===================================================================
// INITIALIZATION
// ===================================================================
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    setupSVGGradient();
});

function initializeEventListeners() {
    // Form submission
    document.getElementById('validation-form').addEventListener('submit', handleFormSubmit);

    // Drawer controls
    document.getElementById('reasoning-toggle')?.addEventListener('click', openReasoningDrawer);
    document.querySelector('.drawer-close')?.addEventListener('click', closeReasoningDrawer);
    document.querySelector('.drawer-overlay')?.addEventListener('click', closeReasoningDrawer);

    // HITL chat
    document.getElementById('hitl-chat-form')?.addEventListener('submit', handleHITLChatSubmit);
    document.getElementById('submit-all-hitl-btn')?.addEventListener('click', handleSubmitAllHITL);
}

// ===================================================================
// FORM SUBMISSION
// ===================================================================
async function handleFormSubmit(e) {
    e.preventDefault();

    const userInput = document.getElementById('user-input').value.trim();
    const hitlMode = document.getElementById('hitl-mode').checked;

    if (!userInput) {
        showToast('Please enter a cable design description', 'error');
        return;
    }

    await runValidation(userInput, hitlMode);
}

// ===================================================================
// VALIDATION API CALLS
// ===================================================================
async function runValidation(userInput, hitlMode) {
    const btn = document.getElementById('validate-btn');
    btn.classList.add('loading');

    try {
        state.originalUserInput = userInput;
        state.hitlMode = hitlMode;

        const response = await fetch(`${API_BASE_URL}/api/validations/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_input: userInput,
                hitl_mode: hitlMode
            })
        });

        if (!response.ok) {
            throw new Error(`Validation failed: ${response.statusText}`);
        }

        const data = await response.json();
        state.currentValidation = data;

        // Display results
        displayValidationResults(data);

        // Check if HITL is required
        if (data.hitl_required && data.missing_attributes.length > 0) {
            // Show initial validation results first
            showToast('Initial validation complete. Missing attributes detected.', 'warning');

            // Then open HITL chat
            setTimeout(() => {
                state.missingAttributes = data.missing_attributes;
                state.hitlResponses = {};
                state.currentAttributeIndex = 0;
                openHITLChat();
            }, 1000);
        } else {
            showToast('Validation complete!', 'success');
        }

    } catch (error) {
        console.error('Validation error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
    }
}

async function runValidationWithResponses() {
    const btn = document.getElementById('submit-all-hitl-btn');
    btn.classList.add('loading');

    try {
        console.log('='.repeat(80));
        console.log('📤 SENDING HITL RESPONSES TO BACKEND');
        console.log('='.repeat(80));
        console.log('Original User Input:', state.originalUserInput);
        console.log('HITL Responses:', state.hitlResponses);
        console.log('Number of responses:', Object.keys(state.hitlResponses).length);
        console.log('='.repeat(80));

        const response = await fetch(`${API_BASE_URL}/api/validations/validate-with-responses`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_input: state.originalUserInput,
                responses: state.hitlResponses
            })
        });

        if (!response.ok) {
            throw new Error(`Re-validation failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('📥 RECEIVED RESPONSE:', data);
        state.currentValidation = data;

        // Close HITL chat
        closeHITLChat();

        // Display updated results
        displayValidationResults(data);

        showToast('Re-validation complete with improved confidence!', 'success');

    } catch (error) {
        console.error('Re-validation error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
    }
}

// ===================================================================
// DISPLAY VALIDATION RESULTS
// ===================================================================
function displayValidationResults(data) {
    // Show results section, hide placeholder
    document.getElementById('results-section').style.display = 'block';
    document.getElementById('placeholder-section').style.display = 'none';

    // Update header
    document.getElementById('result-design-id').textContent = data.design_id || 'N/A';

    // Update confidence meter
    const confidence = data.confidence || 0;
    const confidencePercent = Math.round(confidence * 100);
    document.getElementById('confidence-bar').style.width = `${confidencePercent}%`;
    document.getElementById('confidence-value').textContent = `${confidencePercent}%`;

    // Update results table
    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '';

    if (data.validation && data.validation.length > 0) {
        data.validation.forEach(item => {
            const row = document.createElement('tr');

            // Get provided value from attributes
            const providedValue = data.attributes[item.field] !== null && data.attributes[item.field] !== undefined
                ? data.attributes[item.field]
                : '-';

            row.innerHTML = `
                <td><strong>${formatFieldName(item.field)}</strong></td>
                <td>${providedValue}</td>
                <td>${item.expected || '-'}</td>
                <td>${renderStatusChip(item.status)}</td>
                <td>${item.comment || '-'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // Store data for drawer
    window.currentValidationData = data;
}

function formatFieldName(field) {
    return field
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function renderStatusChip(status) {
    const statusLower = status.toLowerCase();
    const icon = statusLower === 'pass' ? '✓' : statusLower === 'warn' ? '⚠' : '✗';
    return `<span class="status-chip ${statusLower}">${icon} ${status}</span>`;
}

// ===================================================================
// REASONING DRAWER
// ===================================================================
function openReasoningDrawer() {
    const drawer = document.getElementById('reasoning-drawer');
    drawer.classList.add('active');

    const data = window.currentValidationData;
    if (!data) return;

    // Update confidence circle
    const confidence = data.confidence || 0;
    const confidencePercent = Math.round(confidence * 100);
    const circumference = 2 * Math.PI * 45;
    const offset = circumference - (confidence * circumference);

    document.getElementById('confidence-circle').style.strokeDashoffset = offset;
    document.getElementById('confidence-percent').textContent = `${confidencePercent}%`;

    // Update reasoning text
    document.getElementById('reasoning-text').textContent = data.reasoning || 'No reasoning provided';

    // Update HITL log if available
    if (data.hitl_interactions && data.hitl_interactions.length > 0) {
        document.getElementById('hitl-log-section').style.display = 'block';
        const hitlLog = document.getElementById('hitl-log');
        hitlLog.innerHTML = '';

        data.hitl_interactions.forEach(interaction => {
            const item = document.createElement('div');
            item.className = 'hitl-log-item';
            item.innerHTML = `
                <div class="hitl-log-field">${formatFieldName(interaction.field)}</div>
                <div class="hitl-log-response">${interaction.user_response}</div>
            `;
            hitlLog.appendChild(item);
        });
    } else {
        document.getElementById('hitl-log-section').style.display = 'none';
    }
}

function closeReasoningDrawer() {
    document.getElementById('reasoning-drawer').classList.remove('active');
}

function setupSVGGradient() {
    // Add SVG gradient definition for confidence circle
    const svg = document.querySelector('.confidence-circle svg');
    if (svg) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', 'confidence-gradient');
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('y1', '0%');
        gradient.setAttribute('x2', '100%');
        gradient.setAttribute('y2', '100%');

        const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('style', 'stop-color:#818cf8;stop-opacity:1');

        const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('style', 'stop-color:#8b5cf6;stop-opacity:1');

        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        defs.appendChild(gradient);
        svg.insertBefore(defs, svg.firstChild);
    }
}

// ===================================================================
// HITL CHAT INTERACTION
// ===================================================================
function openHITLChat() {
    const modal = document.getElementById('hitl-chat-modal');
    modal.style.display = 'flex';

    // Clear previous messages
    const messagesContainer = document.getElementById('hitl-chat-messages');
    messagesContainer.innerHTML = '';

    // Show input container, hide complete button
    document.getElementById('hitl-chat-input-container').style.display = 'block';
    document.getElementById('hitl-chat-complete').style.display = 'none';

    // Add initial AI message
    addChatMessage('ai', `I noticed some missing attributes in your cable design. Let me help you complete the validation by collecting this information.`);

    // Ask for first missing attribute
    askForNextAttribute();
}

function closeHITLChat() {
    document.getElementById('hitl-chat-modal').style.display = 'none';
}

function askForNextAttribute() {
    if (state.currentAttributeIndex >= state.missingAttributes.length) {
        // All attributes collected
        showCompletionMessage();
        return;
    }

    const attribute = state.missingAttributes[state.currentAttributeIndex];
    const question = getAttributeQuestion(attribute);

    addChatMessage('ai', question);

    // Focus input
    document.getElementById('hitl-chat-input').focus();
}

function getAttributeQuestion(attribute) {
    const questions = {
        standard: 'What IEC standard should be used for validation? (e.g., IEC 60502-1)',
        voltage: 'What is the voltage rating? (e.g., 0.6/1 kV)',
        conductor_material: 'What is the conductor material? (Cu for Copper or Al for Aluminum)',
        conductor_class: 'What is the conductor class? (Class 1 for solid or Class 2 for stranded)',
        csa: 'What is the cross-sectional area in mm²? (e.g., 10)',
        insulation_material: 'What is the insulation material? (PVC, XLPE, or EPR)',
        insulation_thickness: 'What is the insulation thickness in mm? (e.g., 1.0)'
    };

    return questions[attribute] || `Please provide the value for ${formatFieldName(attribute)}:`;
}

function handleHITLChatSubmit(e) {
    e.preventDefault();

    const input = document.getElementById('hitl-chat-input');
    const userResponse = input.value.trim();

    if (!userResponse) return;

    // Add user message
    addChatMessage('user', userResponse);

    // Store response
    const currentAttribute = state.missingAttributes[state.currentAttributeIndex];
    state.hitlResponses[currentAttribute] = userResponse;

    // Clear input
    input.value = '';

    // Add confirmation message
    addChatMessage('ai', `✓ Got it! ${formatFieldName(currentAttribute)}: ${userResponse}`);

    // Move to next attribute
    state.currentAttributeIndex++;

    // Ask for next attribute after a short delay
    setTimeout(() => {
        askForNextAttribute();
    }, 500);
}

function showCompletionMessage() {
    addChatMessage('ai', `Perfect! I've collected all the missing information. Click the button below to re-run the validation with the complete data.`);

    // Hide input, show complete button
    document.getElementById('hitl-chat-input-container').style.display = 'none';
    document.getElementById('hitl-chat-complete').style.display = 'block';
}

function addChatMessage(type, text) {
    const messagesContainer = document.getElementById('hitl-chat-messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;

    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar';
    avatar.textContent = type === 'ai' ? '🤖' : '👤';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.innerHTML = `<p>${text}</p>`;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);

    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function handleSubmitAllHITL() {
    runValidationWithResponses();
}

// ===================================================================
// TOAST NOTIFICATIONS
// ===================================================================
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}
