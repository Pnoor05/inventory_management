export class PriceHistory {
    static init() {
        document.addEventListener('click', e => {
            const historyBtn = e.target.closest('.history-btn');
            if (historyBtn) {
                e.preventDefault();
                this.showModal(historyBtn.closest('tr').dataset.id);
            }
        });
    }

    static async showModal(productId) {
        const modalElement = document.getElementById('priceHistoryModal');
        if (!modalElement) {
            console.error('Modal element not found');
            return;
        }
        
        const modal = new bootstrap.Modal(modalElement);
        const tbody = modalElement.querySelector('tbody');
        
        tbody.innerHTML = `<tr><td colspan="5" class="text-center"><div class="spinner-border"></div></td></tr>`;
        modal.show();

        try {
            const res = await fetch(`/api/price_history/${productId}`);
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            
            const data = await res.json();
            
            tbody.innerHTML = data.length ? data.map(item => `
                <tr>
                    <td>${new Date(item.changed_at).toLocaleString()}</td>
                    <td>₹${item.old_price?.toFixed(2) || 'N/A'}</td>
                    <td>₹${item.new_price?.toFixed(2) || 'N/A'}</td>
                    <td>${item.username || 'System'}</td>
                    <td>${item.source || 'Manual'}</td>
                </tr>
            `).join('') : `<tr><td colspan="5" class="text-muted">No history found</td></tr>`;
            
            const productName = document.querySelector(`tr[data-id="${productId}"] td:nth-child(3)`).textContent;
            document.getElementById('productName').textContent = productName;
        } catch (error) {
            console.error('Error loading price history:', error);
            tbody.innerHTML = `<tr><td colspan="5" class="text-danger">Error loading data: ${error.message}</td></tr>`;
        }
    }
}