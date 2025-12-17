// Menu Item List Template JavaScript - Delete Confirmation

/**
 * Get CSRF token from cookies
 * @returns {string} CSRF token value
 */
function getCsrfToken() {
    let token = '';
    const cookieValue = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    if (cookieValue) {
        token = cookieValue.split('=')[1];
    }
    return token;
}

/**
 * Initialize delete modal functionality
 */
function initializeDeleteModal() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const modal = document.getElementById('deleteModal');
    const deleteForm = document.getElementById('deleteForm');
    const cancelBtns = document.querySelectorAll('#cancelDelete, #cancelDelete2');

    if (!modal) return;

    const bsModal = new bootstrap.Modal(modal);

    // Setup delete button click handlers
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            if (url) {
                deleteForm.action = url;
                bsModal.show();
            }
        });
    });

    // Setup cancel button handlers
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            bsModal.hide();
            deleteForm.action = '';
        });
    });

    // Close modal on Escape key
    modal.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            bsModal.hide();
        }
    });
}

/**
 * Handle table row interactions
 */
function initializeTableInteractions() {
    const rows = document.querySelectorAll('.menuitem-table tbody tr');
    
    rows.forEach(row => {
        // Add hover effect
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'background-color 0.2s ease';
        });

        // Handle action buttons
        const buttons = row.querySelectorAll('.menuitem-btn-view, .menuitem-btn-edit');
        buttons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                // Allow default link behavior
                return true;
            });
        });
    });
}

/**
 * Initialize the menu item list page
 */
document.addEventListener('DOMContentLoaded', function () {
    initializeDeleteModal();
    initializeTableInteractions();
});

/**
 * Refresh the menu item list (useful for AJAX operations)
 */
function refreshMenuItemList() {
    location.reload();
}

/**
 * Highlight a specific menu item row
 * @param {number} itemId - The ID of the menu item to highlight
 */
function highlightMenuItem(itemId) {
    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
    if (row) {
        row.style.background = '#d4edda';
        setTimeout(() => {
            row.style.background = '';
        }, 2000);
    }
}
