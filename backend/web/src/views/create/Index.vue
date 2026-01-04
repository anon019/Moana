<template>
  <div class="page-container">
    <!-- 装饰背景元素 -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="deco-blob w-96 h-96 from-coral-200 to-coral-100 -top-48 -right-48 animate-float" />
      <div class="deco-blob w-80 h-80 from-sky-200 to-sky-100 top-1/3 -left-40 animate-float" style="animation-delay: -2s" />
      <div class="deco-blob w-64 h-64 from-sage-200 to-sage-100 bottom-20 right-1/4 animate-float" style="animation-delay: -4s" />
    </div>

    <div class="page-content relative">
      <!-- 页面头部 -->
      <header class="mb-12 animate-fade-in">
        <div class="flex items-start justify-between">
          <div>
            <h1 class="page-title flex items-center gap-3">
              <span class="inline-block w-12 h-12 bg-forest-100 rounded-xl flex items-center justify-center">
                <svg class="w-7 h-7 text-forest" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
                </svg>
              </span>
              创作工坊
            </h1>
            <p class="page-subtitle text-lg mt-3">
              为宝贝定制专属的故事、音乐与视频
            </p>
          </div>

          <!-- 当前孩子信息 -->
          <div v-if="childStore.currentChild" class="hidden sm:flex items-center gap-3 px-4 py-2 bg-paper rounded-xl border border-bark-100">
            <div class="w-10 h-10 bg-forest-100 rounded-lg flex items-center justify-center text-lg">
              {{ childStore.currentChild.name?.charAt(0) || '宝' }}
            </div>
            <div class="text-sm">
              <p class="font-medium text-ink">{{ childStore.currentChild.name }}</p>
              <p class="text-eraser">{{ childStore.currentChild.current_stage || '幼儿' }}</p>
            </div>
          </div>
        </div>

        <!-- 分隔装饰线 -->
        <div class="deco-line mt-8 w-32" />
      </header>

      <!-- 孩子提示 -->
      <div v-if="!childStore.currentChild" class="mb-8 p-5 bg-bark-50 border-2 border-dashed border-bark-200 rounded-2xl animate-fade-in">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-bark-100 rounded-xl flex items-center justify-center shrink-0">
            <svg class="w-6 h-6 text-bark" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-bark-700">还没有添加宝贝信息</p>
            <p class="text-sm text-bark-500 mt-1">
              <router-link to="/children/add" class="text-forest font-medium hover:underline">添加孩子</router-link>
              后可以获得更个性化的创作体验
            </p>
          </div>
        </div>
      </div>

      <!-- 创作类型卡片 -->
      <section class="mb-16">
        <h2 class="section-title mb-6">
          <span class="w-1.5 h-6 bg-forest rounded-full" />
          选择创作类型
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 animate-stagger">
          <!-- 绘本创作 -->
          <router-link to="/create/picture-book" class="create-card create-card-book group">
            <div class="relative z-10 flex flex-col h-full min-h-[180px]">
              <!-- 图标 -->
              <div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>

              <!-- 内容 -->
              <h3 class="text-2xl font-bold mb-2">绘本故事</h3>
              <p class="text-white/80 mb-4 flex-grow">
                AI 智能生成精美插画故事书，陪伴宝贝探索奇妙世界
              </p>

              <!-- 标签 -->
              <div class="flex items-center gap-2 text-sm">
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">4步完成</span>
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">多种风格</span>
              </div>
            </div>

            <!-- 装饰图形 -->
            <div class="absolute -right-6 -bottom-6 w-32 h-32 border-[3px] border-white/20 rounded-2xl rotate-12 transition-transform group-hover:rotate-6" />
            <div class="absolute right-8 bottom-8 w-16 h-16 border-[3px] border-white/10 rounded-xl -rotate-6 transition-transform group-hover:rotate-0" />
          </router-link>

          <!-- 儿歌创作 -->
          <router-link to="/create/nursery-rhyme" class="create-card create-card-song group">
            <div class="relative z-10 flex flex-col h-full min-h-[180px]">
              <div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </div>

              <h3 class="text-2xl font-bold mb-2">原创儿歌</h3>
              <p class="text-white/80 mb-4 flex-grow">
                AI 作词作曲，为宝贝创作朗朗上口的专属音乐
              </p>

              <div class="flex items-center gap-2 text-sm">
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">Suno AI</span>
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">多种曲风</span>
              </div>
            </div>

            <div class="absolute -right-6 -bottom-6 w-32 h-32 border-[3px] border-white/20 rounded-full transition-transform group-hover:scale-110" />
            <div class="absolute right-10 bottom-10 w-12 h-12 border-[3px] border-white/10 rounded-full" />
          </router-link>

          <!-- 视频创作 -->
          <router-link to="/create/video" class="create-card create-card-video group">
            <div class="relative z-10 flex flex-col h-full min-h-[180px]">
              <div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>

              <h3 class="text-2xl font-bold mb-2">创意视频</h3>
              <p class="text-white/80 mb-4 flex-grow">
                AI 生成精彩动画短片，让故事和画面动起来
              </p>

              <div class="flex items-center gap-2 text-sm">
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">VEO 生成</span>
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">高清画质</span>
              </div>
            </div>

            <div class="absolute -right-4 -bottom-4 w-28 h-20 border-[3px] border-white/20 rounded-xl transition-transform group-hover:translate-x-2" />
            <div class="absolute right-6 bottom-12 w-20 h-14 border-[3px] border-white/10 rounded-lg" />
          </router-link>

          <!-- 智能创作 -->
          <router-link to="/create/smart" class="create-card create-card-smart group">
            <div class="relative z-10 flex flex-col h-full min-h-[180px]">
              <div class="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>

              <h3 class="text-2xl font-bold mb-2">智能创作</h3>
              <p class="text-white/80 mb-4 flex-grow">
                用自然语言描述想法，AI 自动选择最佳创作方式
              </p>

              <div class="flex items-center gap-2 text-sm">
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">一键生成</span>
                <span class="px-2.5 py-1 bg-white/20 rounded-lg">智能推荐</span>
              </div>
            </div>

            <div class="absolute -right-8 -bottom-8 w-36 h-36 opacity-20">
              <svg viewBox="0 0 100 100" class="w-full h-full">
                <path d="M50 10 L90 50 L50 90 L10 50 Z" fill="none" stroke="currentColor" stroke-width="3" class="transition-transform group-hover:scale-110 origin-center" />
                <path d="M50 25 L75 50 L50 75 L25 50 Z" fill="none" stroke="currentColor" stroke-width="2" />
              </svg>
            </div>
          </router-link>
        </div>
      </section>

      <!-- 最近创作 -->
      <section class="animate-fade-in" style="animation-delay: 200ms">
        <div class="flex items-center justify-between mb-6">
          <h2 class="section-title">
            <span class="w-1.5 h-6 bg-coral rounded-full" />
            最近作品
          </h2>
          <router-link to="/library" class="text-forest hover:text-forest-600 text-sm font-medium flex items-center gap-1 group">
            查看全部
            <svg class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>

        <div v-if="recentContents.length" class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <router-link
            v-for="content in recentContents"
            :key="content.id"
            :to="`/play/${content.content_type}/${content.id}`"
            class="card card-interactive overflow-hidden group"
          >
            <!-- 封面 -->
            <div class="aspect-[4/3] bg-canvas flex items-center justify-center relative overflow-hidden">
              <div :class="[
                'w-16 h-16 rounded-2xl flex items-center justify-center',
                getContentColorClass(content.content_type)
              ]">
                <component :is="getContentIcon(content.content_type)" class="w-8 h-8 text-white" />
              </div>
              <!-- 悬浮播放按钮 -->
              <div class="absolute inset-0 bg-forest/0 group-hover:bg-forest/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg">
                  <svg class="w-5 h-5 text-forest ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
            </div>
            <!-- 信息 -->
            <div class="p-4">
              <p class="font-medium text-ink truncate">{{ content.title }}</p>
              <p class="text-xs text-eraser mt-1">{{ formatDate(content.created_at) }}</p>
            </div>
          </router-link>
        </div>

        <!-- 空状态 -->
        <div v-else class="text-center py-16 bg-paper rounded-2xl border-2 border-dashed border-bark-200">
          <div class="w-16 h-16 bg-canvas rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-eraser" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <p class="text-pencil font-medium">还没有创作内容</p>
          <p class="text-eraser text-sm mt-1">选择上方任意一种方式开始创作吧</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useChildStore } from '@/stores/child'
import { getContentList } from '@/api/content'
import type { Content } from '@/api/types'

const childStore = useChildStore()
const recentContents = ref<Content[]>([])

onMounted(async () => {
  await childStore.fetchChildren()

  try {
    const res = await getContentList({ limit: 4 })
    recentContents.value = res.items
  } catch (e) {
    console.error('获取最近内容失败:', e)
  }
})

// 内容类型图标组件
const BookIcon = {
  render() {
    return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', class: 'w-8 h-8' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
    ])
  }
}

const MusicIcon = {
  render() {
    return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', class: 'w-8 h-8' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5', d: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3' })
    ])
  }
}

const VideoIcon = {
  render() {
    return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', class: 'w-8 h-8' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5', d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
    ])
  }
}

function getContentIcon(type?: string) {
  const icons: Record<string, any> = {
    picture_book: BookIcon,
    nursery_rhyme: MusicIcon,
    video: VideoIcon
  }
  return icons[type || ''] || BookIcon
}

function getContentColorClass(type?: string): string {
  const colors: Record<string, string> = {
    picture_book: 'bg-coral',
    nursery_rhyme: 'bg-sky',
    video: 'bg-sage'
  }
  return colors[type || ''] || 'bg-bark'
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
</script>
