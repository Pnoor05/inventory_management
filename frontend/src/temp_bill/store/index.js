// Assuming 'api' service exists and is used for some backend interactions
// If not, replace api calls with BillManager calls where appropriate
import api from '../services/api'; 
import { BillManager } from '../services/billManager'; // Import BillManager

import { defineStore } from 'pinia';

// Define your Pinia store
export const useBillStore = defineStore('tempBill', { // 'tempBill' is the store ID
  state: () => ({
    currentBill: null, // Renamed from 'bill' for clarity, or keep 'bill' if preferred
    isLoading: false, // Optional: Add a loading state
    error: null, // Optional: Add an error state
  }),

  actions: {
    // Action to load an existing bill or create a new one
    async loadBill(billId) {
      this.isLoading = true;
      this.error = null;
      try {
        let bill;
        if (billId && billId !== 'new') { // Existing bill
          // Assuming BillManager has a fetchBill method, or use api.fetchBill if it exists
          // If using api.fetchBill, ensure 'api' handles necessary headers (like CSRF)
          bill = await BillManager.getBill(billId); 
          this.currentBill = bill; // Directly update state in Pinia actions
        } else {
          // Should ideally redirect after creation, as handled by BillManager.createNewBill
          console.warn("loadBill called with 'new'. createNewBill should handle redirection.");
        }
      } catch (error) {
        console.error('Error loading bill:', error);
        this.error = 'Failed to load bill: ' + error.message;
        // Handle error, e.g., redirect or show message
        throw error; // Re-throw for component handling
      } finally {
        this.isLoading = false;
      }
    },

    // Action to create a new bill
    async createNewBill() {
       // This action primarily calls BillManager.createNewBill which should handle redirection
       await BillManager.createNewBill();
    },
    addProduct({ commit, state }, { product, quantity }) {
      const existingItem = state.bill.items.find(item => item.product.id === product.id);
      if (existingItem) {
        commit('UPDATE_ITEM_QUANTITY', { itemId: existingItem.id, quantity: existingItem.quantity + quantity });
      } else {
        // Assuming billManager.createBillItem is needed,
        // but typically item structure comes from the backend response.
        // If you need local item creation before saving, ensure billManager is imported.
        // import { billManager } from '../services/billManager'; // Example import if needed

        // If creating item structure locally:
        const newItem = {
          id: Date.now(), // Temporary ID
          product: product, // Ensure product structure is correct
          quantity: quantity
        };
        
        // Directly update state in Pinia actions
        if (this.currentBill && this.currentBill.items) {
           this.currentBill.items.push(newItem);
        }
        
        // Optionally save after adding an item
        this.saveBill(); 
      }
    },
    
    // Action to update item quantity
    updateItemQuantity({ itemId, quantity }) {
      if (this.currentBill && this.currentBill.items) {
        const item = this.currentBill.items.find(item => item.id === itemId);
        if (item) {
          item.quantity = quantity;
          this.saveBill(); // Optionally save after updating quantity
        }
      }
    },

    // Action to remove an item
    removeItem(itemId) {
       if (this.currentBill && this.currentBill.items) {
         this.currentBill.items = this.currentBill.items.filter(item => item.id !== itemId);
         this.saveBill(); // Optionally save after removing item
       }
    },

    // Action to set the client and save
    setClient(clientId) {
      if (!this.currentBill) return;
      this.currentBill.client_id = clientId;
      this.saveBill(); // Automatically save when client is set
    },

    // Actions to manage discount
    applyDiscount(discount) {
      if (!this.currentBill) return;
      this.currentBill.discount = discount;
      this.saveBill(); // Automatically save after applying discount
    },

    removeDiscount() { // Removed duplicate definition
      if (!this.currentBill) return;
      this.currentBill.discount = null; // Assuming null or undefined clears the discount
      this.saveBill(); // Automatically save after removing discount
    },

    // Actions to manage tax
    removeDiscount() {
      if (this.currentBill) {
        this.currentBill.tax = tax;
        this.saveBill(); // Optionally save after applying tax
      }
    },

    // Action to save the current bill state to the backend
    async saveBill() {
      if (!this.currentBill || !this.currentBill.id) {
         console.warn("Cannot save bill: No current bill or bill ID.");
         return;
      }
      try {
        // Use the BillManager to save the bill
        // Ensure BillManager.saveBill sends the full relevant state
        const savedBill = await BillManager.saveBill(this.currentBill.id, {
          client_id: this.currentBill.client_id,
          // Include other bill properties you want to save via this method,
          items: this.currentBill.items,
          discount: this.currentBill.discount, 
          tax: this.currentBill.tax,
        });
        // You might want to update the state with the response if the backend
        // returns the updated bill, including things like calculated totals or IDs for new items
        // this.currentBill = savedBill; 
        console.log('Bill saved successfully');
      } catch (error) {
        console.error('Error saving bill:', error);
        this.error = 'Failed to save bill: ' + error.message;
        throw error; // Re-throw for component handling
      }
    },
    // Action to finalize the bill
    async finalizeBill() {
      if (!this.currentBill || !this.currentBill.id) {
        console.warn("Cannot finalize bill: No current bill or bill ID.");
        return;
      }
      this.isLoading = true;
      this.error = null;
      try {
        const finalizedBill = await BillManager.finalizeBill(this.currentBill.id); // Assuming BillManager has finalizeBill
        this.currentBill = finalizedBill; // Update with final state
        console.log('Bill finalized successfully');
        // Optionally redirect or navigate after finalizing
        // e.g., router.push({ name: 'bill-view', params: { id: this.currentBill.id } });
        return finalizedBill;
      } catch (error) {
        console.error('Error finalizing bill:', error);
        this.error = 'Failed to finalize bill: ' + error.message;
        throw error; // Re-throw for component handling
      } finally {
        this.isLoading = false;
      }
    },
    
    // Helper to clear the bill state
    clearBill() {
      this.currentBill = null;
      this.error = null;
      this.isLoading = false;
    }
  },
  
  // Getters can be defined here if needed
  getters: {
    // Example getter
    // subtotal: (state) => state.currentBill?.items.reduce(...)
  }
});

window.BillManager = BillManager;