/**
 * Restaurant Management System - Interactive Features
 * Provides enhanced UX with real-time interactions, animations, and user feedback
 */

// ============================================
// TOAST NOTIFICATIONS
// ============================================

class Toast {
    static container = null;

    static init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    }

    static show(message, type = 'info', duration = 4000) {
        this.init();

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const iconMap = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <div class="toast-icon">${iconMap[type] || '•'}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        this.container.appendChild(toast);

        if (duration) {
            setTimeout(() => toast.remove(), duration);
        }

        return toast;
    }

    static success(message) {
        return this.show(message, 'success');
    }

    static error(message) {
        return this.show(message, 'error', 5000);
    }

    static warning(message) {
        return this.show(message, 'warning', 4000);
    }

    static info(message) {
        return this.show(message, 'info', 3000);
    }
}

// ============================================
// MODAL DIALOG
// ============================================

class Modal {
    constructor(options = {}) {
        this.title = options.title || 'Modal';
        this.content = options.content || '';
        this.buttons = options.buttons || [];
        this.onClose = options.onClose || null;
        this.element = null;
        this.overlay = null;
    }

    create() {
        // Overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-overlay';
        this.overlay.onclick = (e) => {
            if (e.target === this.overlay) this.close();
        };

        // Modal
        this.element = document.createElement('div');
        this.element.className = 'modal';

        // Header
        const header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = `
            <h2>${this.title}</h2>
            <button class="modal-close">×</button>
        `;

        // Body
        const body = document.createElement('div');
        body.className = 'modal-body';
        body.innerHTML = this.content;

        // Footer with buttons
        const footer = document.createElement('div');
        footer.className = 'modal-footer';
        this.buttons.forEach(btn => {
            const button = document.createElement('button');
            button.className = `btn ${btn.className || 'btn-primary'}`;
            button.textContent = btn.text;
            button.onclick = () => {
                if (btn.onClick) btn.onClick(this);
                if (btn.close !== false) this.close();
            };
            footer.appendChild(button);
        });

        this.element.appendChild(header);
        // Ensure the header close button uses the Modal.close method so body overflow is restored
        const headerClose = header.querySelector('.modal-close');
        if (headerClose) {
            headerClose.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
            });
        }
        this.element.appendChild(body);
        this.element.appendChild(footer);
        this.overlay.appendChild(this.element);
    }

    show() {
        if (!this.element) this.create();
        document.body.appendChild(this.overlay);
        this.overlay.classList.add('active');

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Close on Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                this.close();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    close() {
        if (this.overlay && this.overlay.parentElement) {
            this.overlay.remove();
            document.body.style.overflow = '';
            if (this.onClose) this.onClose();
        }
    }

    setContent(content) {
        this.content = content;
        if (this.element) {
            const bodyEl = this.element.querySelector('.modal-body');
            if (bodyEl) bodyEl.innerHTML = content;
        }
        return this;
    }

    static confirm(title, message, onConfirm, onCancel) {
        const modal = new Modal({
            title: title,
            content: `<p>${message}</p>`,
            buttons: [
                { text: 'Cancel', className: 'btn-secondary', onClick: onCancel || (() => {}) },
                { text: 'Confirm', className: 'btn-danger', onClick: onConfirm }
            ]
        });
        modal.show();
        return modal;
    }
}

// ============================================
// FORM VALIDATION
// ============================================

class FormValidator {
    static validate(formElement) {
        let isValid = true;
        const errors = [];

        const inputs = formElement.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const value = input.value.trim();
            const group = input.closest('.form-group');
            let error = null;

            // Required
            if (input.hasAttribute('required') && !value) {
                error = `${input.name || 'This field'} is required`;
            }
            // Email
            else if (input.type === 'email' && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                error = 'Please enter a valid email';
            }
            // Number
            else if (input.type === 'number' && value && isNaN(value)) {
                error = 'Please enter a valid number';
            }
            // Min length
            else if (input.hasAttribute('minlength') && value && value.length < parseInt(input.getAttribute('minlength'))) {
                error = `Minimum ${input.getAttribute('minlength')} characters required`;
            }

            if (error && group) {
                group.classList.add('has-error');
                let errorEl = group.querySelector('.form-error');
                if (!errorEl) {
                    errorEl = document.createElement('div');
                    errorEl.className = 'form-error';
                    input.parentNode.insertBefore(errorEl, input.nextSibling);
                }
                errorEl.textContent = error;
                errors.push(error);
                isValid = false;
            } else if (group) {
                group.classList.remove('has-error');
                const errorEl = group.querySelector('.form-error');
                if (errorEl) errorEl.remove();
            }
        });

        return { isValid, errors };
    }

    static clearErrors(formElement) {
        formElement.querySelectorAll('.form-group').forEach(group => {
            group.classList.remove('has-error');
            const errorEl = group.querySelector('.form-error');
            if (errorEl) errorEl.remove();
        });
    }
}

