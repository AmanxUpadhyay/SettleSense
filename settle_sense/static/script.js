/**
 * SettleSense - Professional Debt Tracking Application
 * Frontend interaction scripts
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Format currency inputs
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('blur', function(e) {
            if (e.target.value) {
                const value = parseFloat(e.target.value);
                if (!isNaN(value)) {
                    e.target.value = value.toFixed(2);
                }
            }
        });
    }
    
    // Table row hover effect
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseover', () => {
            row.style.backgroundColor = '#f8f9fa';
        });
        row.addEventListener('mouseout', () => {
            row.style.backgroundColor = '';
        });
    });
    
    // Person name autocomplete improvement
    const personInput = document.getElementById('person');
    if (personInput) {
        personInput.addEventListener('input', function() {
            this.value = this.value.trim();
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-focus first input on page load
    if (document.querySelector('form')) {
        const firstInput = document.querySelector('form input:not([type=hidden]):not([disabled]):not([readonly])');
        if (firstInput) {
            firstInput.focus();
        }
    }
    
    // Confirm form submissions that could result in data change
    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.dataset.confirm || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Update date/time display
    function updateTimestamps() {
        const timestamps = document.querySelectorAll('.timestamp');
        timestamps.forEach(el => {
            const date = new Date(el.dataset.time);
            el.textContent = date.toLocaleString();
        });
    }
    
    if (document.querySelectorAll('.timestamp').length > 0) {
        updateTimestamps();
    }
    
    // Analytics data
    function fetchSummaryData() {
        fetch('/api/summary')
            .then(response => response.json())
            .then(data => {
                if (window.summaryChart) {
                    updateSummaryChart(data);
                }
            })
            .catch(error => console.error('Error fetching summary data:', error));
    }
    
    // If there's a chart element, initialize it
    const chartElement = document.getElementById('balanceChart');
    if (chartElement) {
        // This would require a chart library like Chart.js
        // Implementation would go here
    }
    
    console.log('SettleSense scripts initialized successfully');
});
