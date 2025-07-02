import { Search } from "./modules/search.js";
import { BulkOps } from "./modules/bulkOps.js";
import { PriceHistory } from "./modules/priceHistory.js";
import { FormValidator } from "./modules/validation.js";

document.addEventListener('DOMContentLoaded', () => {
    // Initialize search if search input exists
    if (document.getElementById('search-input')) {
        Search.init();
    }

    // Initialize product operations if on products page
    if (document.querySelector('.product-row')) {
        BulkOps.init();
        PriceHistory.init();
        
        // Add quantity update listeners
        document.querySelectorAll('[onchange^="updateQuantity"]').forEach(input => {
            input.addEventListener('change', function() {
                const productId = this.getAttribute('data-product-id');
                updateQuantity(productId, this);
            });
        });
    }

    // Initialize form validation on all forms
    FormValidator.init();
    
    // Initialize any modals
    if (document.getElementById('priceHistoryModal')) {
        new bootstrap.Modal(document.getElementById('priceHistoryModal'));
    }
});