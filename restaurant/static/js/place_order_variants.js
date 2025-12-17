// Shared place order functionality for takeaway and delivery orders

const menuItems = JSON.parse('{{ menu_items_json|safe }}');

let orderData = {};
let totalForms = 0;

document.addEventListener('DOMContentLoaded', () => {
    renderCategories();
    renderItemsGrid();
    setupCategoryFilters();
    setupFormSubmit();
});

function renderCategories() {
    const categories = [...new Set(menuItems.map(item => item['category__name']))];
    const filterContainer = document.getElementById('category-filter');
    
    const allBtn = document.createElement('button');
    allBtn.type = 'button';
    allBtn.className = 'category-btn active';
    allBtn.textContent = 'All Items';
    allBtn.dataset.category = 'all';
    allBtn.onclick = (e) => {
        e.preventDefault();
        document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
        allBtn.classList.add('active');
        renderItemsGrid('all');
    };
    filterContainer.appendChild(allBtn);
    
    categories.forEach(cat => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'category-btn';
        btn.textContent = cat;
        btn.dataset.category = cat;
        btn.onclick = (e) => {
            e.preventDefault();
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderItemsGrid(cat);
        };
        filterContainer.appendChild(btn);
    });
}

function renderItemsGrid(categoryFilter = 'all') {
    const grid = document.getElementById('items-grid');
    grid.innerHTML = '';
    
    const filtered = categoryFilter === 'all' 
        ? menuItems 
        : menuItems.filter(item => item['category__name'] === categoryFilter);
    
    filtered.forEach(item => {
        const card = document.createElement('div');
        card.className = `item-card ${orderData[item.id] ? 'selected' : ''}`;
        card.innerHTML = `
            <div class="item-name">${item.name}</div>
            <div class="item-price">Rs.${item.price.toFixed(2)}</div>
            <div class="small text-muted mb-2">${item['category__name']}</div>
            <div class="item-quick-add">
                <input type="number" class="form-control form-control-sm item-qty-input" value="${orderData[item.id] ? orderData[item.id].qty : 1}" min="1">
                <button type="button" class="btn btn-primary item-add-btn" onclick="quickAddItem(event, ${item.id}, '${item.name}', ${item.price})">
                    <i class="fas fa-plus"></i> Add
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function quickAddItem(e, itemId, itemName, price) {
    e.preventDefault();
    const card = e.target.closest('.item-card');
    const qty = parseInt(card.querySelector('.item-qty-input').value) || 1;
    
    if (orderData[itemId]) {
        orderData[itemId].qty += qty;
    } else {
        orderData[itemId] = { name: itemName, price, qty, category: '' };
    }
    
    renderItemsGrid();
    addToOrderTable(itemId, itemName, price, qty);
    calculateTotal();
    showNotification(`${itemName} added to order!`);
}

function addToOrderTable(itemId, itemName, price, qty) {
    const existingRow = document.querySelector(`[data-item-id="${itemId}"]`);
    if (existingRow) {
        const qtyInput = existingRow.querySelector('.quantity-input');
        qtyInput.value = parseInt(qtyInput.value) + qty;
        updateRowPrices(existingRow);
        return;
    }
    
    const tbody = document.getElementById('order-items');
    const tr = document.createElement('tr');
    tr.className = 'order-item-row';
    tr.dataset.itemId = itemId;
    
    tr.innerHTML = `
        <td><strong>${itemName}</strong></td>
        <td>
            <input type="number" 
                   name="form-${totalForms}-quantity" 
                   value="${qty}" 
                   min="1" 
                   class="form-control form-control-sm quantity-input"
                   required>
            <input type="hidden" name="form-${totalForms}-item" value="${itemId}">
        </td>
        <td class="text-end item-price">Rs.${price.toFixed(2)}</td>
        <td class="text-end item-subtotal">Rs.${(price * qty).toFixed(2)}</td>
        <td class="text-center">
            <button type="button" 
                    onclick="removeOrderItem(this)" 
                    class="btn btn-sm btn-outline-danger"
                    title="Remove">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    tbody.appendChild(tr);
    totalForms++;
    updateFormMeta();
    
    const qtyInput = tr.querySelector('.quantity-input');
    qtyInput.addEventListener('input', () => updateRowPrices(tr));
}

function removeOrderItem(button) {
    const row = button.closest('.order-item-row');
    const itemId = row.dataset.itemId;
    const itemName = row.querySelector('strong').textContent;
    
    delete orderData[itemId];
    row.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => {
        row.remove();
        updateFormIndexes();
        calculateTotal();
        renderItemsGrid();
        showNotification(`${itemName} removed from order!`);
    }, 300);
}

function updateFormIndexes() {
    const rows = document.querySelectorAll('.order-item-row');
    rows.forEach((row, index) => {
        row.querySelector('input[name^="form-"][name$="-quantity"]').name = `form-${index}-quantity`;
        row.querySelector('input[name^="form-"][name$="-item"]').name = `form-${index}-item`;
    });
    totalForms = rows.length;
    updateFormMeta();
}

function updateFormMeta() {
    const input = document.getElementById('id_form-TOTAL_FORMS');
    if (input) input.value = totalForms;
}

function updateRowPrices(row) {
    const quantityInput = row.querySelector('.quantity-input');
    const itemId = row.dataset.itemId;
    const item = menuItems.find(m => m.id === parseInt(itemId));
    
    if (!item) return;
    
    const quantity = parseInt(quantityInput.value) || 0;
    const subtotal = item.price * quantity;
    
    row.querySelector('.item-price').textContent = `Rs.${item.price.toFixed(2)}`;
    row.querySelector('.item-subtotal').textContent = `Rs.${subtotal.toFixed(2)}`;
    
    if (orderData[itemId]) {
        orderData[itemId].qty = quantity;
    }
    
    calculateTotal();
}

function calculateTotal() {
    let total = 0;
    let itemCount = 0;
    document.querySelectorAll('.order-item-row').forEach(row => {
        const subtotal = parseFloat(row.querySelector('.item-subtotal').textContent.replace('Rs.', '')) || 0;
        const qty = parseInt(row.querySelector('.quantity-input').value) || 0;
        total += subtotal;
        itemCount += qty;
    });
    
    document.getElementById('total-amount').textContent = `Rs.${total.toFixed(2)}`;
    const summaryItems = document.getElementById('summary-items');
    const summaryTotal = document.getElementById('summary-total');
    if (summaryItems) summaryItems.textContent = itemCount;
    if (summaryTotal) summaryTotal.textContent = `Rs.${total.toFixed(2)}`;
    
    const summaryItemsDesktop = document.getElementById('summary-items-desktop');
    const summaryTotalDesktop = document.getElementById('summary-total-desktop');
    if (summaryItemsDesktop) summaryItemsDesktop.textContent = itemCount;
    if (summaryTotalDesktop) summaryTotalDesktop.textContent = `Rs.${total.toFixed(2)}`;
}

function showNotification(message) {
    const notif = document.createElement('div');
    notif.className = 'toast-notification';
    notif.innerHTML = `<i class="fas fa-check-circle me-2" style="color:#28a745;"></i>${message}`;
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notif.remove(), 300);
    }, 2000);
}

function setupCategoryFilters() {
    // Already handled in renderCategories
}

function setupFormSubmit() {
    const form = document.getElementById('orderForm');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        const orderRows = document.querySelectorAll('.order-item-row');
        if (orderRows.length === 0) {
            e.preventDefault();
            alert('Please add at least one item to the order before placing it.');
            return;
        }
        
        const customerName = form.querySelector('input[name="customer_name"]');
        const customerPhone = form.querySelector('input[name="customer_phone"]');
        
        if ((customerName && !customerName.value.trim()) || (customerPhone && !customerPhone.value.trim())) {
            e.preventDefault();
            alert('Please fill in all required customer information.');
            return;
        }
        
        const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
        if (totalFormsInput) totalFormsInput.value = orderRows.length;
    });
}
