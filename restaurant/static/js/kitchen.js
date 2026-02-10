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

// Make columns droppable and handle drops
function setupDragDrop() {
    const columns = document.querySelectorAll('.kitchen-column-list');
    columns.forEach(col => {
        col.addEventListener('dragover', (e) => {
            e.preventDefault();
            col.classList.add('drag-over');
        });

        col.addEventListener('dragleave', () => {
            col.classList.remove('drag-over');
        });

        col.addEventListener('drop', (e) => {
            e.preventDefault();
            col.classList.remove('drag-over');
            try {
                const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                const dragged = document.querySelector(`[data-order-id="${data.id}"]`);
                if (dragged) {
                    // remember previous parent so we can revert if server rejects
                    const prevParent = dragged.parentElement;
                    // append locally (optimistic)
                    col.appendChild(dragged);
                    dragged.classList.remove('dragging');

                    // determine new status from column id
                    let newStatus = 'pending';
                    if (col.id === 'cooking-column') newStatus = 'preparing';
                    if (col.id === 'ready-column') newStatus = 'ready';

                    // optimistically update badges
                    updateCounts();

                    // persist change via AJAX and revert if server rejects
                    persistOrderStatus(data.id, newStatus).then(res => {
                        if (res && res.success) {
                            if (res.status === 'ready' || res.status === 'completed' || (res.status || '').includes('ready')) {
                                playKitchenChime();
                                showKitchenAlert(`Order #${data.order_id} marked ${res.status}`);
                                flashColumn('ready-column');
                            }
                        } else {
                            // revert optimistic move
                            if (prevParent) prevParent.appendChild(dragged);
                            updateCounts();
                            showKitchenAlert((res && res.message) ? res.message : 'Failed to update order status');
                        }
                    }).catch(err => {
                        console.warn('Failed to persist status change', err);
                        if (prevParent) prevParent.appendChild(dragged);
                        updateCounts();
                        showKitchenAlert('Network error while updating order');
                    });
                }
            } catch (err) {
                console.error('Invalid drag data', err);
            }
        });
    });
}

function updateCounts() {
    const pending = document.getElementById('pending-column').children.length;
    const cooking = document.getElementById('cooking-column').children.length;
    const ready = document.getElementById('ready-column').children.length;
    document.getElementById('pendingBadge').textContent = pending;
    document.getElementById('cookingBadge').textContent = cooking;
    document.getElementById('readyBadge').textContent = ready;
    document.getElementById('pendingCount').textContent = pending;
    document.getElementById('cookingCount').textContent = cooking;
    document.getElementById('readyCount').textContent = ready;
}

async function persistOrderStatus(orderPk, status) {
    const url = '/kitchen/ajax/update_order_status/';
    const csrftoken = getCookie('csrftoken');
    try {
        const resp = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ order_id: orderPk, status: status })
        });
        let data = null;
        try { data = await resp.json(); } catch (e) { data = null; }
        if (!resp.ok) return data || { success: false, message: 'Network error', status: null };
        return data;
    } catch (e) {
        return { success: false, message: 'Network error', status: null };
    }
}

/* --- Alert helpers --- */
// Small chime using Web Audio API
function playKitchenChime() {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const ctx = new AudioContext();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = 'sine';
        o.frequency.setValueAtTime(880, ctx.currentTime);
        g.gain.setValueAtTime(0.0001, ctx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.01);
        o.connect(g);
        g.connect(ctx.destination);
        o.start();
        o.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.12);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.3);
        setTimeout(() => { try { o.stop(); ctx.close(); } catch (e) {} }, 350);
    } catch (e) { console.warn('Audio not available', e); }
}

function showKitchenAlert(message) {
    try {
        if (typeof Toast !== 'undefined' && Toast.success) {
            Toast.info(message);
        } else {
            // fallback: small floating element
            const div = document.createElement('div');
            div.textContent = message;
            div.style.position = 'fixed';
            div.style.right = '1rem';
            div.style.bottom = '1rem';
            div.style.background = 'rgba(12,84,96,0.95)';
            div.style.color = 'white';
            div.style.padding = '0.5rem 0.75rem';
            div.style.borderRadius = '6px';
            div.style.zIndex = 12000;
            document.body.appendChild(div);
            setTimeout(() => div.remove(), 4000);
        }
    } catch (e) { console.warn('Failed to show alert', e); }
}

