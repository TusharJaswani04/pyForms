class ThemeManager {
    constructor() {
        this.init();
    }

    init() {
        this.applyStoredTheme();
        this.setupThemeToggle();
    }

    applyStoredTheme() {
        const theme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', theme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.showToast(`${newTheme === 'dark' ? 'Dark' : 'Light'} mode activated`);
    }

    setupThemeToggle() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-toggle="theme"]')) {
                this.toggleTheme();
            }
        });
    }

    showToast(message) {
        // Create and show toast notification
        const toastContainer = document.querySelector('.toast-container');
        if (toastContainer) {
            const toastEl = document.getElementById('liveToast');
            const toastBody = document.getElementById('toastMessage');
            
            if (toastEl && toastBody) {
                toastBody.textContent = message;
                const toast = new bootstrap.Toast(toastEl);
                toast.show();
            }
        }
    }
}

// Form Utilities
class FormUtils {
    static validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }

    static showLoading(element, show = true) {
        if (show) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }

    static animateValue(element, start, end, duration) {
        const startTimestamp = performance.now();
        
        const step = (timestamp) => {
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = value;
            
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };
        
        requestAnimationFrame(step);
    }
}

// Copy to Clipboard
class ClipboardManager {
    static async copyText(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        }
    }
}

// Global Functions
window.copyToClipboard = async function(text) {
    const success = await ClipboardManager.copyText(text);
    if (success) {
        showToast('Link copied to clipboard!');
    } else {
        showToast('Failed to copy link', 'error');
    }
};

window.showToast = function(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');
    
    if (toastElement && toastMessage) {
        toastMessage.textContent = message;
        
        // Update toast style based on type
        const toastHeader = toastElement.querySelector('.toast-header');
        const icon = toastHeader.querySelector('i');
        
        if (type === 'error') {
            icon.className = 'bi bi-exclamation-triangle text-danger me-2';
        } else if (type === 'warning') {
            icon.className = 'bi bi-exclamation-circle text-warning me-2';
        } else {
            icon.className = 'bi bi-check-circle text-success me-2';
        }
        
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }
};

// Auto-save functionality
class AutoSave {
    constructor(formSelector, saveUrl, interval = 30000) {
        this.form = document.querySelector(formSelector);
        this.saveUrl = saveUrl;
        this.interval = interval;
        this.lastSave = {};
        
        if (this.form) {
            this.init();
        }
    }

    init() {
        this.setupEventListeners();
        setInterval(() => this.autoSave(), this.interval);
    }

    setupEventListeners() {
        this.form.addEventListener('input', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.markChanged();
            }
        });
    }

    markChanged() {
        this.hasChanges = true;
    }

    async autoSave() {
        if (!this.hasChanges) return;

        const formData = new FormData(this.form);
        const currentData = Object.fromEntries(formData);
        
        // Check if data actually changed
        if (JSON.stringify(currentData) === JSON.stringify(this.lastSave)) {
            return;
        }

        try {
            const response = await fetch(this.saveUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            if (response.ok) {
                this.lastSave = currentData;
                this.hasChanges = false;
                this.showSaveIndicator(true);
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
            this.showSaveIndicator(false);
        }
    }

    showSaveIndicator(success) {
        const indicator = document.getElementById('saveIndicator');
        if (indicator) {
            indicator.textContent = success ? 'Saved' : 'Save failed';
            indicator.className = `badge ${success ? 'bg-success' : 'bg-danger'}`;
            
            setTimeout(() => {
                indicator.textContent = '';
                indicator.className = 'badge';
            }, 2000);
        }
    }
}

// Page Animations
class PageAnimations {
    static fadeInElements() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });

        elements.forEach(el => observer.observe(el));
    }

    static initCounters() {
        const counters = document.querySelectorAll('[data-count]');
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.count);
            FormUtils.animateValue(counter, 0, target, 2000);
        });
    }
}

// Keyboard Shortcuts
class KeyboardShortcuts {
    constructor() {
        this.shortcuts = {
            'ctrl+s': () => this.saveForm(),
            'ctrl+n': () => this.newForm(),
            'ctrl+p': () => this.previewForm(),
            'esc': () => this.closeModal()
        };
        
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyCombo(e);
            if (this.shortcuts[key]) {
                e.preventDefault();
                this.shortcuts[key]();
            }
        });
    }

    getKeyCombo(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('ctrl');
        if (e.shiftKey) parts.push('shift');
        if (e.altKey) parts.push('alt');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    }

    saveForm() {
        const saveButton = document.querySelector('button[type="submit"]');
        if (saveButton) saveButton.click();
    }

    newForm() {
        const newFormButton = document.querySelector('[href*="create"]');
        if (newFormButton) window.location.href = newFormButton.href;
    }

    previewForm() {
        const previewButton = document.querySelector('[data-action="preview"]');
        if (previewButton) previewButton.click();
    }

    closeModal() {
        const modal = bootstrap.Modal.getInstance(document.querySelector('.modal.show'));
        if (modal) modal.hide();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme manager
    new ThemeManager();
    
    // Initialize keyboard shortcuts
    new KeyboardShortcuts();
    
    // Initialize page animations
    PageAnimations.fadeInElements();
    PageAnimations.initCounters();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                FormUtils.showLoading(submitButton);
            }
        });
    });
});

// Export for use in other files
window.FormUtils = FormUtils;
window.ClipboardManager = ClipboardManager;
window.ThemeManager = ThemeManager;