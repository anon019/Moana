<template>
  <div class="page-container">
    <div class="page-content">
      <h1 class="page-title mb-8">设置</h1>

      <div class="space-y-6">
        <!-- 账号状态 -->
        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-ink">账号状态</h2>
              <p class="text-sm text-pencil mt-1">家长管理员</p>
            </div>
            <div class="flex items-center gap-2 px-3 py-1.5 bg-forest-50 rounded-lg">
              <span class="w-2 h-2 rounded-full bg-forest animate-pulse" />
              <span class="text-sm text-forest font-medium">已登录</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex flex-col gap-4">
          <button
            class="btn btn-primary w-full flex items-center justify-center gap-2"
            @click="handleLogout"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            退出登录
          </button>
        </div>

        <!-- 关于 -->
        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-ink">关于</h2>
              <p class="text-sm text-pencil mt-1">童趣工坊 · 家长管理端</p>
            </div>
            <span class="text-sm text-eraser bg-canvas px-3 py-1 rounded-lg">v1.0.0</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// userStore 用于退出登录

function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    userStore.logout()
    router.push('/login')
  }
}
</script>
