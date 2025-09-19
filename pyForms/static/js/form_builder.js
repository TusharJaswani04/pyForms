// static/js/form_builder.js

let currentQuestionId = null;

// Get CSRF token
function getCSRFToken() {
    const csrfInput = document.querySelector('#csrfForm input[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

// Add new question (Google Forms style)
function addQuestion() {
    const questionsList = document.getElementById('questionsList');
    const questionId = Date.now(); // Temporary ID for new questions
    
    const questionHTML = `
        <div class="question-card mb-3" data-question-id="new-${questionId}">
            <div class="card">
                <div class="card-body">
                    <!-- Question Editor -->
                    <div class="question-editor">
                        <div class="row">
                            <div class="col-md-8">
                                <div class="mb-3">
                                    <input type="text" class="form-control form-control-lg question-title-input" 
                                           placeholder="Question" value="Untitled Question">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <select class="form-select question-type-select">
                                    <option value="short_text">Short answer</option>
                                    <option value="long_text">Paragraph</option>
                                    <option value="multiple_choice" selected>Multiple choice</option>
                                    <option value="checkboxes">Checkboxes</option>
                                    <option value="dropdown">Dropdown</option>
                                    <option value="linear_scale">Linear scale</option>
                                    <option value="date">Date</option>
                                    <option value="time">Time</option>
                                    <option value="file_upload">File upload</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- Options Section (for multiple choice, checkboxes, dropdown) -->
                        <div class="question-options">
                            <div class="option-item mb-2">
                                <div class="input-group">
                                    <span class="input-group-text"><i class="bi bi-circle"></i></span>
                                    <input type="text" class="form-control" placeholder="Option 1">
                                    <button class="btn btn-outline-secondary" type="button" onclick="removeOption(this)">
                                        <i class="bi bi-x"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="option-item mb-2">
                                <div class="input-group">
                                    <span class="input-group-text"><i class="bi bi-circle"></i></span>
                                    <input type="text" class="form-control" placeholder="Option 2">
                                    <button class="btn btn-outline-secondary" type="button" onclick="removeOption(this)">
                                        <i class="bi bi-x"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="add-option">
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="addNewOption(this)">
                                    <i class="bi bi-plus me-1"></i>Add option
                                </button>
                            </div>
                        </div>
                        
                        <!-- Linear Scale Section -->
                        <div class="linear-scale-section" style="display: none;">
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="form-label">From</label>
                                    <select class="form-select scale-min">
                                        <option value="0">0</option>
                                        <option value="1" selected>1</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">To</label>
                                    <select class="form-select scale-max">
                                        <option value="5" selected>5</option>
                                        <option value="10">10</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <input type="text" class="form-control scale-min-label" placeholder="Label (optional)">
                                </div>
                                <div class="col-md-6">
                                    <input type="text" class="form-control scale-max-label" placeholder="Label (optional)">
                                </div>
                            </div>
                        </div>
                        
                        <!-- Help Text -->
                        <div class="mt-3">
                            <input type="text" class="form-control help-text-input" placeholder="Description (optional)">
                        </div>
                        
                        <!-- Question Actions -->
                        <div class="question-actions mt-3 pt-3 border-top">
                            <div class="row align-items-center">
                                <div class="col">
                                    <div class="form-check">
                                        <input class="form-check-input required-checkbox" type="checkbox" id="required-${questionId}" checked>
                                        <label class="form-check-label" for="required-${questionId}">Required</label>
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <div class="btn-group">
                                        <button type="button" class="btn btn-outline-secondary btn-sm" onclick="duplicateQuestion(this)" title="Duplicate">
                                            <i class="bi bi-files"></i>
                                        </button>
                                        <button type="button" class="btn btn-outline-danger btn-sm" onclick="deleteQuestion(this)" title="Delete">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Insert before the "Add Question" button
    const addQuestionSection = document.querySelector('.add-question-section');
    if (addQuestionSection) {
        addQuestionSection.insertAdjacentHTML('beforebegin', questionHTML);
        
        // Bind events for the new question
        const newQuestion = document.querySelector(`[data-question-id="new-${questionId}"]`);
        bindQuestionEvents(newQuestion);
        
        // Focus on the question title
        newQuestion.querySelector('.question-title-input').focus();
        
        // Auto-save after a delay
        setTimeout(() => saveQuestion(newQuestion), 1000);
    }
}

// Bind events to a question card
function bindQuestionEvents(questionCard) {
    const typeSelect = questionCard.querySelector('.question-type-select');
    const titleInput = questionCard.querySelector('.question-title-input');
    const helpTextInput = questionCard.querySelector('.help-text-input');
    const requiredCheckbox = questionCard.querySelector('.required-checkbox');
    
    // Question type change
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            handleQuestionTypeChange(questionCard);
            autoSaveQuestion(questionCard);
        });
    }
    
    // Auto-save on input changes
    [titleInput, helpTextInput].forEach(input => {
        if (input) {
            input.addEventListener('input', () => {
                clearTimeout(input.saveTimeout);
                input.saveTimeout = setTimeout(() => autoSaveQuestion(questionCard), 1500);
            });
        }
    });
    
    if (requiredCheckbox) {
        requiredCheckbox.addEventListener('change', () => autoSaveQuestion(questionCard));
    }
    
    // Option input changes
    questionCard.querySelectorAll('.option-item input').forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(input.saveTimeout);
            input.saveTimeout = setTimeout(() => autoSaveQuestion(questionCard), 1500);
        });
    });
}

// Handle question type change
function handleQuestionTypeChange(questionCard) {
    const type = questionCard.querySelector('.question-type-select').value;
    const optionsSection = questionCard.querySelector('.question-options');
    const scaleSection = questionCard.querySelector('.linear-scale-section');
    
    // Hide all sections first
    if (optionsSection) optionsSection.style.display = 'none';
    if (scaleSection) scaleSection.style.display = 'none';
    
    // Show relevant sections
    if (['multiple_choice', 'checkboxes', 'dropdown'].includes(type)) {
        if (optionsSection) optionsSection.style.display = 'block';
        // Update icons based on type
        const icon = type === 'multiple_choice' ? 'bi-circle' : 
                    type === 'checkboxes' ? 'bi-square' : 'bi-chevron-down';
        questionCard.querySelectorAll('.option-item .input-group-text i').forEach(i => {
            i.className = `bi ${icon}`;
        });
    } else if (type === 'linear_scale') {
        if (scaleSection) scaleSection.style.display = 'block';
    }
}

// Add new option
function addNewOption(button) {
    const questionCard = button.closest('.question-card');
    const optionsContainer = questionCard.querySelector('.question-options');
    const optionCount = optionsContainer.querySelectorAll('.option-item').length + 1;
    const type = questionCard.querySelector('.question-type-select').value;
    const icon = type === 'multiple_choice' ? 'bi-circle' : 
                type === 'checkboxes' ? 'bi-square' : 'bi-chevron-down';
    
    const optionHTML = `
        <div class="option-item mb-2">
            <div class="input-group">
                <span class="input-group-text"><i class="bi ${icon}"></i></span>
                <input type="text" class="form-control" placeholder="Option ${optionCount}">
                <button class="btn btn-outline-secondary" type="button" onclick="removeOption(this)">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        </div>
    `;
    
    button.parentElement.insertAdjacentHTML('beforebegin', optionHTML);
    
    // Bind events to new option
    const newOption = optionsContainer.querySelector('.option-item:last-of-type');
    const input = newOption.querySelector('input');
    input.addEventListener('input', () => {
        clearTimeout(input.saveTimeout);
        input.saveTimeout = setTimeout(() => autoSaveQuestion(questionCard), 1500);
    });
    
    input.focus();
}

// Remove option
function removeOption(button) {
    const optionItem = button.closest('.option-item');
    const questionCard = button.closest('.question-card');
    optionItem.remove();
    
    // Auto-save after removal
    setTimeout(() => autoSaveQuestion(questionCard), 500);
}

// Duplicate question
function duplicateQuestion(button) {
    const questionCard = button.closest('.question-card');
    const clonedCard = questionCard.cloneNode(true);
    
    // Update ID
    const newId = Date.now();
    clonedCard.setAttribute('data-question-id', `new-${newId}`);
    clonedCard.querySelector('.required-checkbox').id = `required-${newId}`;
    clonedCard.querySelector('.form-check-label').setAttribute('for', `required-${newId}`);
    
    // Insert after current question
    questionCard.insertAdjacentElement('afterend', clonedCard);
    
    // Bind events
    bindQuestionEvents(clonedCard);
    
    // Auto-save
    setTimeout(() => autoSaveQuestion(clonedCard), 1000);
}

// Delete question
function deleteQuestion(button) {
    const questionCard = button.closest('.question-card');
    const questionId = questionCard.getAttribute('data-question-id');
    
    if (confirm('Delete this question?')) {
        if (questionId.startsWith('new-')) {
            // Just remove if it's a new question
            questionCard.remove();
        } else {
            // Send delete request to server for existing questions
            fetch(`/delete-question/${questionId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            }).then(response => {
                if (response.ok) {
                    questionCard.remove();
                    showSaveIndicator('Question deleted', 'success');
                }
            }).catch(error => {
                console.error('Error deleting question:', error);
                showSaveIndicator('Error deleting', 'error');
            });
        }
    }
}

