// ===================================
// CONFIGURATION
// ===================================
const API_BASE_URL = 'http://localhost:8000';
// ===================================
// STATE MANAGEMENT
// ===================================
let currentValidation = null;
let validationHistory = [];
// ===================================
// DOM ELEMENTS
// ===================================
const elements = {
    form: document.getElementById('validation-form'),
    userInput: document.getElementById('user-input'),
    hitlMode: document.getElementById('hitl-mode'),
    validateBtn: document.getElementById('validate-btn'),
    resultsSection: document.getElementById('results-section'),
    resultDesignId: document.getElementById('result-design-id'),
    confidenceBar: document.getElementById('confidence-bar'),
    confidenceValue: document.getElementById('confidence-value'),
    resultsTbody: document.getElementById('results-tbody'),
    reasoningText: document.getElementById('reasoning-text'),
    hitlFormSection: document.getElementById('hitl-form-section'),
    hitlResponseForm: document.getElementById('hitl-response-form'),
    hitlFieldsContainer: document.getElementById('hitl-fields-container'),
    submitHitlBtn: document.getElementById('submit-hitl-btn'),
    cancelHitlBtn: document.getElementById('cancel-hitl-btn'),
    hitlSection: document.getElementById('hitl-section'),
    hitlInteractions: document.getElementById('hitl-interactions'),
    historyContainer: document.getElementById('history-container'),
    refreshHistoryBtn: document.getElementById('refresh-history-btn'),
    toastContainer: document.getElementById('toast-container')
};
// ===================================
// UTILITY FUNCTIONS
// ===================================
/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
/**
 * Format timestamp to readable format
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
/**
 * Update workflow visualization
 */
function updateWorkflow(step, status = 'active') {
    const steps = document.querySelectorAll('.workflow-step');
    const stepMap = {
        'supervisor': 0,
        'fetch': 1,
        'validate': 2,
        'complete': 3
    };

    const currentIndex = stepMap[step];

    steps.forEach((stepEl, index) => {
        const statusEl = stepEl.querySelector('.step-status');

        if (index < currentIndex) {
            stepEl.classList.remove('active');
            stepEl.classList.add('completed');
            statusEl.textContent = 'Completed';
        } else if (index === currentIndex) {
            stepEl.classList.add('active');
            stepEl.classList.remove('completed');
            statusEl.textContent = status === 'active' ? 'Processing...' : 'Completed';
        } else {
            stepEl.classList.remove('active', 'completed');
            statusEl.textContent = 'Waiting';
        }
    });
}
/**
 * Reset workflow visualization
 */
function resetWorkflow() {
    const steps = document.querySelectorAll('.workflow-step');
    steps.forEach(step => {
        step.classList.remove('active', 'completed');
        step.querySelector('.step-status').textContent = 'Waiting';
    });
}
// ===================================
// API FUNCTIONS
// ===================================
/**
 * Validate design
 */
async function validateDesign(userInput, hitlMode) {
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
        const error = await response.json();
        throw new Error(error.detail || 'Validation failed');
    }

    return await response.json();
}
/**
 * Fetch validation history
 */
async function fetchValidationHistory() {
    const response = await fetch(`${API_BASE_URL}/api/validations/`);

    if (!response.ok) {
        throw new Error('Failed to fetch validation history');
    }

    return await response.json();
}
/**
 * Submit HITL responses
 */
async function submitHitlResponses(validationId, responses) {
    const response = await fetch(`${API_BASE_URL}/api/validations/submit-hitl`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            validation_id: validationId,
            responses: responses
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'HITL submission failed');
    }

    return await response.json();
}
/**
 * Fetch specific validation
 */
async function fetchValidation(validationId) {
    const response = await fetch(`${API_BASE_URL}/api/validations/${validationId}`);

    if (!response.ok) {
        throw new Error('Failed to fetch validation');
    }

    return await response.json();
}
// ===================================
// UI RENDERING FUNCTIONS
// ===================================
/**
 * Display validation results
 */
