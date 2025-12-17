// Order Item Management Functions

function openAddItemModal() {
    const modal = document.getElementById('add-item-modal');
    if (!modal) return;
    modal.classList.remove('d-none');
    modal.classList.add('active');
    filterMenuItems();
}

function closeAddItemModal() {
    const modal = document.getElementById('add-item-modal');
    if (!modal) return;
    modal.classList.add('d-none');
    modal.classList.remove('active');
    const cat = document.getElementById('category-filter');
    const qty = document.getElementById('item-quantity');
    if (cat) cat.value = '';
    if (qty) qty.value = 1;
}

function filterMenuItems() {
    const categoryId = document.getElementById('category-filter') ? document.getElementById('category-filter').value : '';
    const menuItems = document.getElementById('menu-item');
    if (!menuItems) return;
    const options = menuItems.options;
    for (let i = 0; i < options.length; i++) {
        const item = options[i];
        if (!categoryId || item.dataset.category === categoryId) {
            item.hidden = false;
        } else {
            item.hidden = true;
        }
    }
}

function calculateTotal(baseTotal, deliveryCharge = 0) {
    return parseFloat(baseTotal) + parseFloat(deliveryCharge);
}

function updateDisplayTotals(subtotal, deliveryCharge = 0) {
    const total = calculateTotal(subtotal, deliveryCharge);
    const canonical = document.getElementById('canonical-total');
    if (canonical) {
        canonical.dataset.total = total;
        canonical.textContent = `Rs.${total.toFixed(2)}`;
    }
    updateRemainingAmount();
}

function updateRemainingAmount() {
    let totalAmount = 0;
    const canonical = document.getElementById('canonical-total');
    
    if (canonical && canonical.dataset && canonical.dataset.total) {
        totalAmount = parseFloat(canonical.dataset.total) || 0;
    } 
    
    if (totalAmount === 0 && canonical) {
        const text = canonical.textContent || canonical.innerText || '';
        totalAmount = parseFloat(text.replace(/[^0-9.-]+/g, '')) || 0;
    }

    let settledAmount = 0;
    const paymentElements = document.querySelectorAll('.payment-amount');
    paymentElements.forEach((element) => {
        const text = element.textContent || element.innerText || '';
        const cleanedText = text.replace(/Rs\.?\s*/g, '').trim();
        const amount = parseFloat(cleanedText) || 0;
        settledAmount += amount;
    });

    let pendingAmount = 0;
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(input => {
        pendingAmount += parseFloat(input.value) || 0;
    });

    const remainingAmount = totalAmount - settledAmount - pendingAmount;
    const remainingEl = document.getElementById('remaining-amount');
    if (remainingEl) remainingEl.textContent = 'Rs. ' + Number(remainingAmount || 0).toFixed(2);

    const remainingContainer = remainingEl ? remainingEl.parentElement : null;
    if (remainingContainer) {
        if (remainingAmount < 0) {
            remainingContainer.classList.add('text-danger');
        } else {
            remainingContainer.classList.remove('text-danger');
        }
    }

    try { if (window.updateRemaining) window.updateRemaining(); } catch (e) { }
}