// Auto-save question
function autoSaveQuestion(questionCard) {
    const questionData = extractQuestionData(questionCard);
    const questionId = questionCard.getAttribute('data-question-id');
    
    if (questionId.startsWith('new-')) {
        // Save new question
        saveQuestion(questionCard);
    } else {
        // Update existing question
        updateQuestion(questionId, questionData);
    }
}

// Extract question data from form
function extractQuestionData(questionCard) {
    const type = questionCard.querySelector('.question-type-select').value;
    const title = questionCard.querySelector('.question-title-input').value;
    const helpText = questionCard.querySelector('.help-text-input').value;
    const isRequired = questionCard.querySelector('.required-checkbox').checked;
    
    const data = {
        text: title,
        question_type: type,
        help_text: helpText,
        is_required: isRequired
    };
    
    // Add options for relevant types
    if (['multiple_choice', 'checkboxes', 'dropdown'].includes(type)) {
        const options = [];
        questionCard.querySelectorAll('.option-item input').forEach(input => {
            if (input.value.trim()) {
                options.push(input.value.trim());
            }
        });
        data.options = options;
    }
    
    // Add scale data
    if (type === 'linear_scale') {
        data.scale_min = parseInt(questionCard.querySelector('.scale-min').value);
        data.scale_max = parseInt(questionCard.querySelector('.scale-max').value);
        data.scale_min_label = questionCard.querySelector('.scale-min-label').value;
        data.scale_max_label = questionCard.querySelector('.scale-max-label').value;
    }
    
    return data;
}

