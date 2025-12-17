// Menu Template JavaScript - Search and Filtering

/**
 * Filter menu items based on search term
 * Hides categories and items that don't match
 */
function filterMenu() {
    const searchTerm = document.getElementById('menuSearch').value.toLowerCase();
    document.querySelectorAll('.category-section').forEach(section => {
        const items = section.querySelectorAll('.menu-card');
        let visibleCount = 0;

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm) || searchTerm === '') {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        // Hide entire section if no items match
        section.style.display = visibleCount > 0 ? '' : 'none';
    });
}

/**
 * Initialize menu animations on page load
 */
function initializeMenuAnimations() {
    document.querySelectorAll('.menu-card').forEach((card, index) => {
        card.style.animation = `slideUp 0.5s ease forwards`;
        card.style.animationDelay = `${index * 0.05}s`;
        card.style.opacity = '0';
    });
}

/**
 * Setup event listeners for menu interactions
 */
function setupMenuListeners() {
    // Real-time search
    const searchInput = document.getElementById('menuSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', filterMenu);
    }

    // Search button click
    const searchBtn = document.querySelector('.menu-search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', filterMenu);
    }

    // Add to order buttons
    document.querySelectorAll('.menu-card-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.classList.contains('disabled') || this.hasAttribute('disabled')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Clear search and reset view
 */
function clearMenuSearch() {
    const searchInput = document.getElementById('menuSearch');
    if (searchInput) {
        searchInput.value = '';
        filterMenu();
    }
}

/**
 * Handle category filtering
 * @param {string} categoryName - Category to filter by, or 'all' to show all
 */
function filterByCategory(categoryName) {
    document.querySelectorAll('.category-section').forEach(section => {
        const categoryTitle = section.querySelector('.category-title h2');
        const categoryText = categoryTitle ? categoryTitle.textContent.trim() : '';
        
        if (categoryName === 'all' || categoryText === categoryName) {
            section.style.display = '';
        } else {
            section.style.display = 'none';
        }
    });
}

/**
 * Initialize the menu on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    initializeMenuAnimations();
    setupMenuListeners();
});