function displayResults(validation) {
    currentValidation = validation;

    // Show results section
    elements.resultsSection.style.display = 'block';

    // Update design ID
    elements.resultDesignId.textContent = validation.design_id || 'N/A';

    // Update confidence meter
    const confidence = Math.round((validation.confidence || 0) * 100);
    elements.confidenceBar.style.width = `${confidence}%`;
    elements.confidenceValue.textContent = `${confidence}%`;

    // Update confidence bar color based on value
    if (confidence >= 80) {
        elements.confidenceBar.style.background = 'var(--gradient-success)';
    } else if (confidence >= 60) {
        elements.confidenceBar.style.background = 'var(--gradient-warning)';
    } else {
        elements.confidenceBar.style.background = 'var(--gradient-danger)';
    }

    // Render validation results table
    elements.resultsTbody.innerHTML = '';
    validation.validation.forEach(result => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${result.field}</strong></td>
            <td>
                <span class="status-badge ${result.status.toLowerCase()}">
                    ${result.status}
                </span>
            </td>
            <td>${result.expected || '-'}</td>
            <td>${result.comment || '-'}</td>
        `;
        elements.resultsTbody.appendChild(row);
    });

    // Update reasoning
    elements.reasoningText.textContent = validation.reasoning || 'No reasoning provided';

    // Update HITL interactions
    if (validation.hitl_interactions && validation.hitl_interactions.length > 0) {
        elements.hitlSection.style.display = 'block';
        elements.hitlInteractions.innerHTML = '';

        validation.hitl_interactions.forEach(interaction => {
            const item = document.createElement('div');
            item.className = 'hitl-item';
            item.innerHTML = `
                <div class="hitl-field">${interaction.field}</div>
                <div class="hitl-response">${interaction.user_response || 'No response'}</div>
            `;
            elements.hitlInteractions.appendChild(item);
        });
    } else {
        elements.hitlSection.style.display = 'none';
    }

    // Check if HITL is required - use CHAT interface instead of form
    // FIX: Check hitl_mode and missing_attributes instead of hitl_required (backend bug)
    if (validation.hitl_mode && validation.missing_attributes && validation.missing_attributes.length > 0) {
        // Use new chat interface
        if (typeof initHitlChat === 'function') {
            initHitlChat(validation);
        } else {
            // Fallback to old form if chat not loaded
            displayHitlForm(validation);
        }
    } else {
        elements.hitlFormSection.style.display = 'none';
        const chatSection = document.getElementById('hitl-chat-section');
        if (chatSection) {
            chatSection.style.display = 'none';
        }
    }

    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
/**
 * Render validation history
 */
function renderHistory(validations) {
    validationHistory = validations;

    if (validations.length === 0) {
        elements.historyContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>No validation history yet</p>
            </div>
        `;
        return;
    }

    // Group by design ID
    const grouped = {};
    validations.forEach(validation => {
        const designId = validation.design_id || 'Unknown';
        if (!grouped[designId]) {
            grouped[designId] = [];
        }
        grouped[designId].push(validation);
    });

    // Render grouped history
    elements.historyContainer.innerHTML = '';

    Object.keys(grouped).forEach(designId => {
        const group = grouped[designId];

        const groupEl = document.createElement('div');
        groupEl.className = 'history-group';

        // Group header
        const header = document.createElement('div');
        header.className = 'history-group-header';
        header.innerHTML = `
            <span>📦 ${designId}</span>
            <span style="margin-left: auto; font-size: var(--font-size-xs); color: var(--color-text-muted);">
                ${group.length} validation${group.length > 1 ? 's' : ''}
            </span>
        `;
        groupEl.appendChild(header);

        // Group items
        const itemsContainer = document.createElement('div');
        itemsContainer.className = 'history-items';

        group.forEach(validation => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.onclick = () => displayResults(validation);

            // Calculate status summary
            const statusCounts = { PASS: 0, WARN: 0, FAIL: 0 };
            validation.validation.forEach(result => {
                statusCounts[result.status] = (statusCounts[result.status] || 0) + 1;
            });

            item.innerHTML = `
                <div class="history-item-header">
                    <span class="history-timestamp">${formatTimestamp(validation.created_at)}</span>
                </div>
                <div class="history-summary">
                    ${statusCounts.PASS > 0 ? `<span class="summary-badge" style="background: rgba(16, 185, 129, 0.2); color: var(--color-pass);">✓ ${statusCounts.PASS}</span>` : ''}
                    ${statusCounts.WARN > 0 ? `<span class="summary-badge" style="background: rgba(245, 158, 11, 0.2); color: var(--color-warn);">⚠ ${statusCounts.WARN}</span>` : ''}
                    ${statusCounts.FAIL > 0 ? `<span class="summary-badge" style="background: rgba(239, 68, 68, 0.2); color: var(--color-fail);">✗ ${statusCounts.FAIL}</span>` : ''}
                </div>
            `;

            itemsContainer.appendChild(item);
        });

        groupEl.appendChild(itemsContainer);
        elements.historyContainer.appendChild(groupEl);
    });
}
/**
 * Display HITL form for missing attributes
 */