function addItemToOrder() {
    const menuItemSelect = document.getElementById('menu-item');
    if (!menuItemSelect) { alert('Menu item selector not found'); return; }
    const selectedOption = menuItemSelect.options[menuItemSelect.selectedIndex];
    const quantityEl = document.getElementById('item-quantity');
    const quantity = quantityEl ? parseInt(quantityEl.value) : 1;
    const itemId = menuItemSelect.value;
    if (!itemId || !quantity || quantity < 1) {
        alert('Please select an item and enter a valid quantity');
        return;
    }

    fetch(`/order/${orderId}/add_item/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify({
            item_id: parseInt(itemId),
            quantity: quantity
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => { throw new Error(data.message || 'Failed to add item'); });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const tbody = document.querySelector('#order-items-table tbody');
            if (!tbody) return;
            const existingRow = document.getElementById(`item-row-${data.item_html.item_id}`);
            if (existingRow) {
                const qtyInput = existingRow.querySelector('input[type="number"]');
                if (qtyInput) qtyInput.value = data.item_html.quantity;
                const totalCell = existingRow.querySelector('td:nth-child(4)');
                if (totalCell) totalCell.textContent = `Rs.${data.item_html.total}`;
            } else {
                const newRow = document.createElement('tr');
                newRow.id = `item-row-${data.item_html.item_id}`;
                newRow.innerHTML = `
                    <td class="py-2 px-3 border-bottom">${data.item_html.name}</td>
                    <td class="py-2 px-3 border-bottom text-center">
                        <input type="number" 
                               value="${data.item_html.quantity}" 
                               min="1" 
                               class="w-20 px-2 py-1 border rounded"
                               onchange="updateItemQuantity(${data.item_html.item_id}, this.value)">
                    </td>
                    <td class="py-2 px-3 border-bottom text-right">Rs.${data.item_html.price}</td>
                    <td class="py-2 px-3 border-bottom text-right">Rs.${data.item_html.total}</td>
                    <td class="py-2 px-3 border-bottom text-center">
                        <button onclick="removeOrderItem(${data.item_html.item_id})" class="btn btn-sm btn-danger">Remove</button>
                    </td>
                `;
                tbody.appendChild(newRow);
            }
            updateDisplayTotals(data.new_total);
            closeAddItemModal();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message || 'Error adding item. Please try again.');
    });
}

function updateItemQuantity(itemId, newQuantity) {
    if (newQuantity < 1) {
        alert('Quantity must be at least 1');
        return;
    }

    fetch(`/restaurant/order/${orderId}/add_item/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: newQuantity,
            update: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const row = document.getElementById(`item-row-${itemId}`);
            if (row) row.querySelector('td:nth-child(4)').textContent = `Rs.${data.item_html.total}`;
            updateDisplayTotals(data.new_total);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating quantity');
    });
}

function editOrderItem(itemId, currentQty, itemPrice) {
    const qtyCell = document.querySelector(`.qty-cell-${itemId}`);
    const editBtn = document.querySelector(`.edit-btn-${itemId}`);
    const saveBtn = document.querySelector(`.save-btn-${itemId}`);
    
    if (!qtyCell) return;
    
    qtyCell.innerHTML = `<input type="number" id="qty-input-${itemId}" min="1" value="${currentQty}" class="form-control" style="width: 80px; margin: 0 auto;">`;
    
    editBtn.classList.add('d-none');
    saveBtn.classList.remove('d-none');
    
    document.getElementById(`qty-input-${itemId}`).focus();
}

function saveOrderItem(itemId) {
    const qtyInput = document.getElementById(`qty-input-${itemId}`);
    if (!qtyInput) return;
    
    const newQty = parseInt(qtyInput.value);
    if (!newQty || newQty < 1) {
        alert('Please enter a valid quantity');
        return;
    }
    
    fetch(`/order/${orderId}/update_item/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify({
            quantity: newQty
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const qtyCell = document.querySelector(`.qty-cell-${itemId}`);
            const totalCell = document.querySelector(`.total-cell-${itemId}`);
            const editBtn = document.querySelector(`.edit-btn-${itemId}`);
            const saveBtn = document.querySelector(`.save-btn-${itemId}`);
            
            qtyCell.textContent = newQty;
            totalCell.textContent = `Rs.${(newQty * data.item_price).toFixed(2)}`;
            
            editBtn.classList.remove('d-none');
            saveBtn.classList.add('d-none');
            
            updateDisplayTotals(data.new_total);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating item quantity');
    });
}

function removeOrderItem(itemId) {
    if (!confirm('Are you sure you want to remove this item?')) {
        return;
    }

    fetch(`/order/${orderId}/remove_item/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const row = document.getElementById(`item-row-${itemId}`);
            if (row) row.remove();
            updateDisplayTotals(data.new_total);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error removing item');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const addItemModal = document.getElementById('add-item-modal');
    if (addItemModal) {
        addItemModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeAddItemModal();
            }
        });
    }

    updateRemainingAmount();
    setTimeout(() => updateRemainingAmount(), 100);
});
