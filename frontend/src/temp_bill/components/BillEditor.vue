<template>
  <div class="bill-editor">
    <div class="editor-header">
      <h2>
        <span v-if="bill.bill_number">{{ bill.bill_number }}</span>
        <span v-else>New Temporary Bill</span>
      </h2>
      <div class="header-actions">
        <button @click="saveDraft" class="btn btn-outline-secondary">
          <i class="bi bi-save"></i> Save Draft
        </button>
        <button @click="finalizeBill" class="btn btn-success">
          <i class="bi bi-check-circle"></i> Finalize
        </button>
      </div>
    </div>

    <div>
      <DiscountModal ref="discountModal" />
      <button @click="showDiscountModal" class="btn btn-sm btn-outline-secondary">
        <i class="bi bi-percent"></i> Discount
      </button>  
    </div>
    
    <div>
      <TaxModal ref="taxModal" />
      <button @click="showTaxModal" class="btn btn-sm btn-outline-secondary">
        <i class="bi bi-calculator"></i> Tax
      </button>    
    </div>

    <div class="editor-container">
      <ProductSearch @add-product="addProductToBill" />

      <div class="bill-container">
        <BillTabs />

        <div class="bill-header">
 <ClientSelector />
          <TemplateSelector v-model="bill.template_id" />
        </div>

        <div class="bill-items">
          <BillItem
            v-for="item in bill.items"
            :key="item.id"
            :item="item"
            @update-item="updateItem"
            @remove-item="removeItem"
          />
        </div>

        <TotalsPanel
          :subtotal="subtotal"
          :discount="discount"
          :tax="tax"
          :total="total"
          @add-discount="showDiscountModal"
          @add-tax="showTaxModal"
        />
      </div>
    </div>

    <!-- Modals for discount and tax -->
    <DiscountModal
      v-if="showDiscount"
      :current-discount="bill.discount"
      @apply-discount="applyDiscount"
      @close="showDiscount = false"
    />
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import BillItem from './BillItem.vue';
import BillTabs from './BillTabs.vue';
import ProductSearch from './ProductSearch.vue';
import TotalsPanel from './TotalsPanel.vue';
import TemplateSelector from './TemplateSelector.vue';
import ClientSelector from './ClientSelector.vue';
import DiscountModal from './DiscountModal.vue';
import TaxModal from './TaxModal.vue';

export default {
  components: {
    BillItem,
    BillTabs,
    ProductSearch,
    TotalsPanel,
    TemplateSelector,
    ClientSelector,
    DiscountModal,
    TaxModal,
  },
  data() {
    return {
      showDiscount: false,
    };
  },
  computed: {
    ...mapState('tempBill', ['bill']),
    subtotal() {
      if (!this.bill || !this.bill.items) return 0;
      return this.bill.items.reduce(
        (sum, item) => sum + item.unit_price * item.quantity,
        0
      );
    },
    discount() {
      if (!this.bill || !this.bill.discount) return 0;
      return this.bill.discount.type === 'percentage'
        ? this.subtotal * (this.bill.discount.value / 100)
        : this.bill.discount.value;
    },
    tax() {
      if (!this.bill || !this.bill.tax) return 0;
      return (this.subtotal - this.discount) * (this.bill.tax.rate / 100);
    },
    total() {
      return this.subtotal - this.discount + this.tax;
    },
  },
  methods: {
    ...mapActions('tempBill', [
      'addProduct',
      'updateItemQuantity',
      'removeItem',
      'applyDiscount',
      'applyTax',
      'saveBill',
      'finalizeBill',
    ]),
    addProductToBill(product) {
      this.addProduct({
        product,
        quantity: 1, // Default quantity
      });
    },
    updateItem({ itemId, quantity }) {
      this.updateItemQuantity({ itemId, quantity });
    },
    removeItem(itemId) {
      this.removeItem(itemId);
    },
    showDiscountModal() {
      this.showDiscount = true;
    },
    showTaxModal() {
      this.$refs.taxModal.showModal()
    },
    async saveDraft() {
      try {
        await this.saveBill();
        // Add success notification
        console.log('Draft saved successfully');
      } catch (error) {
        // Add error notification
        console.error('Failed to save draft:', error);
      }
    },
    async finalizeBill() {
      try {
        await this.finalizeBill();
        // Add success notification and possibly redirect
        console.log('Bill finalized successfully');
        // Example redirect: this.$router.push({ name: 'bill-preview', params: { id: this.bill.id } });
      } catch (error) {
        // Add error notification
        console.error('Failed to finalize bill:', error);
      }
    },
  },
  created() {
    // Initialize the bill when the component is created (e.g., from route params)
    // This assumes the route includes a bill ID for editing, or you handle new bills
    const billId = this.$route.params.id; // Example: getting ID from Vue Router
    this.$store.dispatch('tempBill/initializeBill', billId);
  },
};
</script>

<style scoped>
.bill-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.editor-container {
  display: flex;
  flex: 1;
  overflow: hidden; /* Prevent overflow from internal components */
}

.bill-container {
  flex: 1; /* Take remaining space */
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow-y: auto; /* Enable scrolling for bill items */
}

.bill-header {
  display: flex;
  gap: 1rem; /* Space between selectors */
  margin-bottom: 1rem;
}

.bill-items {
  flex: 1; /* Allow items to take available vertical space */
  overflow-y: auto; /* Scrollable if many items */
}
</style>