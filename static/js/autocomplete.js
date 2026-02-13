// Autocomplete search functionality
let searchTimeout;
const autocompleteContainer = document.getElementById('autocomplete-suggestions');
const searchInput = document.getElementById('search-input');

if (searchInput && autocompleteContainer) {
    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            autocompleteContainer.innerHTML = '';
            autocompleteContainer.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch(`/api/autocomplete/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.suggestions && data.suggestions.length > 0) {
                        displaySuggestions(data.suggestions);
                    } else {
                        autocompleteContainer.innerHTML = '<div class="autocomplete-item">No results found</div>';
                        autocompleteContainer.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Autocomplete error:', error);
                });
        }, 300); // Debounce 300ms
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !autocompleteContainer.contains(e.target)) {
            autocompleteContainer.style.display = 'none';
        }
    });
}

function displaySuggestions(suggestions) {
    let html = '';
    suggestions.forEach(book => {
        html += `
            <a href="${book.url}" class="autocomplete-item">
                <div style="flex: 1;">
                    <div style="font-weight: 600;">${book.title}</div>
                    <div style="font-size: 0.875rem; color: var(--gray);">by ${book.author}</div>
                </div>
                <div style="font-weight: 700; color: var(--primary-color);">₹${book.price}</div>
            </a>
        `;
    });
    autocompleteContainer.innerHTML = html;
    autocompleteContainer.style.display = 'block';
}
