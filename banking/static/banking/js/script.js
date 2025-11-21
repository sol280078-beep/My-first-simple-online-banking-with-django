// Banking System - Enhanced JavaScript
class BankingSystem {
    constructor() {
        this.init();
    }

    init() {
        this.initializeEventListeners();
        this.setupFormValidation();
        this.autoDismissAlerts();
        this.enhanceUserExperience();
    }

    initializeEventListeners() {
        // Amount formatting
        document.querySelectorAll('input[name="amount"]').forEach(input => {
            input.addEventListener('blur', (e) => this.formatAmount(e.target));
        });

        // Transaction filter
        const transactionFilter = document.getElementById('transaction-filter');
        if (transactionFilter) {
            transactionFilter.addEventListener('change', (e) => this.filterTransactions(e.target.value));
        }

        // Print functionality
        document.querySelectorAll('.print-btn').forEach(btn => {
            btn.addEventListener('click', () => window.print());
        });
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        });

        // Transfer form specific validation
        const transferForm = document.querySelector('form[action*="transfer"]');
        if (transferForm) {
            this.setupTransferValidation(transferForm);
        }
    }

    setupTransferValidation(form) {
        const toAccountInput = form.querySelector('input[name="to_account"]');
        const amountInput = form.querySelector('input[name="amount"]');

        if (toAccountInput) {
            toAccountInput.addEventListener('input', (e) => this.validateAccountNumber(e.target));
        }

        if (amountInput) {
            amountInput.addEventListener('input', (e) => this.validateAmount(e.target));
        }
    }

    validateAccountNumber(input) {
        const value = input.value.trim();
        const isValid = /^[A-Z0-9]{8,20}$/i.test(value);
        
        this.toggleFieldValidation(input, isValid, 'Please enter a valid account number (8-20 characters)');
        return isValid;
    }

    validateAmount(input) {
        const value = parseFloat(input.value);
        const isValid = !isNaN(value) && value > 0 && value <= 1000000;
        
        this.toggleFieldValidation(input, isValid, 'Please enter a valid amount (0.01 - 1,000,000)');
        return isValid;
    }

    toggleFieldValidation(field, isValid, errorMessage) {
        // Remove existing error
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        // Remove existing classes
        field.classList.remove('is-valid', 'is-invalid');

        if (field.value.trim() === '') {
            return;
        }

        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-danger small mt-1';
            errorDiv.textContent = errorMessage;
            field.parentNode.appendChild(errorDiv);
        }
    }

    formatAmount(input) {
        const value = parseFloat(input.value);
        if (!isNaN(value)) {
            input.value = value.toFixed(2);
        }
    }

    handleFormSubmit(e) {
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        if (submitButton) {
            // Show loading state
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = `
                <span class="spinner"></span>
                Processing...
            `;

            // Re-enable button after 5 seconds (safety measure)
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }, 5000);
        }
    }

    filterTransactions(filterValue) {
        const rows = document.querySelectorAll('#transaction-table tbody tr');
        let visibleCount = 0;

        rows.forEach(row => {
            const typeCell = row.querySelector('td:nth-child(2)');
            if (!typeCell) return;

            const type = typeCell.textContent.toLowerCase();
            const shouldShow = filterValue === 'all' || type.includes(filterValue.toLowerCase());
            
            row.style.display = shouldShow ? '' : 'none';
            if (shouldShow) visibleCount++;
        });

        // Show message if no transactions match filter
        this.updateFilterMessage(visibleCount);
    }

    updateFilterMessage(visibleCount) {
        let messageElement = document.getElementById('filter-message');
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.id = 'filter-message';
            messageElement.className = 'alert alert-info mt-3';
            document.querySelector('#transaction-table').parentNode.appendChild(messageElement);
        }

        if (visibleCount === 0) {
            messageElement.textContent = 'No transactions match the selected filter.';
            messageElement.style.display = 'block';
        } else {
            messageElement.style.display = 'none';
        }
    }

    autoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.classList.contains('alert-dismissible')) {
                    const closeButton = alert.querySelector('.btn-close');
                    if (closeButton) {
                        closeButton.click();
                    }
                } else {
                    alert.style.opacity = '0';
                    alert.style.transition = 'opacity 0.5s ease';
                    setTimeout(() => alert.remove(), 500);
                }
            }, 5000);
        });
    }

    enhanceUserExperience() {
        // Add fade-in animation to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });

        // Add hover effects to interactive elements
        this.addHoverEffects();
    }

    addHoverEffects() {
        // Add hover effects to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            btn.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Add hover effects to cards
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    // Utility methods
    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    static formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize the banking system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new BankingSystem();
});

// Add CSS for spinner
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
    .spinner {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 2px solid #ffffff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s ease-in-out infinite;
        margin-right: 0.5rem;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .is-valid {
        border-color: #27ae60 !important;
    }
    
    .is-invalid {
        border-color: #e74c3c !important;
    }
    
    .field-error {
        display: block;
        margin-top: 0.25rem;
    }
`;
document.head.appendChild(spinnerStyle);