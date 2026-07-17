import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import client from './api/client'
import './assets/main.css'

async function boot() {
  // Hosted demo build: run entirely client-side against an in-memory mock API.
  if (import.meta.env.VITE_DEMO === '1') {
    const { mockAdapter } = await import('./api/mock.js')
    client.defaults.adapter = mockAdapter
    if (!localStorage.getItem('bondly_token')) {
      localStorage.setItem('bondly_token', 'demo')
    }
  }

  const app = createApp(App)
  app.use(createPinia())
  app.use(router)
  app.mount('#app')
}

boot()
