<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- 背景遮罩 -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />

        <!-- 弹窗内容 -->
        <div class="relative w-full max-w-md bg-gradient-to-br from-purple-50 via-white to-pink-50 rounded-3xl p-8 shadow-2xl">
          <!-- 成功状态 -->
          <template v-if="status === 'completed'">
            <div class="text-center">
              <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center text-4xl text-white shadow-lg">
                ✓
              </div>
              <h3 class="text-xl font-bold text-gray-800 mb-2">生成完成!</h3>
              <p class="text-gray-500 mb-6">{{ contentTypeLabel }}已经准备好了</p>
              <button
                class="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl transition-shadow"
                @click="handlePlay"
              >
                立即播放
              </button>
            </div>
          </template>

          <!-- 失败状态 -->
          <template v-else-if="status === 'failed'">
            <div class="text-center">
              <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-red-400 to-rose-500 rounded-full flex items-center justify-center text-4xl text-white shadow-lg">
                ✕
              </div>
              <h3 class="text-xl font-bold text-gray-800 mb-2">生成失败</h3>
              <p class="text-gray-500 mb-6">{{ error || '请稍后重试' }}</p>
              <div class="flex gap-3">
                <button
                  class="flex-1 py-3 bg-gray-100 text-gray-700 rounded-2xl font-medium hover:bg-gray-200 transition-colors"
                  @click="handleClose"
                >
                  关闭
                </button>
                <button
                  class="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl font-medium shadow-lg"
                  @click="handleRetry"
                >
                  重试
                </button>
              </div>
            </div>
          </template>

          <!-- 生成中状态 -->
          <template v-else>
            <div class="text-center">
              <!-- 动画图标 -->
              <div class="relative w-24 h-24 mx-auto mb-6">
                <!-- 外圈旋转 -->
                <div class="absolute inset-0 border-4 border-purple-200 rounded-full" />
                <div
                  class="absolute inset-0 border-4 border-transparent border-t-purple-500 rounded-full animate-spin"
                />
                <!-- 内圈动画 -->
                <div class="absolute inset-3 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center">
                  <span class="text-3xl animate-pulse">{{ getStageIcon() }}</span>
                </div>
              </div>

              <h3 class="text-xl font-bold text-gray-800 mb-2">正在生成{{ contentTypeLabel }}</h3>
              <p class="text-gray-500 mb-4">{{ stageText }}</p>

              <!-- 进度条 -->
              <div class="relative h-3 bg-gray-100 rounded-full overflow-hidden mb-2">
                <div
                  class="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                  :style="{ width: `${progress}%` }"
                />
                <!-- 流光效果 -->
                <div
                  class="absolute inset-y-0 left-0 bg-gradient-to-r from-transparent via-white/30 to-transparent rounded-full animate-shimmer"
                  :style="{ width: `${progress}%` }"
                />
              </div>
              <p class="text-sm text-purple-500 font-medium">{{ progress }}%</p>

              <!-- 提示 -->
              <p class="mt-6 text-xs text-gray-400">
                AI 正在努力创作中，请耐心等待...
              </p>
            </div>
          </template>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  visible: boolean
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'idle'
  progress: number
  stage: string
  error?: string
  contentType: 'picture_book' | 'nursery_rhyme' | 'video'
}>()

const emit = defineEmits<{
  'play': []
  'close': []
  'retry': []
}>()

const contentTypeLabel = computed(() => {
  const labels = {
    picture_book: '绘本',
    nursery_rhyme: '儿歌',
    video: '视频'
  }
  return labels[props.contentType] || '内容'
})

const stageText = computed(() => {
  const stageTexts: Record<string, string> = {
    pending: '正在排队中...',
    processing: '正在处理...',
    story: '正在创作故事...',
    image: '正在绘制插图...',
    audio: '正在生成音频...',
    text: '正在创作歌词...',
    first: '正在生成音乐...',
    complete: '即将完成...',
    video: '正在生成视频...'
  }
  return stageTexts[props.stage] || '正在生成中...'
})

function getStageIcon(): string {
  const icons: Record<string, string> = {
    pending: '⏳',
    processing: '🎨',
    story: '📝',
    image: '🖼️',
    audio: '🔊',
    text: '🎵',
    first: '🎶',
    video: '🎬'
  }
  return icons[props.stage] || '✨'
}

function handlePlay() {
  emit('play')
}

function handleClose() {
  emit('close')
}

function handleRetry() {
  emit('retry')
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.9);
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}
</style>
