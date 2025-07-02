<template>
  <div class="modal fade" id="taxModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Configure Tax</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Tax Name</label>
            <input
              type="text"
              class="form-control"
              v-model="taxName"
              placeholder="e.g. GST, VAT, Sales Tax"
            />
          </div>
          <div class="mb-3">
            <label class="form-label">Tax Rate (%)</label>
            <input
              type="number"
              class="form-control"
              v-model="taxRate"
              min="0"
              max="100"
              step="0.01"
            />
          </div>
          <div class="mb-3">
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                v-model="isInclusive"
                id="taxInclusive"
              />
              <label class="form-check-label" for="taxInclusive">
                Tax is already included in prices
              </label>
            </div>
          </div>
          <div class="alert alert-info" v-if="calculatedTax">
            Estimated Tax Amount: {{ formatCurrency(calculatedTax) }}
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-danger"
            v-if="hasExistingTax"
            @click="removeTax"
          >
            Remove Tax
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
            @click="applyTax"
            :disabled="!isValidTax"
          >
            Apply Tax
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import { useBillStore } from '../store/index.js'
import { formatCurrency } from '@/utils/formatters'

const billStore = useBillStore()
const taxModal = ref(null)
const taxName = ref('')
const taxRate = ref(0)
const isInclusive = ref(false)

const hasExistingTax = computed(() => {
  return !!billStore.currentBill?.tax
})

const isValidTax = computed(() => {
  return taxRate.value > 0 && taxRate.value <= 100 && taxName.value.trim() !== ''
})

const calculatedTax = computed(() => {
  if (!isValidTax.value) return 0
  
  const subtotal = billStore.currentBill?.subtotal || 0
  const discount = billStore.currentBill?.discount?.value || 0
  const discountType = billStore.currentBill?.discount?.type || 'fixed'
  
  let taxableAmount = subtotal
  if (discountType === 'percentage') {
    taxableAmount = subtotal * (1 - (discount / 100))
  } else {
    taxableAmount = subtotal - discount
  }
  
  return taxableAmount * (taxRate.value / 100)
})

function showModal() {
  const currentTax = billStore.currentBill?.tax
  if (currentTax) {
    taxName.value = currentTax.name || ''
    taxRate.value = currentTax.rate || 0
    isInclusive.value = currentTax.inclusive || false
  } else {
    resetForm()
  }
  taxModal.value.show()
}

function resetForm() {
  taxName.value = 'Sales Tax'
  taxRate.value = 0
  isInclusive.value = false
}

function applyTax() {
  billStore.applyTax({
    name: taxName.value.trim(),
    rate: parseFloat(taxRate.value),
    inclusive: isInclusive.value
  })
  taxModal.value.hide()
}

function removeTax() {
  billStore.removeTax()
  taxModal.value.hide()
}

onMounted(() => {
  taxModal.value = new Modal('#taxModal')
})

defineExpose({
  showModal
})
</script>

<style scoped>
.tax-preview {
  font-weight: bold;
  color: var(--bs-primary);
}
</style>