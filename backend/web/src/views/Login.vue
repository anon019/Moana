<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
    <div class="w-full max-w-sm">
      <div class="card">
        <!-- Logo -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 mx-auto bg-primary-500 rounded-2xl flex items-center justify-center mb-4">
            <span class="text-3xl">🐠</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900">Moana</h1>
          <p class="text-gray-500 mt-1">家长管理端</p>
        </div>

        <!-- 表单 -->
        <form @submit.prevent="handleLogin">
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">访问密码</label>
            <input
              v-model="password"
              type="password"
              class="input"
              placeholder="请输入密码"
              :class="{ 'border-red-500': error }"
            />
            <p v-if="error" class="mt-2 text-sm text-red-500">{{ error }}</p>
          </div>

          <button
            type="submit"
            class="btn btn-primary w-full"
            :disabled="loading"
          >
            {{ loading ? '登录中...' : '进入管理' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    const success = await userStore.login(password.value)
    if (success) {
      router.push('/dashboard')
    } else {
      error.value = '密码错误'
    }
  } catch (e) {
    error.value = '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
