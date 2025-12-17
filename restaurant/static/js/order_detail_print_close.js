// Print and Order Closing Functions

function openPrintPreview(type) {
    const modal = document.getElementById('print-modal');
    const container = modal ? modal.querySelector('.preview-container') : null;
    const template = document.getElementById(`${type}Template`);
    const preview = document.getElementById('print-preview');
    if (!modal || !preview || !template) return;
    document.getElementById('previewTitle') ? document.getElementById('previewTitle').textContent = type === 'kot' ? 'KOT Preview' : 'Bill Preview' : null;
    preview.innerHTML = template.innerHTML;
    modal.classList.remove('d-none');
    modal.classList.add('active');
}

function closePreview() {
    const modal = document.getElementById('print-modal');
    if (!modal) return;
    modal.classList.add('d-none');
    modal.classList.remove('active');
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
        alert(`Cannot close order. Payment not fully settled.\n\nRemaining Amount: Rs.${remaining.toFixed(2)}\n\nPlease collect the remaining payment first.`);
        return;
    }
    
    if (confirm(`Close Order #${orderId}?\n\nTotal Amount: Rs.${total.toFixed(2)}\nSettled Amount: Rs.${settledAmount.toFixed(2)}\n\nThis action will move the order to completed status.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = CLOSE_ORDER_URL;  // Use the variable defined in template, not Django template tag
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrf_token;
        form.appendChild(csrfInput);
        
        document.body.appendChild(form);
        form.submit();
    }
}