// ============================================
// TABLE FILTERING & SORTING
// ============================================

class TableManager {
    constructor(tableElement) {
        this.table = tableElement;
        this.rows = Array.from(this.table.querySelectorAll('tbody tr'));
        this.originalRows = [...this.rows];
    }

    search(query) {
        const searchTerm = query.toLowerCase();
        this.rows = this.originalRows.filter(row => {
            const text = row.textContent.toLowerCase();
            return text.includes(searchTerm);
        });
        this.render();
        return this.rows.length;
    }

    filter(columnIndex, value) {
        this.rows = this.originalRows.filter(row => {
            const cells = row.querySelectorAll('td');
            return cells[columnIndex]?.textContent.toLowerCase().includes(value.toLowerCase());
        });
        this.render();
    }

    sort(columnIndex, direction = 'asc') {
        this.rows.sort((a, b) => {
            const aText = a.querySelectorAll('td')[columnIndex]?.textContent.trim();
            const bText = b.querySelectorAll('td')[columnIndex]?.textContent.trim();

            let comparison = 0;
            if (!isNaN(aText) && !isNaN(bText)) {
                comparison = parseFloat(aText) - parseFloat(bText);
            } else {
                comparison = aText.localeCompare(bText);
            }

            return direction === 'asc' ? comparison : -comparison;
        });
        this.render();
    }

    render() {
        const tbody = this.table.querySelector('tbody');
        tbody.innerHTML = '';
        this.rows.forEach(row => {
            tbody.appendChild(row.cloneNode(true));
        });

        if (this.rows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="100%" class="text-center py-4">No results found</td></tr>';
        }
    }

    reset() {
        this.rows = [...this.originalRows];
        this.render();
    }
}

// ============================================
// LOADING STATE MANAGER
// ============================================

class LoadingState {
    static setLoading(element, isLoading = true, message = 'Loading...') {
        if (isLoading) {
            element.disabled = true;
            element.dataset.originalText = element.innerHTML;
            element.innerHTML = `<span class="spinner spinner-sm"></span> ${message}`;
            element.classList.add('disabled');
        } else {
            element.disabled = false;
            element.innerHTML = element.dataset.originalText || 'Submit';
            element.classList.remove('disabled');
        }
    }

    static createOverlay(containerId) {
        const container = document.getElementById(containerId) || document.body;
        const overlay = document.createElement('div');
        overlay.className = 'loader';
        overlay.innerHTML = '<div class="spinner spinner-lg"></div>';
        container.appendChild(overlay);
        return overlay;
    }

    static removeOverlay(overlay) {
        if (overlay) overlay.remove();
    }
}

// ============================================
// FORM AUTO-SAVE
// ============================================

class FormAutoSave {
    constructor(formElement, saveUrl, interval = 10000) {
        this.form = formElement;
        this.saveUrl = saveUrl;
        this.interval = interval;
        this.debounceTimer = null;
        this.lastSaveTime = 0;

        this.form.addEventListener('change', () => this.debouncedSave());
        this.form.addEventListener('input', () => this.debouncedSave());
    }

    debouncedSave() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.save(), 1000);
    }

    async save() {
        const now = Date.now();
        if (now - this.lastSaveTime < this.interval) return;

        const formData = new FormData(this.form);
        try {
            const response = await fetch(this.saveUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                Toast.success('Changes saved automatically');
                this.lastSaveTime = now;
            } else {
                Toast.warning('Failed to auto-save');
            }
        } catch (error) {
            console.error('Auto-save error:', error);
        }
    }
}

// ============================================
// LAZY LOADING IMAGES
// ============================================

class LazyLoadImages {
    static init() {
        if ('IntersectionObserver' in window) {
            const images = document.querySelectorAll('img[data-src]');
            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                });
            });
            images.forEach(img => observer.observe(img));
        }
    }
}

// ============================================
// SMOOTH SCROLL ANCHORS
// ============================================

class SmoothScroll {
    static init() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }
}

// ============================================
// DYNAMIC CONTENT LOADER
// ============================================

