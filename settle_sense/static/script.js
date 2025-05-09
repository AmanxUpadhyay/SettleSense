/**
 * SettleSense - Professional Debt Tracking Application
 * Frontend interaction scripts
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // Check for saved theme preference in localStorage
    const savedTheme = localStorage.getItem('settlesense-theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        document.body.setAttribute('data-theme', savedTheme);
    }
    
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
        if (timestamps.length === 0) return;
        
        timestamps.forEach(el => {
            const date = new Date(el.getAttribute('data-time'));
            if (isNaN(date.getTime())) return;
            
            // Calculate time difference
            const now = new Date();
            const diffMs = now - date;
            const diffSec = Math.round(diffMs / 1000);
            const diffMin = Math.round(diffSec / 60);
            const diffHour = Math.round(diffMin / 60);
            const diffDay = Math.round(diffHour / 24);
            
            // Format display text
            let displayText;
            if (diffSec < 60) {
                displayText = 'Just now';
            } else if (diffMin < 60) {
                displayText = `${diffMin}m ago`;
            } else if (diffHour < 24) {
                displayText = `${diffHour}h ago`;
            } else if (diffDay < 7) {
                displayText = `${diffDay}d ago`;
            } else {
                displayText = date.toLocaleDateString();
            }
            
            el.textContent = displayText;
        });
    }
    
    if (document.querySelectorAll('.timestamp').length > 0) {
        updateTimestamps();
    }
    
    // Enhanced search functionality
    const searchFilterForm = document.getElementById('searchFilterForm');
    if (searchFilterForm) {
        // Handle person dropdown change to auto-submit
        const personFilter = searchFilterForm.querySelector('select[name="person"]');
        if (personFilter) {
            personFilter.addEventListener('change', function() {
                searchFilterForm.submit();
            });
        }
        
        // Handle direction dropdown change to auto-submit
        const directionFilter = searchFilterForm.querySelector('select[name="direction"]');
        if (directionFilter) {
            directionFilter.addEventListener('change', function() {
                searchFilterForm.submit();
            });
        }
        
        // Add reset button functionality
        const searchInput = searchFilterForm.querySelector('input[name="search"]');
        if (searchInput && searchInput.value) {
            // Create clear search button
            const clearBtn = document.createElement('button');
            clearBtn.type = 'button';
            clearBtn.className = 'btn btn-outline-secondary';
            clearBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
            clearBtn.title = 'Clear search';
            clearBtn.setAttribute('aria-label', 'Clear search');
            
            // Add clear button next to search input
            searchInput.insertAdjacentElement('afterend', clearBtn);
            
            // Add click handler to clear and submit
            clearBtn.addEventListener('click', function() {
                searchInput.value = '';
                searchFilterForm.submit();
            });
        }
    }
    
    // Analytics data
    function fetchSummaryData() {
        fetch('/api/summary')
            .then(response => response.json())
            .then(data => {
                // Update any live data elements
                console.log('Fetched summary data:', data);
            })
            .catch(error => console.error('Error fetching summary data:', error));
    }
    
    // If there's a chart element, initialize it
    const chartElement = document.getElementById('balanceChart');
    if (chartElement) {
        // Chart.js implementation is handled in the template
    }
    
    // Apply theme from settings
    function applyTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        document.body.setAttribute('data-theme', currentTheme);
        
        // Store the theme preference in localStorage for session persistence
        localStorage.setItem('settlesense-theme', currentTheme);
        
        // Update chart colors based on theme if charts exist
        const chartElements = document.querySelectorAll('canvas');
        if (window.Chart && chartElements.length > 0) {
            const isDark = currentTheme === 'dark';
            
            // Apply theme to existing charts
            Object.values(Chart.instances || {}).forEach(chart => {
                if (chart.config && chart.config.options && chart.options.scales) {
                    try {
                        // Update grid colors
                        if (chart.options.scales.x) {
                            chart.options.scales.x.grid.color = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
                        }
                        if (chart.options.scales.y) {
                            chart.options.scales.y.grid.color = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
                        }
                        
                        // Update text colors
                        if (chart.options.plugins && chart.options.plugins.title) {
                            chart.options.plugins.title.color = isDark ? '#e0e0e0' : '#333';
                        }
                        if (chart.options.plugins && chart.options.plugins.legend) {
                            chart.options.plugins.legend.labels = chart.options.plugins.legend.labels || {};
                            chart.options.plugins.legend.labels.color = isDark ? '#e0e0e0' : '#333';
                        }
                        
                        chart.update();
                    } catch (e) {
                        console.log('Error updating chart theme:', e);
                    }
                }
            });
        }
        
        // Update any modals that might be open
        const modals = document.querySelectorAll('.modal-content');
        if (modals) {
            modals.forEach(modal => {
                if (isDark) {
                    modal.classList.add('dark-mode');
                } else {
                    modal.classList.remove('dark-mode');
                }
            });
        }
    }
    
    // Apply theme on page load
    applyTheme();
    
    console.log('SettleSense scripts initialized successfully');
});
