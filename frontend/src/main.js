import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './app.vue' // Note: Capitalized App.vue (convention)

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Correct mount point (add # selector)
app.mount('#temp-bill-app')