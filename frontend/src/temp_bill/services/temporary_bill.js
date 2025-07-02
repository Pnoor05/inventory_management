import { createApp } from 'vue';
import TemplateManager from './TemplateManager.vue';

const app = createApp(TemplateManager);
app.mount('temperary-bill-app'); // Assuming the HTML element to mount on has the id 'app'