// Save new question
async function saveQuestion(questionCard) {
    const formUuid = window.formUuid;
    const questionData = extractQuestionData(questionCard);
    
    if (!questionData.text.trim()) return;
    
    try {
        const response = await fetch(`/add-question/${formUuid}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(questionData)
        });
        
        const data = await response.json();
        if (data.success) {
            // Update question ID
            questionCard.setAttribute('data-question-id', data.question_id);
            showSaveIndicator('Saved', 'success');
        } else {
            showSaveIndicator('Error saving', 'error');
        }
    } catch (error) {
        console.error('Error saving question:', error);
        showSaveIndicator('Error saving', 'error');
    }
}

// Update existing question
async function updateQuestion(questionId, questionData) {
    try {
        const response = await fetch(`/update-question/${questionId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(questionData)
        });
        
        if (response.ok) {
            showSaveIndicator('Saved', 'success');
        } else {
            showSaveIndicator('Error saving', 'error');
        }
    } catch (error) {
        console.error('Error updating question:', error);
        showSaveIndicator('Error saving', 'error');
    }
}

// Show save indicator
function showSaveIndicator(message, type) {
    let indicator = document.getElementById('save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'save-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            z-index: 1050;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(indicator);
    }
    
    indicator.textContent = message;
    indicator.className = type === 'success' ? 'bg-success text-white' : 'bg-danger text-white';
    indicator.style.display = 'block';
    
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

// Update form setting
async function updateFormSetting(setting, value) {
    const formUuid = window.formUuid;
    
    try {
        const formData = new FormData();
        formData.append(setting, value);
        
        const response = await fetch(`/update-settings/${formUuid}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            body: formData
        });
        
        const data = await response.json();
        if (data.success) {
            showSaveIndicator('Saved', 'success');
        } else {
            showSaveIndicator('Error saving', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showSaveIndicator('Error saving', 'error');
    }
}

// Initialize existing questions
function initializeExistingQuestions() {
    document.querySelectorAll('.question-card').forEach(questionCard => {
        bindQuestionEvents(questionCard);
        handleQuestionTypeChange(questionCard);
    });
}

// Auto-save form title and description
function bindFormHeaderEvents() {
    const titleInput = document.querySelector('.form-title-input');
    const descInput = document.querySelector('.form-description-input');
    
    [titleInput, descInput].forEach(input => {
        if (input) {
            input.addEventListener('input', () => {
                clearTimeout(input.saveTimeout);
                input.saveTimeout = setTimeout(() => {
                    const formData = new FormData();
                    if (titleInput) formData.append('title', titleInput.value);
                    if (descInput) formData.append('description', descInput.value);
                    
                    fetch(`/update-settings/${window.formUuid}/`, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': getCSRFToken() },
                        body: formData
                    }).then(response => {
                        if (response.ok) showSaveIndicator('Saved', 'success');
                    }).catch(() => {
                        showSaveIndicator('Error saving', 'error');
                    });
                }, 1500);
            });
        }
    });
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Form builder initialized');
    
    initializeExistingQuestions();
    bindFormHeaderEvents();
    
    // Bind add question button
    const addQuestionBtn = document.getElementById('add-question-btn');
    if (addQuestionBtn) {
        addQuestionBtn.addEventListener('click', addQuestion);
    }
    
    // Floating add button
    const floatingBtn = document.querySelector('.floating-add-btn');
    if (floatingBtn) {
        floatingBtn.addEventListener('click', addQuestion);
    }
});
