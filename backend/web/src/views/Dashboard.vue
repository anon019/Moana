<template>
  <div class="min-h-screen bg-cream">
    <div class="max-w-6xl mx-auto px-4 py-8">
      <!-- 欢迎区域 -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-text-primary flex items-center gap-2">
          <span class="text-3xl">👋</span>
          <span>欢迎回来！</span>
        </h1>
        <p class="text-text-secondary mt-1">今天想给宝贝看点什么呢？</p>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-3 gap-4 mb-8">
        <!-- 绘本统计 -->
        <div class="bg-book-light rounded-2xl p-6 border-2 border-book/20 hover:border-book/40 transition-colors cursor-pointer" @click="goToLibrary('picture_book')">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-4xl font-bold text-book-dark">{{ stats.books }}</p>
              <p class="text-text-secondary mt-1">本绘本</p>
            </div>
            <span class="text-5xl">📖</span>
          </div>
        </div>

        <!-- 儿歌统计 -->
        <div class="bg-song-light rounded-2xl p-6 border-2 border-song/20 hover:border-song/40 transition-colors cursor-pointer" @click="goToLibrary('nursery_rhyme')">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-4xl font-bold text-song-dark">{{ stats.songs }}</p>
              <p class="text-text-secondary mt-1">首儿歌</p>
            </div>
            <span class="text-5xl">🎵</span>
          </div>
        </div>

        <!-- 视频统计 -->
        <div class="bg-video-light rounded-2xl p-6 border-2 border-video/20 hover:border-video/40 transition-colors cursor-pointer" @click="goToLibrary('video')">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-4xl font-bold text-video-dark">{{ stats.videos }}</p>
              <p class="text-text-secondary mt-1">个视频</p>
            </div>
            <span class="text-5xl">🎬</span>
          </div>
        </div>
      </div>

      <!-- 最新创作 -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-text-primary flex items-center gap-2">
            <span>✨</span>
            <span>最新创作</span>
          </h2>
          <router-link to="/library" class="text-honey hover:text-honey-dark transition-colors text-sm font-medium">
            查看全部 →
          </router-link>
        </div>

        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="w-10 h-10 border-4 border-honey border-t-transparent rounded-full animate-spin"></div>
        </div>

        <div v-else-if="recentItems.length === 0" class="text-center py-12 bg-white rounded-2xl">
          <div class="text-6xl mb-4">📭</div>
          <p class="text-text-secondary">还没有内容哦</p>
          <p class="text-text-light text-sm mt-1">去小程序创作第一个作品吧</p>
        </div>

        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <ContentCard
            v-for="item in recentItems"
            :key="item.id"
            :content="item"
            @play="handlePlay(item)"
            @delete="handleDelete(item)"
          />
        </div>
      </div>

      <!-- 快速入口 -->
      <div>
        <h2 class="text-xl font-bold text-text-primary flex items-center gap-2 mb-4">
          <span>🎯</span>
          <span>快速入口</span>
        </h2>
        <div class="grid grid-cols-3 gap-4">
          <router-link
            to="/library?type=picture_book"
            class="flex items-center gap-3 bg-white rounded-2xl p-5 shadow-card hover:shadow-card-hover transition-all hover:-translate-y-1 border-l-4 border-book"
          >
            <span class="text-3xl">📖</span>
            <span class="font-medium text-text-primary">全部绘本</span>
          </router-link>
          <router-link
            to="/library?type=nursery_rhyme"
            class="flex items-center gap-3 bg-white rounded-2xl p-5 shadow-card hover:shadow-card-hover transition-all hover:-translate-y-1 border-l-4 border-song"
          >
            <span class="text-3xl">🎵</span>
            <span class="font-medium text-text-primary">全部儿歌</span>
          </router-link>
          <router-link
            to="/library?type=video"
            class="flex items-center gap-3 bg-white rounded-2xl p-5 shadow-card hover:shadow-card-hover transition-all hover:-translate-y-1 border-l-4 border-video"
          >
            <span class="text-3xl">🎬</span>
            <span class="font-medium text-text-primary">全部视频</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ContentCard from '@/components/ContentCard.vue'
import { getContentList, deleteContent } from '@/api/content'
import type { Content } from '@/api/types'

const router = useRouter()

const items = ref<Content[]>([])
const loading = ref(true)
const stats = ref({ books: 0, songs: 0, videos: 0 })

// 最新内容（最多显示8个）
const recentItems = computed(() => items.value.slice(0, 8))

async function fetchItems() {
  loading.value = true
  try {
    // 获取内容统计
    const [books, songs, videos] = await Promise.all([
      getContentList({ type: 'picture_book', limit: 1 }),
      getContentList({ type: 'nursery_rhyme', limit: 1 }),
      getContentList({ type: 'video', limit: 1 }),
    ])
    stats.value = {
      books: books.total,
      songs: songs.total,
      videos: videos.total,
    }

    // 获取最新内容
    const res = await getContentList({ limit: 8 })
    items.value = res.items
  } catch (e) {
    console.error('获取内容失败:', e)
  } finally {
    loading.value = false
  }
}

function goToLibrary(type: string) {
  router.push(`/library?type=${type}`)
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
  } catch (e) {
    console.error('删除失败:', e)
    alert('删除失败')
  }
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
