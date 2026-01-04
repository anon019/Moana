import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, logout as apiLogout, verifyPassword } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(!!localStorage.getItem('admin_token'))

  async function login(password: string): Promise<boolean> {
    if (!verifyPassword(password)) {
      return false
    }

    try {
      const res = await apiLogin()
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      localStorage.setItem('admin_token', 'true')
      isLoggedIn.value = true
      return true
    } catch {
      return false
    }
  }

  function logout() {
    apiLogout()
    isLoggedIn.value = false
  }

  return {
    isLoggedIn,
    login,
    logout
  }
})
