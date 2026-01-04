<template>
  <div class="player-picture-book h-full flex flex-col">
    <!-- 顶部导航栏 -->
    <div class="flex items-center justify-between px-4 py-3 bg-black/20">
      <button
        @click="$emit('back')"
        class="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span>返回</span>
      </button>
      <span class="text-white/80 font-medium">
        {{ currentPageIndex + 1 }} / {{ pages.length }}
      </span>
      <div class="w-16"></div>
    </div>

    <!-- 主要内容区 -->
    <div class="flex-1 flex flex-col items-center justify-center p-4 md:p-8 overflow-hidden">
      <!-- 大图展示 -->
      <div class="relative w-full max-w-4xl aspect-video bg-black/30 rounded-2xl overflow-hidden shadow-2xl">
        <img
          v-if="currentPage?.image_url"
          :src="currentPage.image_url"
          :alt="`第 ${currentPageIndex + 1} 页`"
          class="w-full h-full object-contain"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-white/50">
          <span class="text-6xl">📖</span>
        </div>

        <!-- 左翻页按钮 -->
        <button
          v-if="currentPageIndex > 0"
          @click="prevPage"
          class="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/40 hover:bg-black/60 text-white flex items-center justify-center transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <!-- 右翻页按钮 -->
        <button
          v-if="currentPageIndex < pages.length - 1"
          @click="nextPage"
          class="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/40 hover:bg-black/60 text-white flex items-center justify-center transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <!-- 文字区域 -->
      <div class="mt-6 max-w-3xl w-full text-center">
        <p class="text-xl md:text-2xl text-white/90 leading-relaxed">
          {{ currentPage?.text || '' }}
        </p>
      </div>
    </div>

    <!-- 底部页码导航 -->
    <div class="px-4 py-4 bg-black/20">
      <div class="flex items-center justify-center gap-2 overflow-x-auto pb-2">
        <button
          v-for="(page, index) in pages"
          :key="page.page_number"
          @click="goToPage(index)"
          class="w-10 h-10 flex-shrink-0 rounded-full flex items-center justify-center text-sm font-medium transition-colors"
          :class="index === currentPageIndex
            ? 'bg-primary-500 text-white'
            : 'bg-white/20 text-white/70 hover:bg-white/30'"
        >
          {{ index + 1 }}
        </button>
      </div>
    </div>

    <!-- 隐藏的音频播放器 -->
    <audio
      ref="audioRef"
      :src="currentPage?.audio_url"
      @ended="onAudioEnded"
      @error="onAudioError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import type { PictureBookPage } from '@/api/types'

const props = defineProps<{
  title: string
  pages: PictureBookPage[]
}>()

defineEmits<{
  back: []
}>()

const currentPageIndex = ref(0)
const audioRef = ref<HTMLAudioElement | null>(null)

const currentPage = computed(() => props.pages[currentPageIndex.value])

function prevPage() {
  if (currentPageIndex.value > 0) {
    currentPageIndex.value--
  }
}

function nextPage() {
  if (currentPageIndex.value < props.pages.length - 1) {
    currentPageIndex.value++
  }
}

function goToPage(index: number) {
  currentPageIndex.value = index
}

async function playCurrentAudio() {
  await nextTick() // 等待 DOM 更新（src 属性变化）
  if (audioRef.value && currentPage.value?.audio_url) {
    audioRef.value.load() // 重新加载新的音频源
    audioRef.value.play().catch((err) => {
      console.warn('音频播放失败:', err)
    })
  }
}

function onAudioEnded() {
  // 音频播放完毕后自动翻到下一页，最后一页循环回第一页
  if (currentPageIndex.value < props.pages.length - 1) {
    nextPage()
  } else {
    // 循环播放：回到第一页
    currentPageIndex.value = 0
  }
}

function onAudioError(e: Event) {
  console.warn('音频加载失败:', e)
}

// 监听页面变化，自动播放当前页音频
watch(currentPageIndex, () => {
  playCurrentAudio()
})

// 键盘事件处理
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowLeft') {
    prevPage()
  } else if (e.key === 'ArrowRight') {
    nextPage()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  // 初始播放
  playCurrentAudio()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  // 清理音频
  if (audioRef.value) {
    audioRef.value.pause()
    audioRef.value.src = ''
  }
})
</script>

<style scoped>
.player-picture-book {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
</style>
