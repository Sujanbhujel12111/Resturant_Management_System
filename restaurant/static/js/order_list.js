// Order list filtering and bulk actions

function filterOrders() {
    const searchTerm = document.getElementById('orderSearch').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value.toLowerCase();

    document.querySelectorAll('#ordersBody tr').forEach(row => {
        let show = true;

        if (searchTerm && !row.textContent.toLowerCase().includes(searchTerm)) {
            show = false;
        }

        if (statusFilter) {
            const statusSelect = row.querySelector('select[name="status"]');
            let statusText = '';
            if (statusSelect) {
                const sel = statusSelect.options[statusSelect.selectedIndex];
                statusText = (sel && sel.textContent) ? sel.textContent.toLowerCase() : '';
            } else {
                statusText = row.textContent.toLowerCase();
            }
            if (!statusText.includes(statusFilter)) {
                show = false;
            }
        }

        if (typeFilter) {
            const typeCell = row.querySelector('td:nth-child(3)');
            const typeText = typeCell ? typeCell.textContent.toLowerCase() : row.textContent.toLowerCase();
            if (typeFilter === 'table' && !typeText.includes('table')) {
                show = false;
            } else if (typeFilter === 'takeaway' && !typeText.includes('takeaway')) {
                show = false;
            } else if (typeFilter === 'delivery' && !typeText.includes('delivery')) {
                show = false;
            }
        }

        row.style.display = show ? '' : 'none';
    });
}

function toggleSelectAll(checkbox) {
    const visibleCheckboxes = document.querySelectorAll('#ordersBody tr:not([style*="display: none"]) .order-checkbox');
    visibleCheckboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBulkActionButton();
}

function updateBulkActionButton() {
    const selectedCheckboxes = document.querySelectorAll('.order-checkbox:checked');
    const bulkCancelBtn = document.getElementById('bulkCancelBtn');
    
    if (selectedCheckboxes.length > 0) {
        bulkCancelBtn.style.display = 'inline-block';
    } else {
        bulkCancelBtn.style.display = 'none';
        document.getElementById('selectAll').checked = false;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function bulkCancelOrders() {
    const selectedCheckboxes = document.querySelectorAll('.order-checkbox:checked');
    const selectedOrders = Array.from(selectedCheckboxes).map(cb => ({
        id: cb.value,
        row: cb.closest('tr')
    }));

    if (selectedOrders.length === 0) {
        alert('Please select at least one order to cancel');
        return;
    }

    let paidOrders = [];
    selectedOrders.forEach(order => {
        const hasPayment = order.row.getAttribute('data-has-payment') === 'true';
        if (hasPayment) {
            const orderNumber = order.row.getAttribute('data-order-number');
            paidOrders.push(orderNumber);
        }
    });

    if (paidOrders.length > 0) {
        const orderList = paidOrders.join(', ');
        alert('Cannot cancel these orders - Please clear the payment first:\n\nOrder Numbers: ' + orderList);
        return;
    }

    const confirmMessage = `Are you sure you want to cancel ${selectedOrders.length} order(s)?\n\nThis action cannot be undone.`;
    
    if (confirm(confirmMessage)) {
        const orderIds = selectedOrders.map(o => o.id);
        
        fetch('{% url "restaurant:bulk_cancel_orders" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                order_ids: orderIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Successfully cancelled ${data.cancelled_count} order(s)`);
                location.reload();
            } else {
                alert('Error: ' + (data.message || 'Failed to cancel orders'));
            }
        })
        .catch(error => {
            alert('Error: ' + error);
            console.error('Error:', error);
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    try {
        const table = document.getElementById('ordersTable');
        if (!table) return;
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        table.querySelectorAll('tbody tr').forEach(row => {
            Array.from(row.querySelectorAll('td')).forEach((td, i) => {
                if (headers[i]) td.setAttribute('data-label', headers[i]);
            });
        });
    } catch (e) {
        console.warn('Failed to set data-labels for responsive table', e);
    }
});