function flashColumn(columnId) {
    try {
        const el = document.getElementById(columnId);
        if (!el) return;
        el.classList.add('alert-flash');
        setTimeout(() => el.classList.remove('alert-flash'), 1800);
    } catch (e) { console.warn(e); }
}

/* --- Change detection for polling updates --- */
let lastOrdersMap = new Map();
let _kitchen_initial_load = true;

function detectChangesAndAlert(orders) {
    if (_kitchen_initial_load) {
        // seed the map, don't alert on first load
        lastOrdersMap.clear();
        orders.forEach(o => lastOrdersMap.set(Number(o.id), (o.status || '').toString().toLowerCase()));
        _kitchen_initial_load = false;
        return;
    }

    // Compare and find new orders or status->ready
    orders.forEach(o => {
        const id = Number(o.id);
        const status = (o.status || '').toString().toLowerCase();
        const prev = lastOrdersMap.get(id);
        if (typeof prev === 'undefined') {
            // new order
            playKitchenChime();
            showKitchenAlert(`New order: #${o.order_id}`);
            flashColumn('pending-column');
        } else if (prev !== status && status.includes('ready')) {
            // became ready
            playKitchenChime();
            showKitchenAlert(`Order ready: #${o.order_id}`);
            flashColumn('ready-column');
        }
    });

    // update map
    lastOrdersMap.clear();
    orders.forEach(o => lastOrdersMap.set(Number(o.id), (o.status || '').toString().toLowerCase()));
}

// Helper to get CSRF cookie when needed
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

// Change order status helper (used by buttons and keyboard shortcuts)
function changeOrderStatus(orderPk, status, cardEl) {
    // optimistic UI change: move card to column
    try {
        if (cardEl) {
            const prevParent = cardEl.parentElement;
            const targetCol = status === 'preparing' ? document.getElementById('cooking-column') : (status === 'ready' || status === 'completed' ? document.getElementById('ready-column') : document.getElementById('pending-column'));
            if (targetCol) targetCol.appendChild(cardEl);
            updateCounts();

            // persist and revert if necessary
            persistOrderStatus(orderPk, status).then(res => {
                if (!res || !res.success) {
                    // revert
                    if (prevParent) prevParent.appendChild(cardEl);
                    updateCounts();
                    showKitchenAlert((res && res.message) ? res.message : 'Server rejected status change');
                }
            }).catch(err => {
                if (prevParent) prevParent.appendChild(cardEl);
                updateCounts();
                showKitchenAlert('Network error while updating order');
            });
        }
    } catch (e) { console.warn(e); }
}

// Selection management and keyboard shortcuts
let selectedCard = null;
function toggleCardSelection(card) {
    if (selectedCard && selectedCard === card) {
        card.classList.remove('selected');
        selectedCard = null;
        return;
    }
    if (selectedCard) selectedCard.classList.remove('selected');
    card.classList.add('selected');
    selectedCard = card;
}

