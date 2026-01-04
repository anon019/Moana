<template>
  <div class="player-video h-full flex flex-col bg-black">
    <!-- 顶部导航栏（悬浮，自动隐藏） -->
    <div
      class="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-3 bg-gradient-to-b from-black/60 to-transparent transition-opacity duration-300"
      :class="showControls ? 'opacity-100' : 'opacity-0'"
    >
      <button
        @click="$emit('back')"
        class="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span>返回</span>
      </button>
      <h1 class="text-white font-medium truncate max-w-[60%]">{{ title }}</h1>
      <div class="w-16"></div>
    </div>

    <!-- 视频容器 -->
    <div
      class="flex-1 flex items-center justify-center relative"
      @click="toggleControls"
      @mousemove="showControlsTemporarily"
    >
      <video
        ref="videoRef"
        :src="videoUrl"
        :poster="coverUrl"
        class="w-full h-full object-contain"
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @ended="onEnded"
        @error="onError"
        @play="isPlaying = true"
        @pause="isPlaying = false"
        @click.stop="togglePlay"
        playsinline
        loop
      />

      <!-- 中央播放按钮 -->
      <button
        v-if="!isPlaying"
        @click.stop="togglePlay"
        class="absolute inset-0 flex items-center justify-center"
      >
        <div class="w-20 h-20 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center hover:bg-white/40 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-white ml-1" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
      </button>
    </div>

    <!-- 底部控制栏（悬浮，自动隐藏） -->
    <div
      class="absolute bottom-0 left-0 right-0 z-10 px-4 py-4 bg-gradient-to-t from-black/60 to-transparent transition-opacity duration-300"
      :class="showControls ? 'opacity-100' : 'opacity-0'"
    >
      <!-- 进度条 -->
      <div class="mb-4">
        <div class="flex items-center gap-3">
          <span class="text-white/80 text-sm w-12 text-right">{{ formatTime(currentTime) }}</span>
          <div
            class="flex-1 h-1 bg-white/30 rounded-full cursor-pointer relative group"
            @click="handleProgressClick"
            ref="progressBarRef"
          >
            <div
              class="h-full bg-primary-500 rounded-full"
              :style="{ width: `${progressPercent}%` }"
            ></div>
            <div
              class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity"
              :style="{ left: `calc(${progressPercent}% - 6px)` }"
            ></div>
          </div>
          <span class="text-white/80 text-sm w-12">{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- 控制按钮 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <!-- 播放/暂停 -->
          <button
            @click="togglePlay"
            class="w-10 h-10 rounded-full hover:bg-white/10 text-white flex items-center justify-center transition-colors"
          >
            <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          </button>

          <!-- 音量控制 -->
          <div class="flex items-center gap-2">
            <button
              @click="toggleMute"
              class="w-10 h-10 rounded-full hover:bg-white/10 text-white flex items-center justify-center transition-colors"
            >
              <svg v-if="isMuted || volume === 0" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              v-model="volume"
              @input="updateVolume"
              class="w-20 h-1 bg-white/30 rounded-full appearance-none cursor-pointer"
            />
          </div>
        </div>

        <div class="flex items-center gap-4">
          <!-- 全屏 -->
          <button
            @click="toggleFullscreen"
            class="w-10 h-10 rounded-full hover:bg-white/10 text-white flex items-center justify-center transition-colors"
          >
            <svg v-if="!isFullscreen" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

defineProps<{
  title: string
  videoUrl: string
  coverUrl?: string
}>()

defineEmits<{
  back: []
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const progressBarRef = ref<HTMLElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const isMuted = ref(false)
const isFullscreen = ref(false)
const showControls = ref(true)

let hideControlsTimer: ReturnType<typeof setTimeout> | null = null

// 进度百分比
const progressPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

// 格式化时间
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 播放/暂停
function togglePlay() {
  if (!videoRef.value) return
  if (isPlaying.value) {
    videoRef.value.pause()
  } else {
    videoRef.value.play().catch((err) => {
      console.warn('视频播放失败:', err)
    })
  }
}

// 控制栏显示/隐藏
function toggleControls() {
  showControls.value = !showControls.value
  if (showControls.value) {
    scheduleHideControls()
  }
}

function showControlsTemporarily() {
  showControls.value = true
  scheduleHideControls()
}

function scheduleHideControls() {
  if (hideControlsTimer) {
    clearTimeout(hideControlsTimer)
  }
  hideControlsTimer = setTimeout(() => {
    if (isPlaying.value) {
      showControls.value = false
    }
  }, 3000)
}

// 点击进度条跳转
function handleProgressClick(e: MouseEvent) {
  if (!progressBarRef.value || !videoRef.value) return
  const rect = progressBarRef.value.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  videoRef.value.currentTime = percent * duration.value
}

// 音量控制
function updateVolume() {
  if (videoRef.value) {
    videoRef.value.volume = volume.value
    isMuted.value = volume.value === 0
  }
}

function toggleMute() {
  if (!videoRef.value) return
  if (isMuted.value) {
    videoRef.value.muted = false
    isMuted.value = false
    if (volume.value === 0) {
      volume.value = 0.5
      videoRef.value.volume = 0.5
    }
  } else {
    videoRef.value.muted = true
    isMuted.value = true
  }
}

// 全屏
function toggleFullscreen() {
  const container = videoRef.value?.closest('.player-video') as HTMLElement
  if (!container) return

  if (!document.fullscreenElement) {
    container.requestFullscreen().then(() => {
      isFullscreen.value = true
    }).catch((err) => {
      console.warn('全屏失败:', err)
    })
  } else {
    document.exitFullscreen().then(() => {
      isFullscreen.value = false
    })
  }
}

// 视频事件处理
function onTimeUpdate() {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime
  }
}

function onLoadedMetadata() {
  if (videoRef.value) {
    duration.value = videoRef.value.duration
  }
}

function onEnded() {
  // loop 属性会自动处理循环，这里仅作为备用
  isPlaying.value = false
  showControls.value = true
}

function onError(e: Event) {
  console.warn('视频加载失败:', e)
}

// 键盘控制
function handleKeydown(e: KeyboardEvent) {
  if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  } else if (e.key === 'ArrowLeft') {
    if (videoRef.value) {
      videoRef.value.currentTime = Math.max(0, currentTime.value - 10)
    }
  } else if (e.key === 'ArrowRight') {
    if (videoRef.value) {
      videoRef.value.currentTime = Math.min(duration.value, currentTime.value + 10)
    }
  } else if (e.key === 'f' || e.key === 'F') {
    toggleFullscreen()
  } else if (e.key === 'm' || e.key === 'M') {
    toggleMute()
  }
}

// 全屏变化监听
function handleFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  scheduleHideControls()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  if (hideControlsTimer) {
    clearTimeout(hideControlsTimer)
  }
  // 清理视频
  if (videoRef.value) {
    videoRef.value.pause()
    videoRef.value.src = ''
  }
})
</script>

<style scoped>
.player-video {
  position: relative;
}

/* 自定义音量滑块 */
input[type="range"] {
  -webkit-appearance: none;
  background: transparent;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  margin-top: -5px;
}

input[type="range"]::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}
</style>
