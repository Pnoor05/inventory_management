<template>
  <div class="template-manager">
    <!-- Template List -->
    <div class="template-list">
      <div class="template-card" v-for="t in templates" :key="t.id" @click="loadTemplate(t)">
        <img :src="t.thumbnail || '/static/default-template.png'">
        <span>{{ t.name }}</span>
      </div>
       <div class="template-card" @click="createNewTemplate">
         <img src="/static/add-template.png" alt="Add new template">
         <span>New Template</span>
       </div>
    </div>

    <!-- Variables Toolbar -->
    <div v-if="activeTemplate.id !== null" class="variables-toolbar mt-3">
      <h6>Insert Variable:</h6>
      <button v-for="(varData, varName) in standardVars"
              :key="varName"
              @click="insertVariable(varName)" class="btn btn-outline-secondary btn-sm me-2">
        {{ varName }}
      </button>
    </div>
    <!-- Template Editor (CKEditor) -->
    <div v-if="activeTemplate.id !== null" class="template-editor">
        <input type="text" v-model="activeTemplate.name" placeholder="Template Name" class="form-control mb-3">
        <ckeditor :editor="editor" v-model="activeTemplate.html" :config="editorConfig"></ckeditor>
    </div>

    <!-- Upload Asset -->
    <div v-if="activeTemplate.id !== null" class="upload-section mt-3">
      <h6>Upload Asset:</h6>
      <input type="file" @change="uploadAsset" class="form-control-file me-2"/>
      <button @click="insertAssetUrl" class="btn btn-outline-secondary btn-sm">Insert Asset URL</button>
    </div>

    <!-- Toolbar for actions -->
    <div v-if="activeTemplate.id !== null" class="toolbar mt-3">
      <button class="btn btn-primary me-2" @click="saveTemplate">Save</button>
      <button class="btn btn-secondary me-2" @click="setDefault">Set Default</button>
       <button class="btn btn-danger" @click="deleteTemplate">Delete</button>
    </div>

    <!-- Bill Preview Section -->
    <div class="bill-preview-container mt-4" v-if="billPreviewHtml">
      <h4>Bill Preview:</h4>
      <iframe :srcdoc="billPreviewHtml" frameborder="0" width="100%" height="600px"></iframe>
      <button @click="exportPDF" class="btn btn-success mt-2">Export PDF</button>
  </div>
</template>

<script>
import CKEditor from '@ckeditor/ckeditor5-vue';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'; // Assuming you're using the classic build

