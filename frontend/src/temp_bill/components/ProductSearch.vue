<template>
  <div class="product-search-panel">
    <h3>Search Products</h3>
    <div class="input-group mb-3">
      <input 
        type="text" 
        class="form-control" 
        placeholder="Search by name or code"
        v-model="searchTerm"
        @input="debouncedSearch"
      >
      <button class="btn btn-outline-secondary" type="button" @click="performSearch">
        <i class="bi bi-search"></i>
      </button>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <ul v-else-if="results.length" class="list-group search-results">
      <li 
        v-for="product in results" 
        :key="product.id" 
        class="list-group-item d-flex justify-content-between align-items-center"
      >
        <div>
          {{ product.name }} <br>
          <small class="text-muted">{{ product.code }} - ${{ product.unit_price }}</small>
        </div>
        <button class="btn btn-sm btn-success" @click="selectProduct(product)">
          Add
        </button>
      </li>
    </ul>

    <div v-else class="text-muted text-center">
      No results found.
    </div>
  </div>
</template>

<script>
import debounce from 'lodash.debounce';
import api from '../services/api'; // Assuming your API service is here

export default {
  data() {
    return {
      searchTerm: '',
      results: [],
      loading: false,
      error: null
    };
  },
  methods: {
    debouncedSearch: debounce(function() {
      if (this.searchTerm.length > 2) {
        this.performSearch();
      } else {
        this.results = [];
        this.error = null;
      }
    }, 300),
    async performSearch() {
      this.loading = true;
      this.error = null;
      try {
        // Assuming your API service has a searchProducts method
        const response = await api.searchProducts(this.searchTerm); 
        this.results = response.data; // Adjust based on your API response structure
      } catch (err) {
        this.error = 'Error fetching search results.';
        console.error('Search error:', err);
      } finally {
        this.loading = false;
      }
    },
    selectProduct(product) {
      this.$emit('add-product', product);
      this.searchTerm = '';
      this.results = [];
    }
  }
};
</script>

<style scoped>
.product-search-panel {
  padding: 1rem;
  border-right: 1px solid #eee;
  width: 300px; /* Adjust width as needed */
  flex-shrink: 0;
  overflow-y: auto;
}

.search-results {
  max-height: 400px; /* Limit height and add scrollbar */
  overflow-y: auto;
}
</style>