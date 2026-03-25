import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

export function createApp() {
  const app = createSSRApp(App)

  // 配置 Pinia
  const pinia = createPinia()
  app.use(pinia)

  return {
    app,
  }
}