document.addEventListener('keydown', (e) => {
    // don't intercept when typing in inputs
    const active = document.activeElement;
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) return;

    if (!selectedCard) return;
    // Quick keys: S=start/preparing, R=ready, C=complete, ArrowLeft/Right to move between columns
    if (e.key.toLowerCase() === 's') {
        e.preventDefault();
        changeOrderStatus(selectedCard.dataset.orderId, 'preparing', selectedCard);
        return;
    }
    if (e.key.toLowerCase() === 'r') {
        e.preventDefault();
        changeOrderStatus(selectedCard.dataset.orderId, 'ready', selectedCard);
        return;
    }
    if (e.key.toLowerCase() === 'c') {
        e.preventDefault();
        changeOrderStatus(selectedCard.dataset.orderId, 'completed', selectedCard);
        return;
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault();
        // move card between columns visually
        const colOrder = ['pending-column', 'cooking-column', 'ready-column'];
        let parent = selectedCard.closest('.kitchen-column-list');
        let idx = colOrder.indexOf(parent.id);
        if (e.key === 'ArrowLeft') idx = Math.max(0, idx - 1); else idx = Math.min(colOrder.length - 1, idx + 1);
        const target = document.getElementById(colOrder[idx]);
        if (target) {
            const prevParent = selectedCard.parentElement;
            target.appendChild(selectedCard);
            updateCounts();
            // persist mapping and revert on failure
            const newStatus = idx === 0 ? 'pending' : (idx === 1 ? 'preparing' : 'ready');
            persistOrderStatus(selectedCard.dataset.orderId, newStatus).then(res => {
                if (!res || !res.success) {
                    if (prevParent) prevParent.appendChild(selectedCard);
                    updateCounts();
                    showKitchenAlert((res && res.message) ? res.message : 'Failed to update order status');
                }
            }).catch(() => {
                if (prevParent) prevParent.appendChild(selectedCard);
                updateCounts();
                showKitchenAlert('Network error while updating order');
            });
        }
    }
});

// Simple local prep timer increments (per-card) — increments MM:SS every second
function startLocalTimer(timerEl) {
    let seconds = 0;
    timerEl.textContent = '00:00';
    const id = setInterval(() => {
        seconds++;
        const mm = String(Math.floor(seconds/60)).padStart(2,'0');
        const ss = String(seconds%60).padStart(2,'0');
        timerEl.textContent = `${mm}:${ss}`;
        // stop if element removed
        if (!document.body.contains(timerEl)) clearInterval(id);
    }, 1000);
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
            <div class="order-card-actions">
                <button class="btn btn-sm btn-outline-primary quick-action-start" title="Start / Prepare">Start</button>
                <button class="btn btn-sm btn-outline-success quick-action-ready" title="Mark Ready">Ready</button>
                <button class="btn btn-sm btn-outline-secondary quick-action-complete" title="Complete">Complete</button>
            </div>
                <a href="/order_details/${order.order_id}/"
               class="btn btn-primary btn-sm w-100 mt-2" aria-label="View details for order ${order.order_id}">View Details</a>
        </div>
    `;

    // Attach drag event handlers
    card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', JSON.stringify({ id: order.id, order_id: order.order_id }));
        card.classList.add('dragging');
    });

    card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
    });

    // Selection handling for keyboard actions
    card.addEventListener('click', (e) => {
        // allow clicks on buttons to not toggle selection
        if (e.target.closest('.order-card-actions') || e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;
        toggleCardSelection(card);
    });

    // wire quick-action buttons
    const startBtn = card.querySelector('.quick-action-start');
    const readyBtn = card.querySelector('.quick-action-ready');
    const completeBtn = card.querySelector('.quick-action-complete');

    if (startBtn) startBtn.addEventListener('click', (ev) => { ev.stopPropagation(); changeOrderStatus(order.id, 'preparing', card); });
    if (readyBtn) readyBtn.addEventListener('click', (ev) => { ev.stopPropagation(); changeOrderStatus(order.id, 'ready', card); });
    if (completeBtn) completeBtn.addEventListener('click', (ev) => { ev.stopPropagation(); changeOrderStatus(order.id, 'completed', card); });

    // Add small prep timer placeholder if status is preparing
    if ((order.status || '').toLowerCase().includes('prepar')) {
        const timer = document.createElement('div');
        timer.className = 'prep-timer mt-2';
        timer.textContent = '00:00';
        card.querySelector('.order-card-body').insertBefore(timer, card.querySelector('.order-card-body').firstChild);
        startLocalTimer(timer);
    }

    return card;
}

document.addEventListener('DOMContentLoaded', () => {
    initializeKitchenBoard();
    setupDragDrop();
});

// Auto-refresh every 5 seconds: fetch latest orders and re-render board
function refreshKitchenBoard() {
    fetch('/kitchen/orders/api/')
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
