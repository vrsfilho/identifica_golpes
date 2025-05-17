import { createApp } from 'vue'
import App from './App.vue'

// Cria a instância do aplicativo Vue
const app = createApp(App)

// Monta o aplicativo no elemento com id="app" no index.html
app.mount('#app')

// Opcional: Configurações globais, plugins, etc. podem vir aqui
// Ex: app.use(router).use(store).mount('#app')