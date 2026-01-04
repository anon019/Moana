<template>
  <div class="space-y-6">
    <!-- 分类选择 -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="(category, key) in themes"
        :key="key"
        class="px-4 py-2 rounded-full text-sm font-medium transition-all"
        :class="selectedCategory === key
          ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
          : 'bg-white/80 text-gray-600 hover:bg-white hover:shadow-sm border border-gray-200'"
        @click="selectCategory(key as string)"
      >
        {{ getCategoryIcon(key as string) }} {{ category.name }}
      </button>
    </div>

    <!-- 主题卡片网格 -->
    <div v-if="currentThemes.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      <div
        v-for="theme in currentThemes"
        :key="theme.id"
        class="group relative p-4 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-105"
        :class="selectedTopic === theme.id
          ? 'bg-gradient-to-br from-purple-100 to-pink-100 border-2 border-purple-400 shadow-lg'
          : 'bg-white/80 border border-gray-200 hover:shadow-md'"
        @click="selectTheme(theme)"
      >
        <!-- 选中标记 -->
        <div
          v-if="selectedTopic === theme.id"
          class="absolute -top-2 -right-2 w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center text-white text-xs"
        >
          ✓
        </div>

        <!-- 主题名称 -->
        <h3 class="text-base font-medium text-gray-800 mb-2">{{ theme.name }}</h3>

        <!-- 子分类 -->
        <p class="text-xs text-gray-500 mb-2">{{ theme.subcategory }}</p>

        <!-- 年龄范围 -->
        <div class="flex items-center text-xs text-purple-500">
          <span>{{ formatAgeRange(theme.age_range) }}</span>
        </div>

        <!-- 关键词标签 -->
        <div class="flex flex-wrap gap-1 mt-2">
          <span
            v-for="keyword in theme.keywords?.slice(0, 2)"
            :key="keyword"
            class="px-2 py-0.5 bg-purple-50 text-purple-600 rounded-full text-xs"
          >
            {{ keyword }}
          </span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="selectedCategory" class="text-center py-12 text-gray-500">
      该分类暂无主题
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ThemeList, ThemeItem } from '@/api/create'

const props = defineProps<{
  themes: ThemeList | null
  selectedCategory: string
  selectedTopic: string
}>()

const emit = defineEmits<{
  'update:selectedCategory': [value: string]
  'update:selectedTopic': [value: string]
  'select': [theme: ThemeItem]
}>()

const currentThemes = computed(() => {
  if (!props.themes || !props.selectedCategory) return []
  return props.themes[props.selectedCategory]?.themes || []
})

function selectCategory(key: string) {
  emit('update:selectedCategory', key)
  emit('update:selectedTopic', '')
}

function selectTheme(theme: ThemeItem) {
  emit('update:selectedTopic', theme.id)
  emit('select', theme)
}

function getCategoryIcon(key: string): string {
  const icons: Record<string, string> = {
    habit: '🌟',
    cognition: '🧠',
    emotion: '💖',
    social: '👫',
    creativity: '🎨',
    nature: '🌿',
    safety: '🛡️',
    festival: '🎉'
  }
  return icons[key] || '📚'
}

function formatAgeRange(range: [number, number]): string {
  if (!range) return ''
  const [min, max] = range
  const minYears = Math.floor(min / 12)
  const maxYears = Math.floor(max / 12)
  return `${minYears}-${maxYears}岁`
}
</script>
