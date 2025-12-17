// Remaining Amount Calculation and Payment Form Handling

function parseAmount(text) {
    if (!text) return 0;
    const cleaned = String(text).replace(/[^\d.]/g, '');
    console.log('parseAmount input:', JSON.stringify(text), 'cleaned:', JSON.stringify(cleaned));
    const n = parseFloat(cleaned);
    console.log('parseFloat result:', n);
    return isNaN(n) ? 0 : n;
}

function updateRemaining() {
    const totalEl = document.getElementById('canonical-total');
    if (!totalEl) return;
    
    let total = parseFloat(totalEl.dataset.total);
    if (isNaN(total)) {
        total = parseAmount(totalEl.textContent);
    }

    let settled = 0;
    const paymentEls = Array.from(document.querySelectorAll('.payment-amount'));
    console.log('Found payment elements:', paymentEls.length);
    
    paymentEls.forEach(function(el) {
        let amt = parseFloat(el.dataset.amount);
        if (isNaN(amt)) {
            amt = parseAmount(el.textContent);
        }
        console.log('Payment amount:', el.dataset.amount, '=>', amt);
        settled += amt;
    });

    console.log('Total:', total, 'Settled:', settled);
    const remaining = Math.max(0, total - settled);
    const remEl = document.getElementById('remaining-amount');
    if (remEl) remEl.textContent = 'Rs. ' + remaining.toFixed(2);

    try {
        const hdrs = document.querySelectorAll('.section-header h3');
        hdrs.forEach(function(h) {
            const txt = h.textContent || '';
            if (txt.trim().startsWith('Settled Payments')) {
                const base = txt.split('(')[0].trim();
                const newTxt = `${base} (${paymentEls.length})`;
                h.textContent = newTxt;
            }
        });
    } catch (e) { }
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        // convert created_at to local timezone
        document.querySelectorAll('.js-created-at').forEach(function(el) {
            const iso = el.dataset.utc;
            if (iso) {
                const d = new Date(iso);
                el.textContent = d.toLocaleString();
            }
        });

        // initialize remaining display
        updateRemaining();

        // Handle add-payment form via AJAX to update remaining live
        const addForm = document.getElementById('add-payment-form');
        if (addForm) {
            addForm.addEventListener('submit', function(evt) {
                evt.preventDefault();
                const formData = new FormData(addForm);
                const action = addForm.getAttribute('action');
                const addPaymentCsrfToken = (function() {
                    const m = document.cookie.match('(^|;)\\s*' + 'csrftoken' + '\\s*=\\s*([^;]+)');
                    return m ? decodeURIComponent(m.pop()) : null;
                })();
                fetch(action, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': addPaymentCsrfToken || ''
                    },
                    body: formData,
                })
                .then(resp => resp.json())
                .then(data => {
                    console.log('Add payment response', data);
                    if (data.status === 'success') {
                        let paymentsContainer = document.getElementById('settled-payments');
                        const method = formData.get('payment_method') || '';
                        const amount = parseAmount(formData.get('amount')) || 0;
                        const tx = formData.get('transaction_id') || '';

                        if (!paymentsContainer) {
                            const cards = document.querySelectorAll('.card');
                            for (const c of cards) {
                                const hdr = c.querySelector('.section-header h3');
                                if (hdr && hdr.textContent && hdr.textContent.trim().includes('Settled Payments')) {
                                    const content = c.querySelector('.card-content');
                                    if (content) {
                                        const p = content.querySelector('p');
                                        if (p) p.remove();
                                        const container = document.createElement('div');
                                        container.id = 'settled-payments';
                                        content.appendChild(container);
                                        paymentsContainer = container;
                                    }
                                    break;
                                }
                            }
                        }

                        const item = document.createElement('div');
                        item.className = 'payment-item';
                        item.innerHTML = `<div style="display:flex;align-items:center;gap:1rem;">
                            <div class="payment-info"><h5>${method.charAt(0).toUpperCase() + method.slice(1)}</h5>${tx ? ('<p>ID: ' + tx + '</p>') : ''}</div>
                            <div class="payment-amount" data-amount="${amount.toFixed(2)}">Rs. ${amount.toFixed(2)}</div>
                        </div>`;

                        if (paymentsContainer) {
                            paymentsContainer.appendChild(item);
                        }

                        addForm.querySelector('input[name="amount"]').value = '';

                        if (data.remaining_amount !== undefined && data.remaining_amount !== null) {
                            const remEl = document.getElementById('remaining-amount');
                            if (remEl) remEl.textContent = 'Rs. ' + parseFloat(data.remaining_amount).toFixed(2);
                        } else {
                            updateRemaining();
                        }
                    } else {
                        alert('Failed to add payment: ' + (data.message || JSON.stringify(data.errors || data)));
                    }
                })
                .catch(err => {
                    console.error('Add payment failed', err);
                    alert('Failed to add payment. See console.');
                });
            });
        }

        // If payments are edited/deleted via existing handlers, they should call updateRemaining()
        window.updateRemaining = updateRemaining;

    } catch (e) { console.error(e); }
});
