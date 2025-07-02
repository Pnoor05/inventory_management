class LandingSearch {
    static init() {
        this.searchInput = document.getElementById('search-input');
        this.resultsContainer = document.getElementById('results-container');
        this.selectedIndex = -1;
        this.results = [];

        if (!this.searchInput) return;

        this.setupEventListeners();
 this.setupCreateBillButton();
    }

    static setupEventListeners() {
        this.searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        this.searchInput.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.resultsContainer.contains(e.target)) {
                this.hideResults();
            }
        });
    }

 static setupCreateBillButton() {
        const createBillButton = document.getElementById('create-bill-button');
        if (createBillButton) {
            createBillButton.addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/temp_bills/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            // Add CSRF token if your Flask app requires it
                            'X-CSRFToken': '{{ csrf_token() }}' // Ensure this is rendered correctly in your template
                        }
                    });
                    const result = await response.json();
                    if (response.ok && result.bill_id) {
                        window.location.href = `/temp_bill/edit/${result.bill_id}`;
                    } else {
                        console.error('Failed to create new bill:', result.error);
                        // Optionally show an error message to the user
                    }
                } catch (error) {
                    console.error('Error creating new bill:', error);
                    // Optionally show an error message to the user
                }
            });
        }
    }

    static async handleSearch() {
        const query = this.searchInput.value.trim();
        this.selectedIndex = -1;

        if (query.length < 2) {
            this.hideResults();
            return;
        }

        try {
            const response = await fetch(`/landing_search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Network error');
            const data = await response.json();

            if (data.error) throw new Error(data.error);
            this.results = data.results;
            this.displayResults(this.results);
        } catch (error) {
            console.error("Search error:", error);
            this.showError();
        }
    }

    static displayResults(results) {
        if (!results || results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="result-item">
                    No products found
                </div>`;
            this.resultsContainer.style.display = 'block';
            return;
        }

        this.resultsContainer.innerHTML = results.map((item, index) => {
            if (item.type === 'brand') {
                return `
                    <div class="result-item ${index === this.selectedIndex ? 'selected' : ''}"
                         data-index="${index}" data-type="brand" data-brand="${item.brand}">
                        <div class="product-brand">Brand: ${item.brand}</div>
                    </div>
                `;
            } else { // Assuming it's a product
                return `
                    <div class="result-item ${index === this.selectedIndex ? 'selected' : ''}"
                         data-id="${item.id}"
                         data-index="${index}" data-type="product">
                        <div class="fw-bold">${item.brand} ${item.description}</div>
                        <div class="d-flex justify-content-between mt-1">
                            <span>${item.unit_price ? '₹' + item.unit_price.toFixed(2) : ''}</span>
                            <span class="stock-badge ${item.quantity_in_stock > 0 ? 'in-stock' : 'out-of-stock'}">\n                                ${item.quantity_in_stock > 0 ? `${item.quantity_in_stock} in stock` : 'Out of stock'}\n                            </span>
                        </div>
                        <div class="text-muted small">${item.category}</div>
                    </div>
                `;
            }
        }).join('');

        this.resultsContainer.style.display = 'block';

        document.querySelectorAll('.result-item').forEach(item => {
            item.addEventListener('click'), () => {
                const productId = item.dataset.id; // Assuming data-id attribute holds the product ID
                this.hideResults();
            }
        });
    }

    static async handleSearch() {
        const query = this.searchInput.value.trim();
        this.selectedIndex = -1;

        if (query.length < 2) {
            this.hideResults();
            return;
        }

        try {
            const response = await fetch(`/landing_search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Network error');
            const data = await response.json();

            if (data.error) throw new Error(data.error);
            this.results = data.results;
            this.displayResults(this.results);
        } catch (error) {
            console.error("Search error:", error);
            this.showError();
        }
    }

    static displayResults(results) {
        if (!results || results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="result-item">
                    No products found
                </div>`;
            this.resultsContainer.style.display = 'block';
            return;
        }

        this.resultsContainer.innerHTML = results.map((item, index) => {
            if (item.type === 'brand') {
                return `
                    <div class="result-item ${index === this.selectedIndex ? 'selected' : ''}"
                         data-index="${index}" data-type="brand" data-brand="${item.brand}">
                        <div class="product-brand">Brand: ${item.brand}</div>
                    </div>
                `;
            } else { // Assuming it's a product
                return `
                    <div class="result-item ${index === this.selectedIndex ? 'selected' : ''}"
                         data-id="${item.id}"
                         data-index="${index}" data-type="product">
                        <div class="fw-bold">${item.brand} ${item.description}</div>
                        <div class="d-flex justify-content-between mt-1">
                            <span>${item.unit_price ? '₹' + item.unit_price.toFixed(2) : ''}</span>
                            <span class="stock-badge ${item.quantity_in_stock > 0 ? 'in-stock' : 'out-of-stock'}">
                                ${item.quantity_in_stock > 0 ? `${item.quantity_in_stock} in stock` : 'Out of stock'}
                            </span>
                        </div>
                        <div class="text-muted small">${item.category}</div>
                    </div>
                `;
            }
        }).join('');

        this.resultsContainer.style.display = 'block';

        document.querySelectorAll('.result-item').forEach(item => {
            item.addEventListener('click', () => {
                const productId = item.dataset.id; // Assuming data-id attribute holds the product ID
                window.location.href = `/products?selected_product_id=${productId}`;
            });
        });
    }

    static handleKeyDown(e) {
        if (!this.results || this.results.length === 0) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.results.length - 1);
                this.updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
            case 'Enter':
                if (this.selectedIndex >= 0) {
                    const selectedItem = document.querySelector(`.result-item[data-index="${this.selectedIndex}"]`);
                    const itemType = selectedItem.dataset.type;
                    if (itemType === 'brand') {
                        const brandName = selectedItem.dataset.brand;
                        // Redirect to product list page with brand filter
                        window.location.href = `/products?search=${encodeURIComponent(brandName)}&filter_type=brand`;
                    } else { // Product
                        selectedItem.click(); // Use the existing product click handler
                    }
                }
                break;
            case 'Escape':
                this.hideResults();
                break;
        }
    }

    static updateSelection() {
        document.querySelectorAll('.result-item').forEach(item => {
            item.classList.remove('selected');
        });

        if (this.selectedIndex >= 0) {
            const selectedItem = document.querySelector(`.result-item[data-index="${this.selectedIndex}"]`);
            selectedItem.classList.add('selected');
            selectedItem.scrollIntoView({ block: 'nearest' });
        }
    }

    static showError() {
        this.resultsContainer.innerHTML = `
            <div class="result-item text-danger">
                Error loading results. Please try again.
            </div>`;
        this.resultsContainer.style.display = 'block';
    }

    static hideResults() {
        this.resultsContainer.style.display = 'none';
        this.selectedIndex = -1;
    }

    static debounce(func, delay) {
        let timeout;
        return function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, arguments), delay);
        };
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', LandingSearch.init.bind(LandingSearch));