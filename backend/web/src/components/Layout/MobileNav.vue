<template>
  <!-- 顶部 Header -->
  <header class="lg:hidden fixed top-0 left-0 right-0 h-14 bg-paper/95 backdrop-blur-sm border-b border-bark-100 z-50">
    <div class="flex items-center justify-between h-full px-4">
      <span class="text-xl font-bold text-forest">
        童趣工坊
      </span>
      <span class="text-sm text-pencil">{{ pageTitle }}</span>
    </div>
  </header>

  <!-- 底部 TabBar -->
  <nav class="lg:hidden fixed bottom-0 left-0 right-0 h-20 bg-paper border-t border-bark-100 z-50 pb-safe">
    <div class="grid grid-cols-4 h-full">
      <router-link
        v-for="item in tabItems"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center justify-center text-xs transition-all"
        :class="isActive(item.path) ? 'text-forest' : 'text-eraser'"
      >
        <span
          class="text-2xl mb-1 transition-transform"
          :class="isActive(item.path) ? 'scale-110' : ''"
        >{{ item.icon }}</span>
        <span :class="isActive(item.path) ? 'font-medium' : ''">{{ item.name }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const tabItems = [
  { path: '/dashboard', name: '首页', icon: '🏠' },
  { path: '/create', name: '创作', icon: '✨' },
  { path: '/library', name: '内容', icon: '📚' },
  { path: '/settings', name: '设置', icon: '⚙️' },
]

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': '首页',
    '/create': '创作中心',
    '/children': '孩子管理',
    '/library': '内容库',
    '/favorites': '收藏',
    '/report': '学习报告',
    '/settings': '设置',
  }
  return titles[route.path] || ''
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
