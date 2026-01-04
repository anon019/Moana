<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">我的收藏</h1>
    </div>

    <!-- 筛选栏 -->
    <div class="flex flex-wrap gap-4">
      <div class="flex bg-gray-100 rounded-lg p-1">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="currentType = tab.value"
          class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
          :class="currentType === tab.value ? 'bg-white shadow text-primary-600' : 'text-gray-600 hover:text-gray-900'"
        >
          {{ tab.label }}
        </button>
      </div>

      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索标题..."
        class="input max-w-xs"
      />
    </div>

    <!-- 内容网格 -->
    <div v-if="loading" class="text-center py-12 text-gray-500">
      加载中...
    </div>

    <div v-else-if="filteredItems.length === 0" class="text-center py-12">
      <div class="text-6xl mb-4">&#x2764;</div>
      <p class="text-gray-500">还没有收藏内容</p>
      <p class="text-gray-400 text-sm mt-2">在内容播放页点击心形按钮添加收藏</p>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="card p-0 overflow-hidden hover:shadow-md transition-shadow cursor-pointer group"
        @click="handlePlay(item)"
      >
        <!-- 封面图 -->
        <div class="relative aspect-video bg-gray-100">
          <img
            v-if="getCover(item)"
            :src="getCover(item)"
            :alt="item.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-4xl">
            {{ getTypeIcon(item) }}
          </div>

          <!-- 类型角标 -->
          <span class="absolute top-2 left-2 px-2 py-1 text-xs font-medium rounded-full bg-black/50 text-white">
            {{ getTypeLabel(item) }}
          </span>

          <!-- 悬浮操作 -->
          <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
            <button
              @click.stop="handlePlay(item)"
              class="w-12 h-12 rounded-full bg-white text-gray-900 flex items-center justify-center hover:scale-110 transition-transform"
              title="播放"
            >
              <span class="text-xl">&#9654;</span>
            </button>
            <button
              @click.stop="handleUnfavorite(item)"
              class="w-10 h-10 rounded-full bg-red-500 text-white flex items-center justify-center hover:scale-110 transition-transform"
              title="取消收藏"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 信息 -->
        <div class="p-4">
          <h3 class="font-medium text-gray-900 truncate">{{ item.title }}</h3>
          <p class="text-sm text-gray-500 mt-1">{{ formatDate(item.created_at) }}</p>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore && !loading && filteredItems.length > 0" class="text-center">
      <button @click="loadMore" class="btn btn-primary" :disabled="loadingMore">
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFavorites, removeFavorite } from '@/api/favorite'
import type { Content } from '@/api/types'

const router = useRouter()

type ContentType = '' | 'picture_book' | 'nursery_rhyme' | 'video'

const tabs: Array<{ value: ContentType; label: string }> = [
  { value: '', label: '全部' },
  { value: 'picture_book', label: '绘本' },
  { value: 'nursery_rhyme', label: '儿歌' },
  { value: 'video', label: '视频' },
]

const currentType = ref<ContentType>('')
const searchQuery = ref('')
const items = ref<Content[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(false)
const offset = ref(0)
const limit = 20

// 获取内容类型
function getContentType(item: Content): ContentType {
  if ('pages' in item) return 'picture_book'
  if ('lyrics' in item) return 'nursery_rhyme'
  return 'video'
}

// 按类型和搜索过滤
const filteredItems = computed(() => {
  let result = items.value

  // 按类型筛选
  if (currentType.value) {
    result = result.filter(item => getContentType(item) === currentType.value)
  }

  // 按标题搜索
  if (searchQuery.value) {
    result = result.filter(item =>
      item.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  return result
})

// 获取封面
function getCover(item: Content): string | undefined {
  const c = item as any
  return c.cover_url || c.cover_thumb_url || c.suno_cover_url
}

// 获取类型图标
function getTypeIcon(item: Content): string {
  const icons: Record<ContentType, string> = {
    '': '',
    picture_book: '\uD83D\uDCD6',
    nursery_rhyme: '\uD83C\uDFB5',
    video: '\uD83C\uDFAC'
  }
  return icons[getContentType(item)]
}

// 获取类型标签
function getTypeLabel(item: Content): string {
  const labels: Record<ContentType, string> = {
    '': '全部',
    picture_book: '绘本',
    nursery_rhyme: '儿歌',
    video: '视频'
  }
  return labels[getContentType(item)]
}

// 格式化日期（香港时间）
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const hkDate = new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Hong_Kong' }))
  return `${hkDate.getMonth() + 1}月${hkDate.getDate()}日`
}

async function fetchItems(reset = false) {
  if (reset) {
    offset.value = 0
    items.value = []
  }

  loading.value = reset
  loadingMore.value = !reset

  try {
    const res = await getFavorites({
      limit,
      offset: offset.value,
    })
    items.value = reset ? res.items : [...items.value, ...res.items]
    hasMore.value = res.has_more
    offset.value += res.items.length
  } catch (e) {
    console.error('获取收藏列表失败:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  fetchItems(false)
}

function handlePlay(item: Content) {
  const type = 'pages' in item ? 'picture-book' : 'lyrics' in item ? 'nursery-rhyme' : 'video'
  router.push(`/play/${type}/${item.id}`)
}

async function handleUnfavorite(item: Content) {
  if (!confirm(`确定取消收藏「${item.title}」吗？`)) return

  try {
    await removeFavorite(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
  } catch (e) {
    console.error('取消收藏失败:', e)
    alert('取消收藏失败')
  }
}

// 初始加载
onMounted(() => fetchItems(true))
</script>
