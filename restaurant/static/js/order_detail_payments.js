// Payment Management Functions
// Note: csrf_token, orderId, orderPk, PAYMENT_EDIT_URL_TEMPLATE, PAYMENT_DELETE_URL_TEMPLATE
// are declared in the template to avoid duplicate declarations

function addPaymentForm() {
    const paymentForms = document.getElementById('payment-forms');
    const newPaymentForm = document.createElement('div');
    newPaymentForm.classList.add('payment-form', 'mt-2');
    newPaymentForm.innerHTML = `
        <select name="payment_method" class="py-2 px-3 border rounded">
            {% for method in payment_methods %}
                <option value="{{ method.0 }}">{{ method.1 }}</option>
            {% endfor %}
        </select>
        <input type="number" name="amount" step="0.01" class="py-2 px-3 border rounded ml-2" 
               placeholder="Amount" oninput="updateRemainingAmount()">
        <input type="text" name="transaction_id" class="py-2 px-3 border rounded ml-2" 
               placeholder="Transaction ID (optional)">
    `;
    if (paymentForms) paymentForms.appendChild(newPaymentForm);
}

function editPayment(id) {
    const paymentItem = document.getElementById(`payment-${id}`);
    if (!paymentItem) return;
    const paymentMethod = paymentItem.querySelector('.payment-method') ? paymentItem.querySelector('.payment-method').innerText : '';
    const amountEl = paymentItem.querySelector('.payment-amount');
    const amount = amountEl ? amountEl.innerText.replace(/Rs\.?\s*/g, '') : '';
    const transactionEl = paymentItem.querySelector('.payment-transaction-id');
    const transactionId = transactionEl ? transactionEl.innerText : '';

    if (paymentItem.querySelector('.payment-method')) {
        // Build dropdown with payment method choices
        let optionsHTML = '';
        if (typeof PAYMENT_METHOD_CHOICES !== 'undefined') {
            PAYMENT_METHOD_CHOICES.forEach(method => {
                optionsHTML += `<option value="${method[0]}">${method[1]}</option>`;
            });
        }
        paymentItem.querySelector('.payment-method').innerHTML = `
            <select class="py-2 px-3 border rounded">
                ${optionsHTML}
            </select>
        `;
        try {
            const sel = paymentItem.querySelector('.payment-method select');
            if (sel) sel.value = paymentMethod;
        } catch (e) { }
    }
    if (amountEl) {
        const numericAmount = String(amount).replace(/[^0-9.\-\.]/g, '') || '';
        amountEl.innerHTML = `<input type="number" value="${numericAmount}" class="py-2 px-3 border rounded">`;
    }
    if (transactionEl) {
        transactionEl.innerHTML = `<input type="text" value="${transactionId}" class="py-2 px-3 border rounded">`;
    }

    const primaryBtn = paymentItem.querySelector('.text-primary');
    const successBtn = paymentItem.querySelector('.text-success');
    if (primaryBtn) primaryBtn.classList.add('d-none');
    if (successBtn) successBtn.classList.remove('d-none');
}

function savePayment(id) {
    const paymentItem = document.getElementById(`payment-${id}`);
    if (!paymentItem) return;
    const pmSelect = paymentItem.querySelector('.payment-method select');
    const paymentMethod = pmSelect ? pmSelect.value : '';
    const amountInput = paymentItem.querySelector('.payment-amount input');
    const amount = amountInput ? amountInput.value : '';
    const txInput = paymentItem.querySelector('.payment-transaction-id input');
    const transactionId = txInput ? txInput.value : '';

    const csrftoken = (function () {
        const m = document.cookie.match('(^|;)\\s*' + 'csrftoken' + '\\s*=\\s*([^;]+)');
        return m ? decodeURIComponent(m.pop()) : null;
    })();

    const editUrl = PAYMENT_EDIT_URL_TEMPLATE.replace('/0/', '/' + id + '/');
    console.log('Edit payment posting to', editUrl, { payment_method: paymentMethod, amount: amount, transaction_id: transactionId });
    fetch(editUrl, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || ''
        },
        body: JSON.stringify({
            payment_method: paymentMethod,
            amount: amount,
            transaction_id: transactionId
        }),
    }).then(response => response.json())
        .then(data => {
            if (data && data.status === 'success') {
                if (paymentItem.querySelector('.payment-method')) paymentItem.querySelector('.payment-method').innerText = paymentMethod;
                const amountEl = paymentItem.querySelector('.payment-amount');
                if (amountEl) {
                    const formattedAmount = parseFloat(amount).toFixed(2);
                    amountEl.setAttribute('data-amount', formattedAmount);
                    amountEl.innerText = `Rs. ${formattedAmount}`;
                }
                if (paymentItem.querySelector('.payment-transaction-id')) paymentItem.querySelector('.payment-transaction-id').innerText = transactionId;

                const primaryBtn = paymentItem.querySelector('.text-primary');
                const successBtn = paymentItem.querySelector('.text-success');
                if (primaryBtn) primaryBtn.classList.remove('d-none');
                if (successBtn) successBtn.classList.add('d-none');

                if (window.updateRemaining) window.updateRemaining();
            } else {
                console.error('Edit payment failed', data);
                alert('Failed to save payment edits');
            }
        }).catch(err => { console.error('Edit payment error', err); alert('Failed to save payment edits'); });
}

function deletePayment(id) {
    if (!confirm('Are you sure you want to delete this payment?')) {
        return;
    }
    const csrftoken2 = (function () {
        const m = document.cookie.match('(^|;)\\s*' + 'csrftoken' + '\\s*=\\s*([^;]+)');
        return m ? decodeURIComponent(m.pop()) : null;
    })();
    const deleteUrl = PAYMENT_DELETE_URL_TEMPLATE.replace('/0/', '/' + id + '/');
    fetch(deleteUrl, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken2 || ''
        },
    }).then(response => response.json())
        .then(data => {
            if (data && data.status === 'success') {
                const paymentItem = document.getElementById(`payment-${id}`);
                if (paymentItem) paymentItem.remove();
                if (window.updateRemaining) window.updateRemaining();
            } else {
                console.error('Delete payment failed', data);
                alert('Failed to delete payment');
            }
        }).catch(err => { console.error('Delete payment error', err); alert('Failed to delete payment'); });
}