class DynamicLoader {
    static async loadContent(url, targetElement) {
        try {
            const overlay = LoadingState.createOverlay(targetElement.id || '');
            const response = await fetch(url);
            const html = await response.text();
            targetElement.innerHTML = html;
            LoadingState.removeOverlay(overlay);
            Toast.success('Content loaded');
        } catch (error) {
            console.error('Load error:', error);
            Toast.error('Failed to load content');
        }
    }
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

class KeyboardShortcuts {
    static register(shortcuts = {}) {
        document.addEventListener('keydown', (e) => {
            // Ctrl+S for search
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                const searchBox = document.querySelector('[data-search-box]');
                if (searchBox) searchBox.focus();
            }

            // Esc to close modals
            if (e.key === 'Escape') {
                const modal = document.querySelector('.modal-overlay.active');
                if (modal) {
                    modal.remove();
                    // Ensure body scrolling is restored in case the modal's close logic was bypassed
                    try { document.body.style.overflow = ''; } catch (err) { /* ignore */ }
                }
            }

            // Custom shortcuts
            Object.entries(shortcuts).forEach(([combo, callback]) => {
                if (this.matchesCombo(e, combo)) {
                    e.preventDefault();
                    callback();
                }
            });
        });
    }

    static matchesCombo(event, combo) {
        const [keys, key] = combo.includes('+') ? [combo.split('+').slice(0, -1), combo.split('+').pop()] : [[], combo];
        
        let matches = event.key.toLowerCase() === key.toLowerCase();
        matches = matches && keys.every(k => {
            switch (k.toLowerCase()) {
                case 'ctrl': return event.ctrlKey;
                case 'alt': return event.altKey;
                case 'shift': return event.shiftKey;
                default: return false;
            }
        });
        
        return matches;
    }
}

// ============================================
// COUNTDOWN TIMER
// ============================================

class CountdownTimer {
    constructor(elementId, seconds, onComplete) {
        this.element = document.getElementById(elementId);
        this.seconds = seconds;
        this.onComplete = onComplete;
        this.intervalId = null;
    }

    start() {
        let remaining = this.seconds;
        this.update(remaining);

        this.intervalId = setInterval(() => {
            remaining--;
            this.update(remaining);

            if (remaining <= 0) {
                this.stop();
                if (this.onComplete) this.onComplete();
            }
        }, 1000);

        return this;
    }

    stop() {
        clearInterval(this.intervalId);
    }

    update(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        this.element.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
}

// ============================================
// INITIALIZATION ON DOM READY
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize features
    Toast.init();
    LazyLoadImages.init();
    SmoothScroll.init();

    // Setup keyboard shortcuts
    KeyboardShortcuts.register({
        'ctrl+shift+n': () => Toast.info('New item shortcut'),
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.add('hidden');
            });
        }
    });

    // Form validation on submit
    document.querySelectorAll('form:not([data-no-validate])').forEach(form => {
        form.addEventListener('submit', (e) => {
            const validation = FormValidator.validate(form);
            if (!validation.isValid) {
                e.preventDefault();
                Toast.error('Please fix the errors in the form');
            }
        });

        // Real-time validation
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('blur', () => {
                const group = input.closest('.form-group');
                if (group) {
                    const validation = FormValidator.validate(form);
                    // Re-run validation for this field
                    if (!validation.isValid && !group.classList.contains('has-error')) {
                        group.classList.remove('has-error');
                    }
                }
            });
        });
    });

    // Add to Order item removal with confirmation
    document.querySelectorAll('[data-confirm-delete]').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            const message = element.dataset.confirmDelete || 'Are you sure?';
            Modal.confirm('Confirm Action', message, () => {
                if (element.href) window.location.href = element.href;
                else if (element.form) element.form.submit();
            });
        });
    });
});

// ============================================
// ANIMATION EFFECTS
// ============================================

class AnimationEffects {
    static fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.transition = `opacity ${duration}ms`;
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    }

    static slideDown(element, duration = 300) {
        element.style.maxHeight = '0';
        element.style.overflow = 'hidden';
        element.style.transition = `max-height ${duration}ms`;
        setTimeout(() => {
            element.style.maxHeight = element.scrollHeight + 'px';
        }, 10);
    }

    static pulse(element, count = 2) {
        let pulses = 0;
        const pulse = () => {
            element.style.opacity = element.style.opacity === '1' ? '0.5' : '1';
            pulses++;
            if (pulses < count * 2) setTimeout(pulse, 200);
        };
        pulse();
    }

    static shake(element, distance = 5, duration = 500) {
        const start = Date.now();
        const animate = () => {
            const progress = (Date.now() - start) / duration;
            const offset = Math.sin(progress * Math.PI * 8) * distance * (1 - progress);
            element.style.transform = `translateX(${offset}px)`;
            if (progress < 1) requestAnimationFrame(animate);
            else element.style.transform = '';
        };
        animate();
    }
}

