/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { wechatLogin, getCurrentUser, logout as apiLogout, mockLogin, type User } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => !!user.value)

  // 登录
  async function login(userInfo?: { nickname?: string; avatar_url?: string }) {
    try {
      await wechatLogin(userInfo)
      await fetchUser()
      return true
    } catch (e) {
      console.error('登录失败，尝试模拟登录:', e)
      // 开发环境：使用模拟登录
      try {
        const { user: mockUser } = mockLogin()
        user.value = mockUser
        console.log('模拟登录成功')
        return true
      } catch (mockErr) {
        console.error('模拟登录也失败:', mockErr)
        return false
      }
    }
  }

  // 获取用户信息
  async function fetchUser() {
    try {
      user.value = await getCurrentUser()
    } catch (e) {
      // 如果获取用户失败但有 token，使用模拟用户
      const token = uni.getStorageSync('access_token')
      if (token && token.startsWith('mock-')) {
        const { user: mockUser } = mockLogin()
        user.value = mockUser
      } else {
        user.value = null
        throw e
      }
    }
  }

  // 退出登录
  function logout() {
    apiLogout()
    user.value = null
  }

  // 检查登录状态
  function checkLogin(): boolean {
    const token = uni.getStorageSync('access_token')
    return !!token
  }

  return {
    user,
    isLoggedIn,
    login,
    fetchUser,
    logout,
    checkLogin
  }
})