function displayHitlForm(validation) {
    elements.hitlFormSection.style.display = 'block';
    elements.hitlFieldsContainer.innerHTML = '';

    const attributeLabels = {
        'standard': 'IEC Standard (e.g., IEC 60502-1)',
        'voltage': 'Voltage Rating (e.g., 0.6/1 kV)',
        'conductor_material': 'Conductor Material (Cu or Al)',
        'conductor_class': 'Conductor Class (Class 1 or Class 2)',
        'csa': 'Cross-Sectional Area (mm²)',
        'insulation_material': 'Insulation Material (PVC, XLPE, or EPR)',
        'insulation_thickness': 'Insulation Thickness (mm)'
    };

    validation.missing_attributes.forEach(attr => {
        const fieldGroup = document.createElement('div');
        fieldGroup.className = 'hitl-field-group';

        const label = document.createElement('label');
        label.className = 'hitl-field-label';
        label.textContent = attributeLabels[attr] || attr;
        label.setAttribute('for', `hitl-${attr}`);

        const input = document.createElement('input');
        input.type = 'text';
        input.id = `hitl-${attr}`;
        input.name = attr;
        input.className = 'hitl-field-input';
        input.required = true;
        input.placeholder = `Enter ${attributeLabels[attr] || attr}`;

        fieldGroup.appendChild(label);
        fieldGroup.appendChild(input);
        elements.hitlFieldsContainer.appendChild(fieldGroup);
    });

    // Store validation ID for submission
    elements.hitlResponseForm.dataset.validationId = validation.validation_id;
}
// ===================================
// EVENT HANDLERS
// ===================================
/**
 * Handle form submission
 */
async function handleSubmit(e) {
    e.preventDefault();

    const userInput = elements.userInput.value.trim();
    const hitlMode = elements.hitlMode.checked;

    if (!userInput) {
        showToast('Please enter a design query', 'error');
        return;
    }

    // Update UI state
    elements.validateBtn.classList.add('loading');
    elements.validateBtn.disabled = true;
    resetWorkflow();

    try {
        // Simulate workflow progression
        updateWorkflow('supervisor', 'active');
        await new Promise(resolve => setTimeout(resolve, 500));

        updateWorkflow('fetch', 'active');
        await new Promise(resolve => setTimeout(resolve, 500));

        updateWorkflow('validate', 'active');

        // Make API call
        const result = await validateDesign(userInput, hitlMode);

        // Complete workflow
        updateWorkflow('complete', 'active');
        await new Promise(resolve => setTimeout(resolve, 300));

        // Display results
        displayResults(result);

        // Refresh history
        await loadHistory();

        showToast('Validation completed successfully', 'success');

    } catch (error) {
        console.error('Validation error:', error);
        showToast(error.message || 'Validation failed', 'error');
        resetWorkflow();
    } finally {
        elements.validateBtn.classList.remove('loading');
        elements.validateBtn.disabled = false;
    }
}
/**
 * Load validation history
 */
async function loadHistory() {
    try {
        const validations = await fetchValidationHistory();
        renderHistory(validations);
    } catch (error) {
        console.error('Failed to load history:', error);
        showToast('Failed to load history', 'error');
    }
}
/**
 * Handle hint click
 */
function handleHintClick(e) {
    if (e.target.classList.contains('hint')) {
        const hintText = e.target.textContent.replace('💡 Try: ', '');
        elements.userInput.value = hintText;
        elements.userInput.focus();
    }
}
/**
 * Handle HITL form submission
 */
async function handleHitlSubmit(e) {
    e.preventDefault();

    const validationId = elements.hitlResponseForm.dataset.validationId;
    if (!validationId) {
        showToast('No validation ID found', 'error');
        return;
    }

    // Collect responses
    const formData = new FormData(elements.hitlResponseForm);
    const responses = {};
    for (const [key, value] of formData.entries()) {
        if (value.trim()) {
            responses[key] = value.trim();
        }
    }

    if (Object.keys(responses).length === 0) {
        showToast('Please provide at least one response', 'error');
        return;
    }

    // Update UI state
    elements.submitHitlBtn.classList.add('loading');
    elements.submitHitlBtn.disabled = true;

    try {
        updateWorkflow('validate', 'active');

        // Submit HITL responses
        const result = await submitHitlResponses(validationId, responses);

        // Complete workflow
        updateWorkflow('complete', 'active');
        await new Promise(resolve => setTimeout(resolve, 300));

        // Display updated results
        displayResults(result);

        // Refresh history
        await loadHistory();

        showToast('HITL responses submitted successfully', 'success');

    } catch (error) {
        console.error('HITL submission error:', error);
        showToast(error.message || 'HITL submission failed', 'error');
    } finally {
        elements.submitHitlBtn.classList.remove('loading');
        elements.submitHitlBtn.disabled = false;
    }
}
/**
 * Handle HITL cancellation
 */
function handleHitlCancel() {
    elements.hitlFormSection.style.display = 'none';
    showToast('HITL input cancelled', 'info');
}
// ===================================
// INITIALIZATION
// ===================================
/**
 * Initialize application
 */
function init() {
    // Attach event listeners
    elements.form.addEventListener('submit', handleSubmit);
    elements.refreshHistoryBtn.addEventListener('click', loadHistory);
    elements.hitlResponseForm.addEventListener('submit', handleHitlSubmit);
    elements.cancelHitlBtn.addEventListener('click', handleHitlCancel);
    document.querySelector('.input-hints').addEventListener('click', handleHintClick);

    // Load initial history
    loadHistory();

    // Show welcome toast
    setTimeout(() => {
        showToast('Welcome to Cable Design Validator! 🚀', 'info');
    }, 500);
}
// Start application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}