// ============================================
// COLLAPSIBLE SECTIONS
// ============================================

class Collapsible {
    static init() {
        document.querySelectorAll('[data-toggle="collapse"]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = trigger.getAttribute('data-target');
                const target = document.querySelector(targetId);
                if (target) {
                    const isOpen = target.classList.contains('open');
                    target.classList.toggle('open');
                    trigger.classList.toggle('active');

                    if (!isOpen) {
                        AnimationEffects.slideDown(target, 300);
                    } else {
                        target.style.maxHeight = '0';
                    }
                }
            });
        });
    }
}

// ============================================
// TABS/TABBED CONTENT
// ============================================

class Tabs {
    static init() {
        document.querySelectorAll('[role="tablist"]').forEach(tablist => {
            const tabs = tablist.querySelectorAll('[role="tab"]');
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const tabpanelId = tab.getAttribute('aria-controls');
                    const tabpanel = document.getElementById(tabpanelId);

                    if (tabpanel) {
                        // Deactivate all tabs
                        tabs.forEach(t => {
                            t.setAttribute('aria-selected', 'false');
                            t.classList.remove('active');
                        });

                        // Hide all panels
                        tablist.parentElement.querySelectorAll('[role="tabpanel"]').forEach(panel => {
                            panel.style.display = 'none';
                        });

                        // Activate this tab
                        tab.setAttribute('aria-selected', 'true');
                        tab.classList.add('active');
                        tabpanel.style.display = 'block';
                        AnimationEffects.fadeIn(tabpanel, 200);
                    }
                });
            });

            // Activate first tab by default
            const firstTab = tabs[0];
            if (firstTab) firstTab.click();
        });
    }
}

// ============================================
// DROPDOWN MENUS
// ============================================

class DropdownMenu {
    static init() {
        document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const menu = toggle.nextElementSibling;
                if (menu && menu.classList.contains('dropdown-menu')) {
                    menu.classList.toggle('show');
                }
            });
        });

        document.addEventListener('click', () => {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        });
    }
}

// ============================================
// TOOLTIPS
// ============================================

class Tooltip {
    static show(element, text, position = 'top') {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.position = 'absolute';
        tooltip.style.zIndex = '1000';
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        const positions = {
            top: { top: rect.top - tooltipRect.height - 8, left: rect.left + rect.width / 2 - tooltipRect.width / 2 },
            bottom: { top: rect.bottom + 8, left: rect.left + rect.width / 2 - tooltipRect.width / 2 },
            left: { top: rect.top + rect.height / 2 - tooltipRect.height / 2, left: rect.left - tooltipRect.width - 8 },
            right: { top: rect.top + rect.height / 2 - tooltipRect.height / 2, left: rect.right + 8 }
        };

        const pos = positions[position] || positions.top;
        Object.assign(tooltip.style, {
            top: pos.top + window.scrollY + 'px',
            left: pos.left + window.scrollX + 'px'
        });

        setTimeout(() => tooltip.remove(), 3000);
    }

    static init() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', () => {
                Tooltip.show(element, element.dataset.tooltip, element.dataset.tooltipPosition || 'top');
            });
        });
    }
}

// ============================================
// POPOVER
// ============================================

class Popover {
    static show(element, content, title = '') {
        const popover = document.createElement('div');
        popover.className = 'popover';
        popover.innerHTML = `
            ${title ? `<div class="popover-title">${title}</div>` : ''}
            <div class="popover-body">${content}</div>
        `;
        document.body.appendChild(popover);

        const rect = element.getBoundingClientRect();
        popover.style.top = (rect.bottom + 8 + window.scrollY) + 'px';
        popover.style.left = (rect.left + window.scrollX) + 'px';

        document.addEventListener('click', () => popover.remove(), { once: true });
    }

    static init() {
        document.querySelectorAll('[data-popover]').forEach(element => {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                Popover.show(element, element.dataset.popover, element.dataset.popoverTitle);
            });
        });
    }
}

// ============================================
// PROGRESS BAR
// ============================================

