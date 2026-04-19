import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

const app = createApp(App)

// 🛡️ Le filet de sécurité Frontend
app.config.errorHandler = (err, instance, info) => {
    console.error("💥 [VUE CRASH FATAL]", err)
    console.error("📍 [INFO COMPOSANT]", info)
    // Optionnel : Tu pourrais même faire un fetch() ici pour envoyer l'erreur à ton backend !
}

// Intercepte les promesses non gérées (ex: un fetch qui plante silencieusement)
window.addEventListener('unhandledrejection', event => {
    console.error("🌐 [PROMISE NON GÉRÉE]", event.reason);
});

app.mount('#app')