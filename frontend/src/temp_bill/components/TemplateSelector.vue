<template>
  <div class="template-selector">
    <label for="templateSelect" class="form-label">Template:</label>
    <select 
      id="templateSelect" 
      class="form-select" 
      :value="selectedTemplateId" 
      @change="handleTemplateChange"
    >
      <option value="">Select Template</option>
      <option 
        v-for="template in templates" 
        :key="template.id" 
        :value="template.id"
      >
        {{ template.name }}
      </option>
    </select>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  props: {
    value: {
      type: [String, Number, null],
      default: null
    }
  },
  data() {
    return {
      templates: [] // This should be populated from an API or initial data
    };
  },
  computed: {
    selectedTemplateId: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit('input', value); // For v-model
        this.$emit('change', value); // Emit change event
      }
    }
  },
  methods: {
    ...mapActions('tempBill', ['applyTemplate']), // Assuming an action exists to apply template
    handleTemplateChange(event) {
      const templateId = event.target.value;
      this.selectedTemplateId = templateId;
      if (templateId) {
        // Optionally fetch template details and apply
        // this.applyTemplate(templateId); 
      }
    },
    async fetchTemplates() {
      // Replace with your actual API call
      try {
        const response = await fetch('/api/templates'); 
        if (!response.ok) {
          throw new Error('Failed to fetch templates');
        }
        const data = await response.json();
        this.templates = data;
      } catch (error) {
        console.error('Error fetching templates:', error);
        // Handle error appropriately
      }
    }
  },
  created() {
    this.fetchTemplates(); // Fetch templates when component is created
  }
};
</script>

<style scoped>
.template-selector {
  /* Add styling as needed */
}
</style>