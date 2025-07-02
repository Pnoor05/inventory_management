// static/js/temporary_bill/services/billManager.js
export class BillManager {
    static async createNewBill() {
        try {
            const response = await fetch('/api/temp_bills', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    client_id: null,
                    template_id: null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                return {
                    success: true,
                    billId: data.bill_id,
                    billNumber: data.bill_number,
                    redirectUrl: `/temp_bill/edit/${data.bill_id}`
                };
            } else {
                throw new Error(data.error || 'Failed to create bill');
            }
        } catch (error) {
            console.error('Error creating new bill:', error);
            this.showError('Failed to create new bill: ' + error.message);
            return { success: false, error: error.message };
        }
    }

    static async addItemToBill(billId, productId, quantity) {
        try {
            const response = await fetch('/api/temp_bills/add_item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    bill_id: billId,
                    product_id: productId,
                    quantity: quantity
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error adding item to bill:', error);
            throw error;
        }
    }

    static async getBill(billId) {
        try {
            const response = await fetch(`/api/temp_bills/${billId}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching bill:', error);
            throw error;
        }
    }

    static async finalizeBill(billId) {
        try {
            const response = await fetch(`/api/temp_bills/${billId}/finalize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error finalizing bill:', error);
            throw error;
        }
    }

    static async searchClients(query) {
        try {
            const response = await fetch(`/api/clients/search?q=${encodeURIComponent(query)}`)
            return await response.json()
        } catch (error) {
            console.error('Error searching clients:', error)
            throw error
        }
    }
    static async getClient(clientId) {
        try {
            const response = await fetch(`/api/clients/${clientId}`)
            return await response.json()
        } catch (error) {
            console.error('Error fetching client:', error)
            throw error
        }
    }

    static getCSRFToken() {
        // Get CSRF token from meta tag (standard in Flask)
        return document.querySelector('meta[name="csrf-token"]').content;
    }

    static showError(message) {
        // Use your existing notification system or create a simple one
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        document.body.appendChild(toast);
        new bootstrap.Toast(toast).show();
        setTimeout(() => toast.remove(), 5000);
    }

    static async applyDiscount(billId, discount) {
        try {
            const response = await fetch(`/api/temp_bills/${billId}/discount`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(discount)
            });
             if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error applying discount to bill ${billId}:`, error);
            this.showError('Failed to apply discount: ' + error.message);
            throw error;
        }
    }
    static async removeDiscount(billId) {
        const response = await fetch(`/api/temp_bills/${billId}/discount`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });
        return await response.json();
    }

    static async applyTax(billId, tax) {
        try {
            const response = await fetch(`/api/temp_bills/${billId}/tax`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(tax)
            })
             if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json()
        } catch (error) {
            console.error(`Error applying tax to bill ${billId}:`, error);
            this.showError('Failed to apply tax: ' + error.message);
            throw error;
        }
    }
    static async removeTax(billId) {
        const response = await fetch(`/api/temp_bills/${billId}/tax`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
         if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json()
    }
}