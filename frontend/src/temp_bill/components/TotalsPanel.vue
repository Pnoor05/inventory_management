<template>
  <div class="totals-panel">
    <h4>Totals</h4>
    <div class="total-row">
      <span>Subtotal:</span>
      <span>{{ formatCurrency(subtotal) }}</span>
    </div>
    <div class="total-row">
      <span>Discount:</span>
      <span>- {{ formatCurrency(discount) }}</span>
    </div>
    <div class="total-row">
      <span>Tax:</span>
      <span>+ {{ formatCurrency(tax) }}</span>
    </div>
    <hr>
    <div class="total-row total">
      <span>Total:</span>
      <span>{{ formatCurrency(total) }}</span>
    </div>
    <div class="actions mt-3">
      <button @click="$emit('add-discount')" class="btn btn-sm btn-outline-secondary me-2">
        Add Discount
      </button>
      <button @click="$emit('add-tax')" class="btn btn-sm btn-outline-secondary">
        Add Tax
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    subtotal: {
      type: Number,
      required: true
    },
    discount: {
      type: Number,
      default: 0
    },
    tax: {
      type: Number,
      default: 0
    },
    total: {
      type: Number,
      required: true
    }
  },
  methods: {
    formatCurrency(value) {
      // Implement your currency formatting logic here
      return `$${value.toFixed(2)}`;
    }
  }
}
</script>

<style scoped>
.totals-panel {
  border-top: 1px solid #eee;
  padding-top: 1rem;
  margin-top: 1rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.total-row.total {
  font-weight: bold;
  font-size: 1.2em;
}

.actions button {
  min-width: 120px;
}
</style>