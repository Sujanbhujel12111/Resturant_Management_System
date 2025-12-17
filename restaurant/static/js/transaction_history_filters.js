// Filter controls: update query params and reload (debounced for search)
(function() {
    function getInput(id) {
        return document.getElementById(id);
    }

    const searchInput = getInput('search-input');
    const orderType = getInput('order-type');
    const statusFilter = getInput('status-filter');
    const entriesSelect = getInput('entries-select');
    const startDate = getInput('start-date');
    const endDate = getInput('end-date');

    let _searchTimer = null;
    const debounceSearch = (fn, delay = 400) => {
        return function() {
            clearTimeout(_searchTimer);
            _searchTimer = setTimeout(fn, delay);
        };
    };

    function applyFilters() {
        const params = new URLSearchParams(window.location.search);
        const q = searchInput ? searchInput.value.trim() : '';
        const type = orderType ? orderType.value : '';
        const status = statusFilter ? statusFilter.value : '';
        const entries = entriesSelect ? entriesSelect.value : '';
        const sd = startDate ? startDate.value : '';
        const ed = endDate ? endDate.value : '';

        if (q) params.set('q', q);
        else params.delete('q');
        if (type) params.set('order_type', type);
        else params.delete('order_type');
        if (status) params.set('status', status);
        else params.delete('status');
        if (entries) params.set('entries', entries);
        else params.delete('entries');
        if (sd) params.set('start_date', sd);
        else params.delete('start_date');
        if (ed) params.set('end_date', ed);
        else params.delete('end_date');
        params.delete('page');

        const base = window.location.pathname;
        const qs = params.toString();
        window.location.href = base + (qs ? ('?' + qs) : '');
    }

    if (searchInput) searchInput.addEventListener('input', debounceSearch(applyFilters, 500));
    if (orderType) orderType.addEventListener('change', applyFilters);
    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
    if (entriesSelect) entriesSelect.addEventListener('change', applyFilters);
    if (startDate) startDate.addEventListener('change', applyFilters);
    if (endDate) endDate.addEventListener('change', applyFilters);
})();
