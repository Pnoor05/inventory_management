export default {
    setup() {
        // Vue and Pinia are already available globally
        const { createApp } = window.Vue;
        const { createPinia } = window.Pinia;

        // Import components using dynamic imports
        Promise.all([
            import('./components/BillEditor.vue'),
            import('./store/index.js')
        ]).then(([BillEditor, storeModule]) => {
            const app = createApp(BillEditor.default);
            const pinia = createPinia();

            app.use(pinia);

            // Initialize store
            const billStore = storeModule.useBillStore();

            // Handle bill loading
            const urlParams = new URLSearchParams(window.location.search);
            const billId = urlParams.get('id') || window.location.pathname.split('/').pop();

            if (billId && billId !== 'new') {
                billStore.loadBill(billId);
            } else {
                billStore.createNewBill();
            }

            app.mount('#temp-bill-app');
        }).catch(error => {
            console.error('Failed to load components:', error);
        });
    }
} 