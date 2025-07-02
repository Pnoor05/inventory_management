/**
 * Handles all bulk operations and context menus
 * Preserves original functionality from both view_products.js and view_products_action.js
 */
export class BulkOps {
    static init() {
        this.setupContextMenus();
        this.setupBulkActions();
        this.setupToggleDeleted();
    }

    /* Original view_products_action.js functionality */
    static setupContextMenus() {
        document.querySelectorAll('.product-row').forEach(row => {
            row.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.showContextMenu(e, row.dataset.id);
            });
        });
    }

    static showContextMenu(e, productId) {
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.position = 'absolute';
        menu.style.left = `${e.pageX}px`;
        menu.style.top = `${e.pageY}px`;
        
        // Original delete/restore logic
        if (document.getElementById('toggleDeleted')?.checked) {
            menu.innerHTML = `
                <button onclick="restoreProduct(${productId})">
                    <i class="bi bi-arrow-counterclockwise"></i> Restore
                </button>
            `;
        } else {
            menu.innerHTML = `
                <button onclick="editProduct(${productId})">
                    <i class="bi bi-pencil"></i> Edit
                </button>
                <button onclick="deleteProduct(${productId})">
                    <i class="bi bi-trash"></i> Delete
                </button>
            `;
        }

        document.body.appendChild(menu);
        document.addEventListener('click', () => menu.remove(), { once: true });
    }

    /* Original view_products.js functionality */
    static setupBulkActions() {
        const bulkSelectBtn = document.getElementById('bulkSelect');
        if (!bulkSelectBtn) return;

        bulkSelectBtn.addEventListener('click', this.enableBulkMode);
        document.getElementById('cancelBulk')?.addEventListener('click', this.disableBulkMode);
        document.getElementById('bulkDelete')?.addEventListener('click', this.deleteSelected);
    }

    static enableBulkMode() {
        document.getElementById('bulkSelect').classList.add('d-none');
        document.getElementById('bulkActions').classList.remove('d-none');
        
        document.querySelectorAll('.product-row').forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', this.toggleRowSelection);
        });
    }

    static toggleRowSelection(e) {
        const row = e.currentTarget;
        if (e.target.tagName === 'INPUT' || e.target.closest('button')) return;
        
        row.classList.toggle('table-primary');
        row.dataset.selected = row.dataset.selected === 'true' ? 'false' : 'true';
    }

    static deleteSelected() {
        const selectedIds = Array.from(document.querySelectorAll('.product-row[data-selected="true"]'))
            .map(row => row.dataset.id);
        
        if (selectedIds.length > 0 && confirm(`Delete ${selectedIds.length} selected items?`)) {
            fetch('/bulk_delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: selectedIds })
            }).then(() => window.location.reload());
        }
    }

    static setupToggleDeleted() {
        document.getElementById('toggleDeleted')?.addEventListener('change', function() {
            window.location.href = `?view_deleted=${this.checked ? 1 : 0}`;
        });
    }
}

/* Preserve original global functions */
window.deleteProduct = function(productId) {
    if (confirm("Are you sure you want to delete this product?")) {
        fetch(`/delete_product/${productId}`, { method: "POST" })
            .then(() => window.location.reload());
    }
};

window.restoreProduct = function(productId) {
    fetch(`/restore_product/${productId}`, { method: "POST" })
        .then(() => window.location.reload());
};

window.editProduct = function(productId) {
    window.location.href = `/edit_product/${productId}`;
};