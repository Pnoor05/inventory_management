<template>
  <div class="bill-item">
    <div class="item-details">
      <span class="item-name">{{ item.product.description }}</span>
      <span class="item-price">@ {{ formatCurrency(item.unit_price) }}</span>
    </div>
    <div class="item-controls">
      <input
        type="number"
        v-model.number="quantity"
        min="1"
        class="form-control form-control-sm quantity-input"
        @change="updateQuantity"
      />
      <button class="btn btn-danger btn-sm" @click="removeItem">
        <i class="bi bi-trash"></i>
      </button>
    </div>
    <div class="item-total">
      {{ formatCurrency(item.unit_price * item.quantity) }}
    </div>
  </div>
</template>

<script>
import { formatCurrency } from '@/utils/formatters';

export default {
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      quantity: this.item.quantity
    };
  },
  watch: {
    'item.quantity'(newVal) {
      this.quantity = newVal;
    }
  },
  methods: {
    updateQuantity() {
      if (this.quantity < 1) {
        this.quantity = 1;
      }
      this.$emit('update-item', { itemId: this.item.id, quantity: this.quantity });
    },
    removeItem() {
      this.$emit('remove-item', this.item.id);
    }

  }
};
</script>

<style scoped>
.bill-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #eee;
}

.item-details {
  flex-grow: 1;
  margin-right: 1rem;
}

.item-name {
  font-weight: bold;
}

.item-price {
  font-size: 0.9em;
  color: #666;
  margin-left: 0.5rem;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-input {
  width: 60px;
  text-align: center;
}

.item-total {
  width: 80px;
  text-align: right;
  font-weight: bold;
}
</style>