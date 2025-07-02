// static/js/modules/priceHistory.js
export class PriceHistory {
    static init() {
        document.addEventListener('click', e => {
            if (e.target.closest('.history-btn')) {
                const productId = e.target.closest('tr').dataset.id;
                this.showModal(productId);
            }
        });
    }

    static async showModal(productId) {
        const modal = new bootstrap.Modal('#priceHistoryModal');
        const tbody = document.querySelector('#priceHistoryModal tbody');
        
        // Show loading state
        tbody.innerHTML = `<tr><td colspan="4" class="text-center"><div class="spinner-border"></div></td></tr>`;
        modal.show();

        try {
            const response = await fetch(`/api/price_history/${productId}`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            
            tbody.innerHTML = data.length ? data.map(item => `
                <tr>
                    <td>${new Date(item.changed_at).toLocaleString()}</td>
                    <td>₹${item.old_price.toFixed(2)}</td>
                    <td>₹${item.new_price.toFixed(2)}</td>
                    <td>${item.username || 'System'}</td>
                </tr>
            `).join('') : `<tr><td colspan="4">No history found</td></tr>`;
            
            // Update product name in modal title
            const productName = document.querySelector(`tr[data-id="${productId}"] td:nth-child(3)`).textContent;
            document.getElementById('productName').textContent = productName;
        } catch (error) {
            console.error('Error:', error);
            tbody.innerHTML = `<tr><td colspan="4" class="text-danger">Error loading data</td></tr>`;
        }
    }
}