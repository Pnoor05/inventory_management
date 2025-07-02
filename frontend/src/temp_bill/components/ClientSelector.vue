<template>
  <div class="client-selector">
    <div class="input-group mb-3">
      <input
        type="text"
        class="form-control"
        placeholder="Search clients..."
        v-model="searchQuery"
        @input="searchClients"
      />
      <button class="btn btn-outline-secondary" type="button" @click="clearSelection">
        <i class="bi bi-x"></i>
      </button>
    </div>

    <div v-if="isLoading" class="text-center py-2">
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <ul v-if="filteredClients.length" class="list-group client-list">
      <li
        v-for="client in filteredClients"
        :key="client.id"
        class="list-group-item list-group-item-action"
        :class="{ active: selectedClient?.id === client.id }"
        @click="selectClient(client)"
      >
        {{ client.name }} - {{ client.email || client.phone }}
      </li>
    </ul>

    <div v-if="searchQuery && !filteredClients.length && !isLoading" class="alert alert-info">
      No clients found matching "{{ searchQuery }}"
    </div>

    <div v-if="selectedClient" class="selected-client mt-3">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">{{ selectedClient.name }}</h5>
          <p class="card-text mb-1" v-if="selectedClient.email">
            <i class="bi bi-envelope"></i> {{ selectedClient.email }}
          </p>
          <p class="card-text" v-if="selectedClient.phone">
            <i class="bi bi-telephone"></i> {{ selectedClient.phone }}
          </p>
          <button class="btn btn-sm btn-outline-danger mt-2" @click="clearSelection">
            Remove Client
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useBillStore } from '../store/index.js'
import { BillManager } from '@/temp_bill/services/billManager'

const billStore = useBillStore()
const searchQuery = ref('')
const isLoading = ref(false)
const clients = ref([])
const selectedClient = ref(null)

// Fetch initial clients if needed
onMounted(async () => {
  if (billStore.currentBill?.client_id) {
    await fetchClientDetails(billStore.currentBill.client_id)
  }
})

const filteredClients = computed(() => {
  if (!searchQuery.value) return []
  return clients.value.filter(client =>
    client.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    (client.email && client.email.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
    (client.phone && client.phone.includes(searchQuery.value))
  )
})

async function searchClients() {
  if (searchQuery.value.length < 2) {
    clients.value = []
    return
  }

  isLoading.value = true
  try {
    const response = await BillManager.searchClients(searchQuery.value)
    clients.value = response.data
  } catch (error) {
    console.error('Error searching clients:', error)
  } finally {
    isLoading.value = false
  }
}

async function fetchClientDetails(clientId) {
  isLoading.value = true
  try {
    const response = await BillManager.getClient(clientId)
    selectedClient.value = response.data
  } catch (error) {
    console.error('Error fetching client details:', error)
  } finally {
    isLoading.value = false
  }
}

function selectClient(client) {
  selectedClient.value = client
  searchQuery.value = ''
  clients.value = []
  billStore.setClient(client.id)
}

function clearSelection() {
  selectedClient.value = null
  billStore.setClient(null)
}

// Watch for client changes from other components
watch(
  () => billStore.currentBill?.client_id,
  (newClientId) => {
    if (newClientId && (!selectedClient.value || selectedClient.value.id !== newClientId)) {
      fetchClientDetails(newClientId)
    } else if (!newClientId) {
      selectedClient.value = null
    }
  }
)
</script>

<style scoped>
.client-selector {
  margin-bottom: 1.5rem;
}

.client-list {
  max-height: 300px;
  overflow-y: auto;
  border-radius: 0.25rem;
}

.client-list li {
  cursor: pointer;
}

.client-list li:hover:not(.active) {
  background-color: #f8f9fa;
}

.selected-client {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>