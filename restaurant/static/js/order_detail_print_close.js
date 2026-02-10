// Print and Order Closing Functions

function openPrintPreview(type) {
    const modal = document.getElementById('print-modal');
    const template = document.getElementById(`${type}Template`);
    const preview = document.getElementById('print-preview');
    const previewTitle = document.getElementById('previewTitle');
    
    if (!modal || !preview || !template) return;
    
    // Update title
    if (previewTitle) {
        previewTitle.textContent = type === 'kot' ? 'KOT Preview' : 'Bill Preview';
    }
    
    // Copy template content to preview
    preview.innerHTML = template.innerHTML;
    
    // Show modal
    modal.style.display = 'flex';
}

function closePreview() {
    const modal = document.getElementById('print-modal');
    if (!modal) return;
    modal.style.display = 'none';
}

function printDocument() {
    window.print();
}

function downloadPDF() {
    const content = document.querySelector('#print-preview').innerHTML;
    const style = Array.from(document.querySelectorAll('style')).map(s => s.innerHTML).join('\n');
    const html = `
        <html>
            <head>
                <style>
                    ${style}
                    body { width: 80mm; margin: 0; padding: 0; }
                </style>
            </head>
            <body>
                ${content}
            </body>
        </html>
    `;
    const blob = new Blob([html], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'order-document.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

document.addEventListener('click', function (e) {
    const modal = document.getElementById('cancel-modal');
    if (!modal || modal.style.display === 'none' || modal.classList.contains('d-none')) return;
    if (e.target === modal) closeCancelModal();
});

function openCancelModal() {
    const modal = document.getElementById('cancel-modal');
    if (!modal) return;
    modal.style.display = 'flex';
}

function closeCancelModal() {
    const modal = document.getElementById('cancel-modal');
    if (!modal) return;
    modal.style.display = 'none';
}

function closeOrderConfirm() {
    const totalAmount = document.getElementById('canonical-total');
    if (!totalAmount) return;
    
    const total = parseFloat(totalAmount.dataset.total || totalAmount.textContent.replace(/[^0-9.-]/g, '')) || 0;
    
    let settledAmount = 0;
    const paymentElements = document.querySelectorAll('.payment-amount');
    paymentElements.forEach((element) => {
        const text = element.textContent || element.innerText || '';
        const cleanedText = text.replace(/Rs\.?\s*/g, '').trim();
        const amount = parseFloat(cleanedText) || 0;
        settledAmount += amount;
    });
    
    const remaining = total - settledAmount;
    
    if (remaining > 0) {
        // Show Bootstrap payment error modal instead of alert
        const errorModal = document.getElementById('payment-error-modal');
        if (errorModal) {
            const msgDiv = document.getElementById('payment-error-message');
            if (msgDiv) {
                msgDiv.innerHTML = `<p style="margin: 0; font-size: 0.95rem;"><strong>Remaining Amount:</strong> Rs.${remaining.toFixed(2)}</p>`;
            }
            errorModal.style.display = 'flex';
        }
        return;
    }
    
    // Show Bootstrap close order modal for confirmation
    const closeModal = document.getElementById('close-order-modal');
    if (closeModal) {
        const msgDiv = document.getElementById('close-order-message');
        if (msgDiv) {
            msgDiv.innerHTML = `
                <div class="order-info mb-3">
                    <p class="mb-2"><strong>Order ID:</strong> #${orderId}</p>
                    <p class="mb-2"><strong>Total Amount:</strong> Rs.${total.toFixed(2)}</p>
                    <p class="mb-0"><strong>Settled Amount:</strong> Rs.${settledAmount.toFixed(2)}</p>
                </div>
                <div class="alert alert-info small mb-0">
                    <i class="fas fa-info-circle me-2"></i>This action will move the order to completed status.
                </div>
            `;
        }
        closeModal.style.display = 'flex';
    }
}

function confirmCloseOrder() {
    if (document.getElementById('close-order-modal')) {
        document.getElementById('close-order-modal').style.display = 'none';
    }
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = CLOSE_ORDER_URL;
    
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrf_token;
    form.appendChild(csrfInput);
    
    document.body.appendChild(form);
    form.submit();
}

function closeCloseOrderModal() {
    const modal = document.getElementById('close-order-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}