class ProgressBar {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.value = 0;
    }

    set(percentage) {
        this.value = Math.min(100, Math.max(0, percentage));
        if (this.element) {
            this.element.style.width = this.value + '%';
            this.element.textContent = this.value + '%';
        }
        return this;
    }

    increment(amount = 10) {
        return this.set(this.value + amount);
    }

    complete() {
        return this.set(100);
    }
}

// ============================================
// TOGGLE SWITCH
// ============================================

class ToggleSwitch {
    static init() {
        document.querySelectorAll('.toggle-switch').forEach(toggle => {
            const input = toggle.querySelector('input[type="checkbox"]');
            if (input) {
                toggle.addEventListener('click', (e) => {
                    if (e.target !== input) {
                        input.checked = !input.checked;
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });

                input.addEventListener('change', () => {
                    toggle.classList.toggle('active', input.checked);
                });

                // Set initial state
                toggle.classList.toggle('active', input.checked);
            }
        });
    }
}

// ============================================
// AUTOCOMPLETE
// ============================================

class Autocomplete {
    constructor(inputElement, suggestions = []) {
        this.input = inputElement;
        this.suggestions = suggestions;
        this.list = null;
        this.setupEvents();
    }

    setupEvents() {
        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        document.addEventListener('click', (e) => {
            if (e.target !== this.input && this.list) this.list.remove();
        });
    }

    handleInput() {
        const value = this.input.value.toLowerCase();
        if (!value) {
            if (this.list) this.list.remove();
            return;
        }

        const matches = this.suggestions.filter(s => s.toLowerCase().includes(value));
        this.showSuggestions(matches);
    }

    handleKeydown(e) {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            const items = this.list?.querySelectorAll('.autocomplete-item');
            if (items?.length) {
                const current = this.list.querySelector('.active');
                const index = current ? Array.from(items).indexOf(current) : -1;
                const next = e.key === 'ArrowDown' ? index + 1 : index - 1;
                items.forEach(i => i.classList.remove('active'));
                if (next >= 0 && next < items.length) {
                    items[next].classList.add('active');
                    this.input.value = items[next].textContent;
                }
            }
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const active = this.list?.querySelector('.active');
            if (active) {
                this.input.value = active.textContent;
                this.list.remove();
            }
        }
    }

    showSuggestions(matches) {
        if (this.list) this.list.remove();
        if (!matches.length) return;

        this.list = document.createElement('ul');
        this.list.className = 'autocomplete-list';

        matches.slice(0, 8).forEach(match => {
            const li = document.createElement('li');
            li.className = 'autocomplete-item';
            li.textContent = match;
            li.addEventListener('click', () => {
                this.input.value = match;
                this.list.remove();
            });
            this.list.appendChild(li);
        });

        this.input.parentElement.appendChild(this.list);
    }
}

// ============================================
// INITIALIZATION ON DOM READY
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Original initializations
    Toast.init();
    LazyLoadImages.init();
    SmoothScroll.init();

    // New enhanced initializations
    Collapsible.init();
    Tabs.init();
    DropdownMenu.init();
    Tooltip.init();
    Popover.init();
    ToggleSwitch.init();

    // Setup keyboard shortcuts
    KeyboardShortcuts.register({
        'ctrl+shift+n': () => Toast.info('New item shortcut'),
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.add('hidden');
            });
        }
    });

    // Form validation on submit
    document.querySelectorAll('form:not([data-no-validate])').forEach(form => {
        form.addEventListener('submit', (e) => {
            const validation = FormValidator.validate(form);
            if (!validation.isValid) {
                e.preventDefault();
                Toast.error('Please fix the errors in the form');
            }
        });

        // Real-time validation
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('blur', () => {
                const group = input.closest('.form-group');
                if (group) {
                    const validation = FormValidator.validate(form);
                    // Re-run validation for this field
                    if (!validation.isValid && !group.classList.contains('has-error')) {
                        group.classList.remove('has-error');
                    }
                }
            });
        });
    });

    // Add to Order item removal with confirmation
    document.querySelectorAll('[data-confirm-delete]').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            const message = element.dataset.confirmDelete || 'Are you sure?';
            Modal.confirm('Confirm Action', message, () => {
                if (element.href) window.location.href = element.href;
                else if (element.form) element.form.submit();
            });
        });
    });
});

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Toast, Modal, FormValidator, TableManager, LoadingState, FormAutoSave, AnimationEffects, Collapsible, Tabs, DropdownMenu, Tooltip, Popover, ProgressBar, ToggleSwitch, Autocomplete };
}
