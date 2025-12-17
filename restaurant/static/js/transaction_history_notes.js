// Notes form AJAX submit (CSRF-safe)
(function() {
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

    const notesForm = document.getElementById('modal-notes-form');
    if (!notesForm) return;
    const notesInput = document.getElementById('modal-notes-input');
    const notesError = document.getElementById('modal-notes-error');
    const notesSuccess = document.getElementById('modal-notes-success');

    notesForm.addEventListener('submit', function(e) {
        e.preventDefault();
        notesError.style.display = 'none';
        notesSuccess.style.display = 'none';
        const notes = (notesInput.value || '').trim();
        if (!notes) {
            notesError.style.display = '';
            return;
        }
        const orderId = notesForm.dataset.orderId;
        if (!orderId) {
            notesError.textContent = 'Missing order id';
            notesError.style.display = '';
            return;
        }

        const ORDER_UPDATE_URL_TEMPLATE = "{% url 'restaurant:order_update_notes' 'ORDER_ID_PLACEHOLDER' %}";
        const url = ORDER_UPDATE_URL_TEMPLATE.replace('ORDER_ID_PLACEHOLDER', encodeURIComponent(orderId));
        const csrftoken = getCookie('csrftoken');

        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                notes: notes
            })
        }).then(r => r.json())
            .then(j => {
                if (j && j.success) {
                    notesSuccess.style.display = '';
                    // update displayed notes
                    const displayed = document.getElementById('modal-special-notes');
                    if (displayed) displayed.textContent = notes;
                    setTimeout(() => {
                        notesSuccess.style.display = 'none';
                    }, 1500);
                } else {
                    notesError.textContent = (j && j.error) ? j.error : 'Failed to save';
                    notesError.style.display = '';
                }
            }).catch(err => {
                notesError.textContent = 'Network error';
                notesError.style.display = '';
                console.error(err);
            });
    });
})();