export default {
  props: {
    userId: {
      type: Number,
      required: true
    }
  },
  components: {
    // <ckeditor> component has to be registered in order to be used
    // in the template.
    // Learn more about CKEditor 5 + Vue integration here:
    ckeditor: CKEditor.component
  },
  data() {
    return {
      templates: [],
      activeTemplate: {
        id: null,
        name: '',
        html: '',
        thumbnail: '' // You might want a more robust way to handle thumbnails
      },
      editor: ClassicEditor, // Use the imported editor build
      editorConfig: {
        // CKEditor 5 configuration options
        // For example, you can configure the toolbar:
        // toolbar: [ 'heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote' ],
      },
      standardVars: {
        'invoice_id': 'Invoice ID',
        'date': 'Date',
        'items': 'Items Table'
      },
      billPreviewHtml: '', // The rendered HTML for the bill preview
      uploadedAssetUrl: '',  // URL for the uploaded asset
    };
  },
  created() {
    this.fetchTemplates();
  },
  methods: {
    fetchTemplates() {
      // Replace with your actual API call to fetch templates for the user
      // Assuming your backend endpoint is '/api/templates?user_id=<user_id>'
      // You might need to use a library like axios or the built-in fetch API
      fetch(`/api/templates?user_id=${this.userId}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.templates = data;
        })
        .catch(error => {
          console.error("Error fetching templates:", error);
          // Handle error, e.g., show an alert to the user
        });
    },
    loadTemplate(template) {
      this.activeTemplate = { ...template };
      this.renderBillPreview(); // Render preview when a template is loaded
    },
    createNewTemplate() {
        this.activeTemplate = {
            id: null,
            name: 'New Template',
            html: '<p>Start building your template here...</p>',
            thumbnail: ''
        };
    },
    saveTemplate() {
      const url = this.activeTemplate.id ? `/api/templates/${this.activeTemplate.id}` : '/api/templates';
      const method = this.activeTemplate.id ? 'PUT' : 'POST';

      // Replace with your actual API call to save/create template
      fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...this.activeTemplate, user_id: this.userId }),
      })
        .then(response => response.json())
        .then(data => {
          alert(data.message);
          this.fetchTemplates(); // Refresh template list
          if (!this.activeTemplate.id && data.id) {
             // If it was a new template creation, update activeTemplate with new ID
             this.activeTemplate.id = data.id;
          }
        })
        .catch(error => {
          console.error("Error saving template:", error);
          alert('Error saving template.');
        });
    },
    deleteTemplate() {
      if (!confirm('Are you sure you want to delete this template?')) {
        return;
      }
      // Replace with your actual API call to delete template
      fetch(`/api/templates/${this.activeTemplate.id}`, {
        method: 'DELETE',
      })
        .then(response => response.json())
        .then(data => {
          alert(data.message);
          this.activeTemplate = { // Reset active template after deletion
            id: null, name: '', html: '', thumbnail: ''
          };
          this.billPreviewHtml = ''; // Clear preview
          this.fetchTemplates(); // Refresh template list
        })
        .catch(error => {
          console.error("Error deleting template:", error);
          alert('Error deleting template.');
        });
    },
    setDefault() {
      if (!this.activeTemplate.id) {
        alert('Please select or save a template first.');
        return;
      }
      // Replace with your actual API call to set default template
      fetch(`/api/templates/${this.activeTemplate.id}/set_default?user_id=${this.userId}`, {
        method: 'PUT',
      })
        .then(response => response.json())
        .then(data => {
          alert(data.message);
          this.fetchTemplates(); // Refresh template list to show default status
        })
        .catch(error => {
          console.error("Error setting default:", error);
          alert('Error setting default template.');
        });
    },
    insertVariable(variable) {
      const placeholder = `{{ ${variable} }}`;
      // Get the editor instance to insert at the current cursor position
      const editorInstance = this.editor.instances[0]; // Assuming one editor instance
      if (editorInstance) {
        editorInstance.execute('insertText', { value: placeholder });
      } else {
         // Fallback if editor instance not found (might append instead)
         this.activeTemplate.html += placeholder;
      }
    },
    renderBillPreview() {
      if (!this.activeTemplate.html) {
        this.billPreviewHtml = '';
        return;
      }
      const templateHtml = this.activeTemplate.html; // The template HTML with variables
      // Sample variables - replace with actual data fetching logic
      const variables = {
        invoice_id: 'INV-2023-001',
        date: '2025-05-11',
        items: [
          { name: 'Product A', price: 10.0, quantity: 2, total: 20.0 },
          { name: 'Product B', price: 15.0, quantity: 1, total: 15.0 },
        ]
      };

      this.billPreviewHtml = this.renderTemplate(templateHtml, variables);
    },
    renderTemplate(templateHtml, variables) {
      // Replaces placeholders in the template with real values
      let renderedHtml = templateHtml;
      for (const [key, value] of Object.entries(variables)) {
        const placeholder = `{{ ${key} }}`;
        if (renderedHtml.includes(placeholder)) {
          if (key === 'items') {
            // Render table for items
            const itemsTable = Array.isArray(value) ? value.map(item => `
              <tr>
                <td>${item.name || ''}</td>
                <td>${item.quantity || ''}</td>
                <td>${item.price || ''}</td>
                <td>${item.total || ''}</td>
              </tr>
            `).join('') : ''; // Handle non-array items gracefully
            renderedHtml = renderedHtml.replace('{{ items }}', `<table><thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead><tbody>${itemsTable}</tbody></table>`);
          } else {
            renderedHtml = renderedHtml.replace(new RegExp(placeholder.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'g'), value); // Use regex for global replace
          }
        }
      }
      return renderedHtml;
    },
    async exportPDF() {
      if (!this.billPreviewHtml) {
        alert('No bill preview to export.');
        return;
      }
      // Ensure jsPDF and html2canvas are loaded
      if (typeof jsPDF === 'undefined' || typeof html2canvas === 'undefined') {
        alert('PDF export libraries not loaded.');
        console.error('jsPDF or html2canvas is not loaded.');
        return;
      }

      const doc = new jsPDF('p', 'mm', 'a4');
      const iframe = document.querySelector('.bill-preview-container iframe');

      if (!iframe || !iframe.contentDocument || !iframe.contentDocument.body) {
          console.error('Iframe or iframe content not accessible.');
          alert('Could not access bill preview content for PDF export.');
          return;
      }

      try {
          const canvas = await html2canvas(iframe.contentDocument.body, { scale: 2 }); // Use scale for better resolution
          const imgData = canvas.toDataURL('image/png');

          const imgWidth = 210; // A4 width in mm
          const pageHeight = 295; // A4 height in mm
          const imgHeight = canvas.height * imgWidth / canvas.width;
          let heightLeft = imgHeight;

          let position = 0;

          doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;

          while (heightLeft >= 0) {
            position = heightLeft - imgHeight;
            doc.addPage();
            doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
          }

          doc.save('bill.pdf');
      } catch (error) {
          console.error("Error generating PDF:", error);
          alert('Error generating PDF. Please try again.');
      }
    },
    async uploadAsset(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        // Replace with your actual API call to upload asset
        const response = await fetch('/api/upload_asset', {
           method: 'POST',
           body: formData,
           // Note: Content-Type header is usually not needed for FormData with fetch
        });
        if (!response.ok) {
             const errorData = await response.json();
             throw new Error(errorData.error || 'Error uploading asset');
        }
        const data = await response.json();
        this.uploadedAssetUrl = data.url;
        alert(`Asset uploaded: ${this.uploadedAssetUrl}`);

        // Optionally, insert the URL into the editor immediately after successful upload
        this.insertAssetUrl();

      } catch (error) {
        console.error("Error uploading asset:", error);
        alert(`Error uploading asset: ${error.message}`);
      }
    },
    insertAssetUrl() {
      if (this.uploadedAssetUrl) {
         const editorInstance = this.editor.instances[0]; // Assuming one editor instance
         if (editorInstance) {
            // You might want a more sophisticated way to insert based on file type
            // For images, insert an img tag
            if (this.uploadedAssetUrl.match(/\.(png|jpg|jpeg|gif|svg)$/i)) {
               editorInstance.execute('insertHtml', `<img src="${this.uploadedAssetUrl}" style="max-width: 100px;">`);
            } else {
               // For other files, insert a link
                editorInstance.execute('insertHtml', `<a href="${this.uploadedAssetUrl}">${this.uploadedAssetUrl}</a>`);
            }
         } else {
            // Fallback if editor instance not found
            this.activeTemplate.html += `<img src="${this.uploadedAssetUrl}" style="max-width: 100px;">`;
         }
      } else {
        alert('No asset uploaded yet.');
      }
    }
  },
  watch: {
      // Watch for changes in activeTemplate.html to update the preview
      'activeTemplate.html': function(newHtml, oldHtml) {
          if (newHtml !== oldHtml) {
              this.renderBillPreview();
          }
      }
  },
   mounted() {
       // Fetch templates when the component is mounted
       this.fetchTemplates();
   }
};

