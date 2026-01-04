<template>
  <div
    class="group relative bg-white rounded-2xl overflow-hidden shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 cursor-pointer"
    :class="borderClass"
    @click="$emit('play')"
  >
    <!-- 左侧类型色条 -->
    <div class="absolute left-0 top-0 bottom-0 w-1" :class="barClass"></div>

    <!-- 封面图 -->
    <div class="relative aspect-[4/3] bg-gray-100 overflow-hidden">
      <img
        v-if="cover"
        :src="cover"
        :alt="content.title"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-5xl" :class="bgLightClass">
        {{ typeIcon }}
      </div>

      <!-- 类型标签 -->
      <div class="absolute top-3 left-3">
        <span class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full text-white" :class="bgClass">
          <span>{{ typeIcon }}</span>
          <span>{{ typeLabel }}</span>
        </span>
      </div>

      <!-- 悬浮操作层 -->
      <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
        <button
          @click.stop="$emit('play')"
          class="w-14 h-14 rounded-full bg-white text-gray-900 flex items-center justify-center hover:scale-110 transition-transform shadow-lg"
          title="播放"
        >
          <svg class="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </button>
        <button
          @click.stop="$emit('delete')"
          class="w-11 h-11 rounded-full bg-red-500 text-white flex items-center justify-center hover:scale-110 transition-transform shadow-lg"
          title="删除"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 信息区 -->
    <div class="p-4">
      <h3 class="font-semibold text-text-primary truncate text-base">{{ content.title }}</h3>
      <div class="flex items-center justify-between mt-2">
        <span class="text-sm text-text-secondary">{{ formatDate(content.created_at) }}</span>
        <button
          @click.stop="$emit('favorite')"
          class="text-xl hover:scale-125 transition-transform"
          title="收藏"
        >
          ❤️
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Content } from '@/api/types'

const props = defineProps<{
  content: Content
}>()

defineEmits<{
  play: []
  delete: []
  favorite: []
}>()

const contentType = computed(() => {
  return (props.content as any).content_type || 'video'
})

const cover = computed(() => {
  const c = props.content as any
  return c.cover_url || c.cover_thumb_url || c.suno_cover_url
})

const typeIcon = computed(() => {
  const icons: Record<string, string> = {
    picture_book: '📖',
    nursery_rhyme: '🎵',
    video: '🎬'
  }
  return icons[contentType.value] || '🎬'
})

const typeLabel = computed(() => {
  const labels: Record<string, string> = {
    picture_book: '绘本',
    nursery_rhyme: '儿歌',
    video: '视频'
  }
  return labels[contentType.value] || '视频'
})

// 类型对应的样式类
const bgClass = computed(() => {
  const classes: Record<string, string> = {
    picture_book: 'bg-book',
    nursery_rhyme: 'bg-song',
    video: 'bg-video'
  }
  return classes[contentType.value] || 'bg-video'
})

const bgLightClass = computed(() => {
  const classes: Record<string, string> = {
    picture_book: 'bg-book-light',
    nursery_rhyme: 'bg-song-light',
    video: 'bg-video-light'
  }
  return classes[contentType.value] || 'bg-video-light'
})

const barClass = computed(() => {
  const classes: Record<string, string> = {
    picture_book: 'bg-book',
    nursery_rhyme: 'bg-song',
    video: 'bg-video'
  }
  return classes[contentType.value] || 'bg-video'
})

const borderClass = computed(() => {
  const classes: Record<string, string> = {
    picture_book: 'ring-1 ring-book/30',
    nursery_rhyme: 'ring-1 ring-song/30',
    video: 'ring-1 ring-video/30'
  }
  return classes[contentType.value] || 'ring-1 ring-video/30'
})

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const hkDate = new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Hong_Kong' }))
  return `${hkDate.getMonth() + 1}月${hkDate.getDate()}日`
}
</script>
