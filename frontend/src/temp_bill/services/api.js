import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
})

export default {
  // Temp Bill API
  getTempBills() {
    return apiClient.get('/temp_bills')
  },
  getTempBill(id) {
    return apiClient.get(`/temp_bills/${id}`)
  },
  createTempBill(clientId = null, templateId = null) {
    return apiClient.post('/api/temp_bills', { client_id: clientId, template_id: templateId })
  },
  addBillItem(billId, productId, quantity) {
    return apiClient.post(`/temp_bills/${billId}/items`, { product_id: productId, quantity })
  },
  updateBillItem(billId, itemId, quantity) {
    return apiClient.put(`/temp_bills/${billId}/items/${itemId}`, { quantity })
  },
  removeBillItem(billId, itemId) {
    return apiClient.delete(`/temp_bills/${billId}/items/${itemId}`)
  },
  applyDiscount(billId, discount) {
    return apiClient.post(`/temp_bills/${billId}/discount`, discount)
  },
  removeDiscount(billId) {
    return apiClient.delete(`/temp_bills/${billId}/discount`)
  },
  applyTax(billId, tax) {
    return apiClient.post(`/temp_bills/${billId}/tax`, tax)
  },
  removeTax(billId) {
    return apiClient.delete(`/temp_bills/${billId}/tax`)
  },
  finalizeBill(billId) {
    return apiClient.post(`/temp_bills/${billId}/finalize`)
  },
  getBillPreview(billId) {
    return apiClient.get(`/temp_bills/${billId}/preview`)
  }
}