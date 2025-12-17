// Modal accessibility helper: open/close modal, trap focus, apply inert to background
(function() {
    const modal = document.getElementById('order-details-modal');
    if (!modal) return;
    
    const dialog = modal.querySelector('.modal-dialog');
    const closeBtn = document.getElementById('modal-close-btn');
    let _lastActive = null;

    function setBackgroundInert(m, inert) {
        try {
            const skip = ['SCRIPT', 'STYLE', 'LINK', 'META', 'TEMPLATE'];
            Array.from(document.body.children).forEach(el => {
                if (el === m) return;
                if (skip.includes(el.tagName)) return;
                if (inert) {
                    if (el.hasAttribute('aria-hidden')) el.dataset._prevAriah = el.getAttribute('aria-hidden');
                    el.setAttribute('inert', '');
                    el.setAttribute('aria-hidden', 'true');
                } else {
                    el.removeAttribute('inert');
                    if (el.dataset && typeof el.dataset._prevAriah !== 'undefined') {
                        el.setAttribute('aria-hidden', el.dataset._prevAriah);
                        delete el.dataset._prevAriah;
                    } else {
                        el.removeAttribute('aria-hidden');
                    }
                }
            });
        } catch (e) {
            /* non-fatal */
        }
    }

    function trapHandler(e) {
        if (e.key === 'Escape') {
            closeModal();
            return;
        }
        if (e.key !== 'Tab') return;
        const focusables = Array.from(modal.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])'));
        if (!focusables.length) {
            e.preventDefault();
            return;
        }
        const idx = focusables.indexOf(document.activeElement);
        if (e.shiftKey) {
            if (idx <= 0) {
                focusables[focusables.length - 1].focus();
                e.preventDefault();
            }
        } else {
            if (idx === focusables.length - 1 || idx === -1) {
                focusables[0].focus();
                e.preventDefault();
            }
        }
    }

    function openModal() {
        _lastActive = document.activeElement;
        if (modal.parentNode !== document.body) document.body.appendChild(modal);
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        setBackgroundInert(modal, true);
        try {
            document.body.style.overflow = 'hidden';
        } catch (e) {}
        document.addEventListener('keydown', trapHandler);
        // focus first focusable (close button)
        setTimeout(() => {
            try {
                closeBtn && closeBtn.focus();
            } catch (e) {}
        }, 10);
    }

    function closeModal() {
        document.removeEventListener('keydown', trapHandler);
        try {
            if (_lastActive && typeof _lastActive.focus === 'function') _lastActive.focus();
        } catch (e) {}
        setBackgroundInert(modal, false);
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');
        try {
            document.body.style.overflow = '';
        } catch (e) {}
    }

    // Make functions globally available
    window.openModal = openModal;
    window.closeModal = closeModal;

    // Delegated click: open when any .order-details-btn clicked
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.order-details-btn');
        if (!btn) return;
        e.preventDefault();
        const url = btn.getAttribute('data-order-url');
        // capture the visible Type text from the table row as a fallback
        const sourceRow = btn.closest('tr');
        const sourceTypeText = (sourceRow && sourceRow.querySelector('td:nth-child(3)')) ? (sourceRow.querySelector('td:nth-child(3)').textContent || '').trim() : '';
        if (!url) {
            openModal();
            return;
        }
        // show modal with skeleton/spinner while loading
        const spinner = document.getElementById('modal-spinner');
        const skeleton = document.getElementById('modal-skeleton');
        const content = document.getElementById('modal-content');
        if (spinner) spinner.classList.add('show');
        if (skeleton) skeleton.classList.add('show');
        if (content) content.style.display = 'none';

        openModal();

        fetch(url, {
            credentials: 'same-origin'
        })
            .then(resp => {
                if (!resp.ok) throw new Error('Failed to load');
                return resp.json();
            })
            .then(data => {
                // populate fields
                try {
                    document.getElementById('modal-order-id').textContent = data.order_id || '';
                    document.getElementById('modal-customer-name').textContent = data.customer_name || '';
                    document.getElementById('modal-customer-phone').textContent = data.customer_phone || '';
                    // order type / table
                    const ot = (data.order_type || '').toString();
                    let otText = ot || '';
                    if (data.table && data.table.number) otText = 'table #' + data.table.number;
                    // fallback to the visible table row Type text if response didn't include table info
                    if (!otText && sourceTypeText) otText = sourceTypeText;
                    if (ot === 'takeaway') otText = 'Takeaway';
                    if (ot === 'delivery') otText = 'Delivery';
                    document.getElementById('modal-order-type').textContent = otText;
                    document.getElementById('modal-completed-by').textContent = data.completed_by || 'N/A';
                    document.getElementById('modal-total-amount').textContent = data.total_amount ? ('Rs.' + data.total_amount) : '';

                    // Handle delivery charge display
                    const deliveryChargeContainer = document.getElementById('modal-delivery-charge-container');
                    const deliveryChargeEl = document.getElementById('modal-delivery-charge');
                    const totalWithDeliveryContainer = document.getElementById('modal-total-with-delivery-container');
                    const totalWithDeliveryEl = document.getElementById('modal-total-with-delivery');

                    if (data.order_type === 'delivery' && data.delivery_charge > 0) {
                        deliveryChargeEl.textContent = 'Rs.' + data.delivery_charge;
                        deliveryChargeContainer.style.display = '';
                        totalWithDeliveryEl.textContent = 'Rs.' + data.total_with_delivery;
                        totalWithDeliveryContainer.style.display = '';
                    } else {
                        deliveryChargeContainer.style.display = 'none';
                        totalWithDeliveryContainer.style.display = 'none';
                    }

                    // cancellation reason
                    if (data.cancellation_reason) {
                        const ctr = document.getElementById('modal-cancellation-reason-container');
                        document.getElementById('modal-cancellation-reason').textContent = data.cancellation_reason;
                        if (ctr) ctr.style.display = '';
                    } else {
                        const ctr = document.getElementById('modal-cancellation-reason-container');
                        if (ctr) ctr.style.display = 'none';
                    }

                    // payments
                    const paymentsEl = document.getElementById('modal-payment-methods');
                    paymentsEl.innerHTML = '';
                    if (data.payments && data.payments.length) {
                        data.payments.forEach(p => {
                            const line = document.createElement('div');
                            line.textContent = (p.method ? p.method + ': ' : '') + (p.amount != null ? ('Rs.' + p.amount) : '');
                            paymentsEl.appendChild(line);
                        });
                    }

                    // items
                    const itemsEl = document.getElementById('modal-order-items');
                    itemsEl.innerHTML = '';
                    if (data.items && data.items.length) {
                        data.items.forEach(it => {
                            const row = document.createElement('div');
                            row.className = 'item-row';
                            row.innerHTML = '<div class="item-name">' + (it.item_name || '') + '</div>' +
                                '<div class="item-qty">Qty: ' + (it.quantity || '') + '</div>' +
                                '<div class="item-price">Rs.' + (it.price || '') + '</div>' +
                                '<div class="item-total">Rs.' + ((it.total != null) ? it.total : '') + '</div>';
                            itemsEl.appendChild(row);
                        });
                    }

                    // notes, dates
                    document.getElementById('modal-special-notes').textContent = data.special_notes || '';
                    const created = document.getElementById('modal-created-date');
                    const completed = document.getElementById('modal-completed-date');
                    created.textContent = data.created_at ? new Date(data.created_at).toLocaleString() : '';
                    completed.textContent = data.updated_at ? new Date(data.updated_at).toLocaleString() : '';

                    // Render status logs (if provided)
                    const statusLogsEl = document.getElementById('modal-status-logs');
                    if (statusLogsEl) {
                        statusLogsEl.innerHTML = '';
                        if (data.status_logs && data.status_logs.length) {
                            data.status_logs.forEach(sl => {
                                const div = document.createElement('div');
                                const who = sl.changed_by || 'System';
                                const prev = sl.previous_status || '-';
                                const nw = sl.new_status || '';
                                const ts = sl.timestamp ? new Date(sl.timestamp).toLocaleString() : '';
                                div.textContent = `${prev} → ${nw} by ${who} @ ${ts}`;
                                statusLogsEl.appendChild(div);
                            });
                        } else {
                            statusLogsEl.textContent = 'No status history available';
                        }
                    }

                    // set notes form target (store current order id/url)
                    const notesForm = document.getElementById('modal-notes-form');
                    notesForm.dataset.orderId = data.order_id;

                    // set revert form target (store current order id)
                    const revertForm = document.getElementById('modal-revert-form');
                    if (revertForm) revertForm.dataset.orderId = data.order_id;

                } catch (e) {
                    console.error('Error populating modal', e);
                }
            })
            .catch(err => {
                console.error('Failed to load order details', err);
                const errEl = document.getElementById('modal-error');
                if (errEl) {
                    errEl.textContent = 'Failed to load order details. Please try again.';
                    errEl.style.display = '';
                }
            })
            .finally(() => {
                if (spinner) spinner.classList.remove('show');
                if (skeleton) skeleton.classList.remove('show');
                if (content) content.style.display = '';
            });
    });

    // overlay click closes if clicked outside dialog
    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeModal();
    });

    if (closeBtn) closeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        closeModal();
    });
})();
