/**
 * RESPONSIVE & INTERACTIVE UTILITIES
 * Enhances the existing interactive.js with additional features
 */

// ===========================
// TOUCH & MOBILE OPTIMIZATION
// ===========================

function initTouchOptimization() {
    const isTouchDevice = () => {
        return (('ontouchstart' in window) ||
                (navigator.maxTouchPoints > 0) ||
                (navigator.msMaxTouchPoints > 0));
    };

    if (isTouchDevice()) {
        document.body.classList.add('touch-device');
        
        // Add tap feedback
        document.querySelectorAll('button, .btn, a.btn, [type="submit"], input, select').forEach(elem => {
            elem.addEventListener('touchstart', function() {
                this.style.opacity = '0.7';
            });
            elem.addEventListener('touchend', function() {
                this.style.opacity = '1';
            });
        });

        // Prevent double-tap zoom on buttons
        document.querySelectorAll('button, .btn, a.btn').forEach(elem => {
            let lastTouchTime = 0;
            elem.addEventListener('touchend', function(e) {
                const currentTime = new Date().getTime();
                const tapLength = currentTime - lastTouchTime;
                if (tapLength < 300 && tapLength > 0) {
                    e.preventDefault();
                }
                lastTouchTime = currentTime;
            });
        });
    }
}

// ===========================
// RESPONSIVE MENU HANDLER
// ===========================

function initResponsiveMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.nav-link');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // Close menu when clicking on a link
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarCollapse.classList.remove('show');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const navbar = document.querySelector('.navbar');
            if (navbar && !navbar.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

// ===========================
// FORM INTERACTIVE ENHANCEMENTS
// ===========================

function initFormEnhancements() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            // Add focus styles
            input.addEventListener('focus', function() {
                this.parentElement.classList?.add('focused');
            });

            input.addEventListener('blur', function() {
                this.parentElement.classList?.remove('focused');
            });

            // Real-time validation feedback
            input.addEventListener('input', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.classList.add('input-error');
                    this.classList.remove('input-success');
                } else if (this.value.trim()) {
                    this.classList.remove('input-error');
                    this.classList.add('input-success');
                }
            });
        });

        // Form submission feedback
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-sm"></span> Processing...';
                
                // Re-enable after delay (you can adjust based on actual submission)
                setTimeout(() => {
                    if (!this.classList.contains('submitted')) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = 'Submit';
                    }
                }, 2000);
            }
        });
    });
}

// ===========================
// TABLE INTERACTIVE FEATURES
// ===========================

function initTableFeatures() {
    const tables = document.querySelectorAll('table');

    tables.forEach(table => {
        // Add hover effects to rows
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#FAFAFA';
            });
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });

        // Make headers sticky on scroll
        const thead = table.querySelector('thead');
        if (thead) {
            thead.style.position = 'sticky';
            thead.style.top = '0';
            thead.style.zIndex = '10';
        }

        // Sortable table columns (if data-sortable is present)
        if (table.hasAttribute('data-sortable')) {
            const headers = table.querySelectorAll('thead th');
            headers.forEach((header, index) => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTableColumn(table, index));
            });
        }
    });
}

function sortTableColumn(table, columnIndex) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isAscending = !table.dataset.sortAsc;

    rows.sort((a, b) => {
        const aVal = a.children[columnIndex].textContent;
        const bVal = b.children[columnIndex].textContent;

        // Try numeric sort
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }

        // String sort
        return isAscending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });

    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));

    table.dataset.sortAsc = isAscending;
}

// ===========================
// MODAL ENHANCEMENTS
// ===========================

function initModalEnhancements() {
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const bsModal = bootstrap?.Modal?.getInstance(modal);
                if (bsModal) bsModal.hide();
            }
        });

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                const bsModal = bootstrap?.Modal?.getInstance(modal);
                if (bsModal) bsModal.hide();
            }
        });
    });
}

// ===========================
// DROPDOWN ENHANCEMENTS
// ===========================

function initDropdownEnhancements() {
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (toggle && menu) {
            // Keyboard navigation
            toggle.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown' || e.key === ' ' || e.key === 'Enter') {
                    e.preventDefault();
                    menu.classList.add('show');
                    const items = menu.querySelectorAll('a, button');
                    if (items.length) items[0].focus();
                }
            });

            // Navigate menu items with arrow keys
            const items = menu.querySelectorAll('a, button');
            items.forEach((item, index) => {
                item.addEventListener('keydown', (e) => {
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        const nextItem = items[index + 1];
                        if (nextItem) nextItem.focus();
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        const prevItem = items[index - 1];
                        if (prevItem) prevItem.focus();
                    }
                });
            });
        }
    });
}

// ===========================
// SEARCH & FILTER OPTIMIZATION
// ===========================

function initSearchFilter() {
    const searchInputs = document.querySelectorAll('[data-searchable]');

    searchInputs.forEach(input => {
        const targetSelector = input.getAttribute('data-searchable');
        const items = document.querySelectorAll(targetSelector);

        const debounceSearch = debounce(function() {
            const query = input.value.toLowerCase();
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(query) ? '' : 'none';
            });
        }, 300);

        input.addEventListener('input', debounceSearch);
    });
}

function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// ===========================
// LAZY LOADING IMAGES
// ===========================

function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// ===========================
// SCROLL ANIMATIONS
// ===========================

function initScrollAnimations() {
    const elements = document.querySelectorAll('[data-animate]');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        elements.forEach(elem => observer.observe(elem));
    }
}

// ===========================
// KEYBOARD NAVIGATION
// ===========================

function initKeyboardNavigation() {
    // Focus visible for keyboard users
    document.addEventListener('keydown', () => {
        document.body.classList.add('keyboard-active');
    });

    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-active');
    });

    // Skip to main content link
    const skipLink = document.querySelector('.skip-to-main');
    if (skipLink) {
        skipLink.addEventListener('click', (e) => {
            e.preventDefault();
            const main = document.querySelector('main');
            if (main) {
                main.focus();
                main.scrollIntoView();
            }
        });
    }
}

// ===========================
// NOTIFICATION SYSTEM ENHANCEMENT
// ===========================

function showAlert(message, type = 'info') {
    if (typeof Toast !== 'undefined' && Toast.show) {
        Toast.show(message, type);
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// ===========================
// LOCAL STORAGE UTILITIES
// ===========================

const Storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Storage error:', e);
        }
    },
    get: (key) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Storage error:', e);
            return null;
        }
    },
    remove: (key) => localStorage.removeItem(key),
    clear: () => localStorage.clear()
};

// ===========================
// INITIALIZATION
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing responsive features...');
    
    initTouchOptimization();
    initResponsiveMenu();
    initFormEnhancements();
    initTableFeatures();
    initModalEnhancements();
    initDropdownEnhancements();
    initSearchFilter();
    initLazyLoading();
    initScrollAnimations();
    initKeyboardNavigation();

    console.log('✓ All responsive features initialized');
});

// ===========================
// UTILITY FUNCTIONS
// ===========================

// Copy to clipboard
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    });
};

// Format currency
window.formatCurrency = function(amount) {
    return `Rs. ${parseFloat(amount).toFixed(2)}`;
};

// Smooth scroll
window.smoothScroll = function(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
};

// Check if element is in viewport
window.isInViewport = function(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
};
