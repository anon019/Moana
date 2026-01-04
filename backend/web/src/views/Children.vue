<template>
  <div class="space-y-6">
    <!-- 页面头部 -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">孩子管理</h1>
      <router-link to="/children/add" class="btn btn-primary">
        + 添加孩子
      </router-link>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-2">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="childStore.children.length === 0" class="card text-center py-12">
      <div class="text-6xl mb-4">👶</div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">还没有添加孩子</h3>
      <p class="text-gray-500 mb-4">添加孩子后，您可以为他们管理学习内容和时间</p>
      <router-link to="/children/add" class="btn btn-primary">
        + 添加孩子
      </router-link>
    </div>

    <!-- 孩子列表 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <router-link
        v-for="child in childStore.children"
        :key="child.id"
        :to="`/children/${child.id}`"
        class="card hover:shadow-md transition-shadow cursor-pointer relative"
      >
        <!-- 当前徽章 -->
        <span
          v-if="childStore.currentChild?.id === child.id"
          class="absolute top-3 right-3 px-2 py-1 bg-primary-100 text-primary-600 text-xs font-medium rounded-full"
        >
          当前
        </span>

        <div class="flex items-center">
          <!-- 头像 -->
          <div
            class="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold"
            :class="childStore.currentChild?.id === child.id ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600'"
          >
            {{ child.name.charAt(0) }}
          </div>

          <!-- 信息 -->
          <div class="ml-4 flex-1 min-w-0">
            <h3 class="text-lg font-medium text-gray-900 truncate">{{ child.name }}</h3>
            <p class="text-sm text-gray-500">{{ calculateAge(child.birth_date) }}</p>
          </div>
        </div>

        <!-- 兴趣标签 -->
        <div v-if="child.interests && child.interests.length > 0" class="mt-4 flex flex-wrap gap-2">
          <span
            v-for="interest in child.interests.slice(0, 3)"
            :key="interest"
            class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
          >
            {{ interest }}
          </span>
          <span
            v-if="child.interests.length > 3"
            class="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full"
          >
            +{{ child.interests.length - 3 }}
          </span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChildStore } from '@/stores/child'

const childStore = useChildStore()
const loading = ref(true)

// 计算年龄
function calculateAge(birthDate: string): string {
  if (!birthDate) return ''
  const birth = new Date(birthDate)
  const now = new Date()
  const months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
  if (months <= 0) return '不足1个月'
  const years = Math.floor(months / 12)
  const remainMonths = months % 12
  if (years === 0) return `${remainMonths}个月`
  if (remainMonths === 0) return `${years}岁`
  return `${years}岁${remainMonths}个月`
}

onMounted(async () => {
  try {
    await childStore.fetchChildren()
  } finally {
    loading.value = false
  }
})
</script>
