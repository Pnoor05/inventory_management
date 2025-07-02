<template>
  <div class="modal fade" id="discountModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Apply Discount</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Discount Type</label>
            <select v-model="discountType" class="form-select">
              <option value="percentage">Percentage</option>
              <option value="fixed">Fixed Amount</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">
              {{ discountType === 'percentage' ? 'Percentage (%)' : 'Amount' }}
            </label>
            <input
              type="number"
              class="form-control"
              v-model="discountValue"
              :min="discountType === 'percentage' ? 0 : 0"
              :max="discountType === 'percentage' ? 100 : null"
              step="0.01"
            />
          </div>
          <div class="mb-3" v-if="discountType === 'percentage'">
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                v-model="applyToSubtotal"
                id="applyToSubtotal"
              />
              <label class="form-check-label" for="applyToSubtotal">
                Apply to subtotal (before taxes)
              </label>
            </div>
          </div>
          <div class="alert alert-info" v-if="calculatedDiscount">
            Discount Amount: {{ formatCurrency(calculatedDiscount) }}
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-danger"
            v-if="hasExistingDiscount"
            @click="removeDiscount"
          >
            Remove Discount
          </button>
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click="applyDiscount"
            :disabled="!isValidDiscount"
          >
            Apply Discount
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import { useBillStore } from '../store/index.js'
import { formatCurrency } from '@/utils/formatters'

const billStore = useBillStore()
const discountModal = ref(null)
const discountType = ref('percentage')
const discountValue = ref(0)
const applyToSubtotal = ref(true)

const hasExistingDiscount = computed(() => {
  return !!billStore.currentBill?.discount
})

const isValidDiscount = computed(() => {
  return discountValue.value > 0 && 
    (discountType.value === 'fixed' || discountValue.value <= 100)
})

const calculatedDiscount = computed(() => {
  if (!isValidDiscount.value) return 0
  
  if (discountType.value === 'percentage') {
    const subtotal = billStore.currentBill?.subtotal || 0
    return subtotal * (discountValue.value / 100)
  }
  return parseFloat(discountValue.value)
})

function showModal() {
  const currentDiscount = billStore.currentBill?.discount
  if (currentDiscount) {
    discountType.value = currentDiscount.type
    discountValue.value = currentDiscount.value
    applyToSubtotal.value = currentDiscount.applyToSubtotal ?? true
  } else {
    resetForm()
  }
  discountModal.value.show()
}

function resetForm() {
  discountType.value = 'percentage'
  discountValue.value = 0
  applyToSubtotal.value = true
}

function applyDiscount() {
  billStore.applyDiscount({
    type: discountType.value,
    value: parseFloat(discountValue.value),
    applyToSubtotal: applyToSubtotal.value
  })
  discountModal.value.hide()
}

function removeDiscount() {
  billStore.removeDiscount()
  discountModal.value.hide()
}

onMounted(() => {
  discountModal.value = new Modal('#discountModal')
})

defineExpose({
  showModal
})
</script>

<style scoped>
.discount-preview {
  font-weight: bold;
  color: var(--bs-success);
}
</style>