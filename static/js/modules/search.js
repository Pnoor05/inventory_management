export class Search {
    static init() {
        console.log("Search.init() called");
        Search.searchInput = document.getElementById("search-input");
        if (!Search.searchInput) return;

        Search.suggestionsContainer = document.createElement("div");
        Search.suggestionsContainer.id = "suggestions-container";
        Search.suggestionsContainer.className = "suggestions-dropdown";
        Search.searchInput.parentNode.appendChild(Search.suggestionsContainer);

        console.log("Search input element:", Search.searchInput);
        Search.suggestions = [];
        Search.selectedIndex = -1;

        Search.setupEventListeners();
    }

    static setupEventListeners() {
        this.searchInput.addEventListener('input', this.debounce(this.handleInput.bind(this), 300));
 console.log('Input event listener attached to search input');
        this.searchInput.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('click', this.handleDocumentClick.bind(this));
    }

    static debounce(func, delay) {
        let timeout;
        return function() {
 console.log('Debounce function called');
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), delay);
        };
    }

    static async handleInput(e) {
 console.log('handleInput function triggered');
        console.log("handleInput called, query:", e.target.value); // query is local to the function
        const query = e.target.value.trim();
        if (query.length < 2) {
            Search.hideSuggestions();
            return;
        }

        Search.suggestions = await Search.fetchSuggestions(query);
        Search.selectedIndex = -1;
        this.showSuggestions(this.suggestions.results, query);
    }

    static async fetchSuggestions(query) {
        try {
            const response = await fetch(`/landing_search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Network error');
            const results = await response.json();
            console.log('Fetched suggestions data:', results);
            return results;
        } catch (error) {
            console.error("Error fetching suggestions:", error);
            return [];
        }
    }

    static showSuggestions(suggestions, query) {
        console.log("Showing suggestions with data:", suggestions); // Now 'suggestions' should be an array
        if (!suggestions || suggestions.length === 0) { // Add check for null/undefined suggestions
            Search.hideSuggestions();
            return;
        }

        Search.suggestionsContainer.innerHTML = suggestions.map((suggestion, index) => `
            <div class="suggestion-item ${index === Search.selectedIndex ? 'selected' : ''}" 
                 data-index="${index}"
                 onclick="Search.selectSuggestionByIndex(${index})">            
                ${suggestion.type === 'brand' 
                    ? `Brand: ${Search.highlightMatch(suggestion.brand, query)}` 
                    : Search.highlightMatch(suggestion.description, query)
                }
            </div>
        `).join('');
        Search.suggestionsContainer.style.display = 'block';
    }

    static highlightMatch(text, query) {
        const regex = new RegExp(`(${this.escapeRegExp(query)})`, "gi");
        return text.replace(regex, "<strong>$1</strong>");
    }

    static escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    static hideSuggestions() {
        Search.suggestionsContainer.innerHTML = '';
        Search.suggestionsContainer.style.display = 'none';
        Search.selectedIndex = -1;
    }

    static handleKeyDown(e) {
        if (!Search.suggestions || Search.suggestions.results.length === 0) return; // Check for null/undefined and results array

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                Search.selectedIndex = (Search.selectedIndex + 1) % Search.suggestions.results.length; // Use results.length
                Search.updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                Search.selectedIndex = (Search.selectedIndex - 1 + Search.suggestions.results.length) % Search.suggestions.results.length; // Use results.length
                Search.updateSelection();
                break;
            case 'Enter':
                if (this.selectedIndex >= 0) {
                    e.preventDefault();
                    this.selectSuggestion(document.querySelector(`.suggestion-item[data-index="${this.selectedIndex}"]`));
                }
                break;
            case 'Escape':
                Search.hideSuggestions();
                break;
        }
    }

    static updateSelection() {
        document.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
 // Use this.selectedIndex here as it refers to the class property
        });
    }

    static handleDocumentClick(e) {
        if (!Search.searchInput.contains(e.target)){
            Search.hideSuggestions();
        }
    }

    static selectSuggestionByIndex(index) {
        const selectedSuggestion = Search.suggestions.results[index]; // Access the suggestion from the results array
        // Use description or brand based on which one is available/preferred for the main search
        const searchQuery = selectedSuggestion.description || selectedSuggestion.brand;
        Search.searchInput.value = searchQuery;
 Search.hideSuggestions();

 if (selectedSuggestion.type === 'brand') {
 Search.fetchAndDisplayProducts(selectedSuggestion.brand, 'brand');
 } else {
 Search.fetchAndDisplayProducts(searchQuery);
 }
    }

    static async fetchAndDisplayProducts(searchQuery, filterType = null) {
        const categoryFilter = document.getElementById('categoryFilter').value;
        const viewDeletedCheckbox = document.getElementById('toggleDeleted');
        const viewDeleted = viewDeletedCheckbox ? (viewDeletedCheckbox.checked ? 1 : 0) : 0;

        // You might need to manage current_page as a static variable in the Search class
        // For now, let's assume it's always page 1 for a new search
        const currentPage = 1; // Or get from a static state variable

        const url = new URL('/products', window.location.origin);
        url.searchParams.append('search', searchQuery);
        url.searchParams.append('category', categoryFilter);
        url.searchParams.append('view_deleted', viewDeleted);
        url.searchParams.append('page', currentPage);
 if (filterType) {
 url.searchParams.append('filter_type', filterType);
 }

        try {
            const response = await fetch(url, { headers: {'X-Requested-With': 'XMLHttpRequest'} }); // Add header to identify as AJAX
            const data = await response.json();
            console.log(data); // Log the data for now
            // TODO: Add logic here to update the product table tbody and pagination links
        } catch (error) {
            console.error("Error fetching and displaying products:", error);
        }
    }

 static async showAddToBillModal(product) {
 // Use your existing modal system or create a simple one
 const modalHtml = `
 <div class="modal fade" id="addToBillModal" tabindex="-1">
 <div class="modal-dialog">
 <div class="modal-content">
 <div class="modal-header">
 <h5 class="modal-title">Add to Bill</h5>
 <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
 </div>
 <div class="modal-body">
 <div class="mb-3">
 <label class="form-label">Quantity</label>
 <input type="number" class="form-control" id="billQuantity" value="1" min="1">
 </div>
 <div class="mb-3">
 <label class="form-label">Select Bill</label>
 <select class="form-select" id="billSelect">
 <option value="new">New Bill</option>
 </select>
 </div>
 </div>
 <div class="modal-footer">
 <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
 <button type="button" class="btn btn-primary" id="confirmAddToBill">Add</button>
 </div>
 </div>
 </div>
 </div>
 `;

 // Inject modal into DOM
 document.body.insertAdjacentHTML('beforeend', modalHtml);
 const modal = new bootstrap.Modal(document.getElementById('addToBillModal'));

 // Load active bills
 try {
 const response = await fetch('/api/temp_bills/active');
 const bills = await response.json();
 console.log("Received bills data:", bills); // Log the received data
 const select = document.getElementById('billSelect');

 if (Array.isArray(bills)) {
 bills.forEach(bill => {
 const option = document.createElement('option');
 option.value = bill.id;
 option.textContent = `Bill #${bill.id} (${new Date(bill.created_at).toLocaleDateString()})`;
 select.appendChild(option);
 });
 } else {
 console.error("Received non-array response for active bills:", bills);
 }
 } catch (error) {
 console.error('Error fetching active bills:', error);
 }

 // Handle confirmation
 document.getElementById('confirmAddToBill').addEventListener('click', async () => {
 const quantity = parseInt(document.getElementById('billQuantity').value);
 const billId = document.getElementById('billSelect').value;

 const payload = {
 product_id: product.id,
 quantity: quantity,
 bill_id: billId === 'new' ? null : billId
 };
 console.log('Sending payload to /api/temp_bills/add_item:', JSON.stringify(payload));
 try {
 const response = await fetch('/api/temp_bills/add_item', {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 'X-CSRFToken': '{{ csrf_token() }}'
 },
 body: JSON.stringify(payload)
 });

 const result = await response.json();
 if (result.success) {
 // Show success feedback
 this.showToast('Product added to bill');

 // Close modal
 modal.hide();
 document.getElementById('addToBillModal').remove();

 // Optionally open bill editor
 if (result.bill_id) {
 window.location.href = `/temp_bill/edit/${result.bill_id}`;
 }
 }
 } catch (error) {
 console.error('Error adding to bill:', error);
 this.showToast('Failed to add product to bill', 'error');
 }
 });

 modal.show();
 }

 static showToast(message, type = 'success') {
 // Implement or integrate with your existing toast system
 const toast = document.createElement('div');
 toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'}`;
 toast.innerHTML = `
 <div class="d-flex">
 <div class="toast-body">${message}</div>
 <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
 </div>
 `;
 document.body.appendChild(toast);
 new bootstrap.Toast(toast).show();
 setTimeout(() => toast.remove(), 3000);
 }
}

// Make available globally
window.Search = Search;