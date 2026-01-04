<template>
  <div class="min-h-screen bg-cream">
    <div class="max-w-6xl mx-auto px-4 py-8">
      <!-- 标题和搜索 -->
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-text-primary flex items-center gap-2">
          <span class="text-3xl">📚</span>
          <span>内容库</span>
        </h1>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索标题..."
            class="pl-10 pr-4 py-2.5 bg-white rounded-full border-2 border-gray-100 focus:border-honey focus:outline-none w-64 text-sm"
          />
          <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-secondary">🔍</span>
        </div>
      </div>

      <!-- 类型筛选 -->
      <div class="flex gap-3 mb-6">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="setFilter(tab.value)"
          class="relative px-5 py-2.5 rounded-full font-medium text-sm transition-all"
          :class="getTabClass(tab.value)"
        >
          <span v-if="tab.icon" class="mr-1.5">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
          <span
            v-if="getCount(tab.value) > 0"
            class="ml-2 px-2 py-0.5 text-xs rounded-full"
            :class="getCountClass(tab.value)"
          >
            {{ getCount(tab.value) }}
          </span>
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="text-center">
          <div class="w-12 h-12 border-4 border-honey border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p class="mt-4 text-text-secondary">加载中...</p>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredItems.length === 0" class="text-center py-16 bg-white rounded-2xl">
        <div class="text-7xl mb-4">📭</div>
        <p class="text-text-primary text-lg font-medium">还没有内容</p>
        <p class="text-text-secondary mt-2">去小程序创作属于宝贝的专属内容吧</p>
      </div>

      <!-- 内容网格 -->
      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        <ContentCard
          v-for="item in filteredItems"
          :key="item.id"
          :content="item"
          @play="handlePlay(item)"
          @delete="handleDelete(item)"
        />
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore && !loading && filteredItems.length > 0" class="text-center mt-8">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="px-8 py-3 bg-honey text-white font-medium rounded-full hover:bg-honey-dark transition-colors disabled:opacity-50"
        >
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ContentCard from '@/components/ContentCard.vue'
import { getContentList, deleteContent } from '@/api/content'
import type { Content } from '@/api/types'

const router = useRouter()
const route = useRoute()

type ContentType = '' | 'picture_book' | 'nursery_rhyme' | 'video'

const tabs = [
  { value: '' as ContentType, label: '全部', icon: '' },
  { value: 'picture_book' as ContentType, label: '绘本', icon: '📖' },
  { value: 'nursery_rhyme' as ContentType, label: '儿歌', icon: '🎵' },
  { value: 'video' as ContentType, label: '视频', icon: '🎬' },
]

const currentType = ref<ContentType>((route.query.type as ContentType) || '')
const searchQuery = ref('')
const items = ref<Content[]>([])
const allItems = ref<Content[]>([]) // 用于统计
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(false)
const offset = ref(0)
const limit = 20

// 获取各类型数量
function getCount(type: ContentType): number {
  if (type === '') return allItems.value.length
  return allItems.value.filter(i => (i as any).content_type === type).length
}

const filteredItems = computed(() => {
  if (!searchQuery.value) return items.value
  return items.value.filter(item =>
    item.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

function getTabClass(type: ContentType): string {
  const isActive = currentType.value === type
  if (isActive) {
    if (type === 'picture_book') return 'bg-book text-white shadow-lg'
    if (type === 'nursery_rhyme') return 'bg-song text-white shadow-lg'
    if (type === 'video') return 'bg-video text-white shadow-lg'
    return 'bg-honey text-white shadow-lg'
  }
  return 'bg-white text-text-secondary hover:bg-gray-50 border border-gray-200'
}

function getCountClass(type: ContentType): string {
  const isActive = currentType.value === type
  if (isActive) return 'bg-white/30 text-white'
  if (type === 'picture_book') return 'bg-book-light text-book-dark'
  if (type === 'nursery_rhyme') return 'bg-song-light text-song-dark'
  if (type === 'video') return 'bg-video-light text-video-dark'
  return 'bg-gray-100 text-text-secondary'
}

function setFilter(type: ContentType) {
  currentType.value = type
  router.replace({ query: type ? { type } : {} })
}

async function fetchItems(reset = false) {
  if (reset) {
    offset.value = 0
    items.value = []
  }

  loading.value = reset
  loadingMore.value = !reset

  try {
    const res = await getContentList({
      type: currentType.value || undefined,
      limit,
      offset: offset.value,
    })
    items.value = reset ? res.items : [...items.value, ...res.items]
    hasMore.value = res.has_more
    offset.value += res.items.length

    // 首次加载时获取全部统计
    if (reset && !currentType.value) {
      allItems.value = res.items
      // 如果还有更多，继续获取用于统计
      if (res.has_more) {
        const allRes = await getContentList({ limit: 100 })
        allItems.value = allRes.items
      }
    }
  } catch (e) {
    console.error('获取内容列表失败:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  fetchItems(false)
}

function handlePlay(item: Content) {
  const type = (item as any).content_type || 'video'
  router.push(`/play/${type}/${item.id}`)
}

async function handleDelete(item: Content) {
  if (!confirm(`确定删除「${item.title}」吗？`)) return

  try {
    await deleteContent(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
    allItems.value = allItems.value.filter(i => i.id !== item.id)
  } catch (e) {
    console.error('删除失败:', e)
    alert('删除失败')
  }
}

watch(currentType, () => fetchItems(true))

onMounted(() => fetchItems(true))
</script>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
