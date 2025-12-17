// Initialize kitchen board
function initializeKitchenBoard(ordersDataArg) {
    const pendingColumn = document.getElementById('pending-column');
    const cookingColumn = document.getElementById('cooking-column');
    const readyColumn = document.getElementById('ready-column');

    pendingColumn.innerHTML = '';
    cookingColumn.innerHTML = '';
    readyColumn.innerHTML = '';

    let pendingCount = 0, cookingCount = 0, readyCount = 0;

    let orders = [];
    // if ordersData passed (from AJAX), use it; otherwise, use server-rendered list
    if (ordersDataArg && Array.isArray(ordersDataArg)) {
        orders = ordersDataArg;
    } else if (typeof ordersData !== 'undefined' && Array.isArray(ordersData)) {
        orders = ordersData;
    } else {
        const ordersJson = document.getElementById('orders-json');
        if (ordersJson) {
            orders = JSON.parse(ordersJson.textContent);
        }
    }

    orders.forEach(order => {
        // Normalize status from server to be safe (trim + lower)
        const status = (order.status || '').toString().trim().toLowerCase();
        const card = createOrderCard(order);

        if (status === 'pending') {
            pendingColumn.appendChild(card);
            pendingCount++;
        } else if (status === 'cooking' || status === 'preparing' || status === 'confirmed') {
            cookingColumn.appendChild(card);
            cookingCount++;
        } else if (status === 'completed' || status === 'ready' || status === 'ready_to_pickup') {
            readyColumn.appendChild(card);
            readyCount++;
        } else {
            pendingColumn.appendChild(card);
            pendingCount++;
        }
    });

    // Update badges
    document.getElementById('pendingBadge').textContent = pendingCount;
    document.getElementById('cookingBadge').textContent = cookingCount;
    document.getElementById('readyBadge').textContent = readyCount;
    document.getElementById('pendingCount').textContent = pendingCount;
    document.getElementById('cookingCount').textContent = cookingCount;
    document.getElementById('readyCount').textContent = readyCount;
}

function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card draggable hover-lift';
    card.draggable = true;
    card.setAttribute('role', 'article');
    card.setAttribute('aria-label', `Order ${order.order_id} - ${order.type}`);
    card.dataset.orderId = order.id;
    card.style.cursor = 'move';

    const normalized = (order.status || '').toString().trim().toLowerCase();
    const statusColor = {
        'pending': '#FFB74D',
        'cooking': '#FF9800',
        'preparing': '#FF9800',
        'confirmed': '#FF9800',
        'completed': '#81C784',
        'ready': '#81C784'
    }[normalized] || '#CCCCCC';

    card.innerHTML = `
        <div class="order-card-header">
            <div class="order-id" style="color: ${statusColor};">#${order.order_id}</div>
            <div class="order-type text-muted">${order.type}</div>
        </div>
        <div class="order-card-body">
            <div class="order-amount-row">
                <span>Order Total:</span>
                <span class="order-amount">Rs.${order.amount}</span>
            </div>
            <div class="order-items-row">
                <span>Items:</span> <strong>${order.items}</strong>
            </div>
            <a href="/restaurant/order_details/${order.order_id}/"
               class="btn btn-primary btn-sm w-100 mt-2" aria-label="View details for order ${order.order_id}">View Details</a>
        </div>
    `;

    return card;
}

document.addEventListener('DOMContentLoaded', () => {
    initializeKitchenBoard();
});

// Auto-refresh every 5 seconds: fetch latest orders and re-render board
function refreshKitchenBoard() {
    fetch('/restaurant/kitchen/orders/api/')
        .then(resp => {
            if (!resp.ok) throw new Error('Network response was not ok');
            return resp.json();
        })
        .then(data => {
            if (data && Array.isArray(data.orders)) {
                initializeKitchenBoard(data.orders);
            }
        })
        .catch(err => {
            console.error('Failed to refresh kitchen board:', err);
        });
}

setInterval(refreshKitchenBoard, 5000);
