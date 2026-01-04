<template>
  <div class="player-nursery-rhyme h-full relative overflow-hidden">
    <!-- 模糊背景 -->
    <div class="absolute inset-0">
      <img
        v-if="coverUrl"
        :src="coverUrl"
        class="w-full h-full object-cover scale-110"
        :style="{ filter: 'blur(30px)' }"
      />
      <div class="absolute inset-0 bg-black/50"></div>
    </div>

    <!-- 主内容区 -->
    <div class="relative z-10 h-full flex flex-col">
      <!-- 顶部导航栏 -->
      <div class="flex items-center justify-between px-4 py-3 bg-gradient-to-b from-black/40 to-transparent">
        <button
          @click="$emit('back')"
          class="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          <span>返回</span>
        </button>
        <h1 class="text-white font-medium truncate max-w-[50%] text-center">{{ title }}</h1>
        <div class="w-16"></div>
      </div>

      <!-- 中间内容区：封面 + 歌词 -->
      <div class="flex-1 flex flex-col items-center justify-center px-4 overflow-hidden">
        <!-- 封面图 -->
        <div
          class="w-48 h-48 md:w-56 md:h-56 rounded-2xl overflow-hidden shadow-2xl bg-black/30"
          :class="{ 'animate-pulse-subtle': isPlaying }"
        >
          <img
            v-if="coverUrl"
            :src="coverUrl"
            :alt="title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-white/50">
            <span class="text-6xl">🎵</span>
          </div>
        </div>

        <!-- 三行歌词区域 -->
        <div class="mt-8 w-full max-w-lg text-center space-y-3">
          <!-- 上一行 -->
          <p class="text-white/40 text-base md:text-lg truncate transition-all duration-300">
            {{ prevLyricText }}
          </p>
          <!-- 当前行 -->
          <p class="text-white text-xl md:text-2xl font-bold transform scale-105 transition-all duration-300 min-h-[2rem]">
            {{ currentLyricText }}
          </p>
          <!-- 下一行 -->
          <p class="text-white/40 text-base md:text-lg truncate transition-all duration-300">
            {{ nextLyricText }}
          </p>
        </div>
      </div>

      <!-- 底部毛玻璃控制栏 -->
      <div class="glass-control-bar px-4 py-5 md:py-6">
        <!-- 进度条 -->
        <div class="max-w-lg mx-auto mb-5">
          <div class="flex items-center gap-3">
            <span class="text-white/70 text-xs w-10 text-right font-mono">{{ formatTime(currentTime) }}</span>
            <div
              class="flex-1 h-1 bg-white/20 rounded-full cursor-pointer relative group"
              @click="handleProgressClick"
              ref="progressBarRef"
            >
              <div
                class="h-full bg-white rounded-full transition-all"
                :style="{ width: `${progressPercent}%` }"
              ></div>
              <div
                class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                :style="{ left: `calc(${progressPercent}% - 6px)` }"
              ></div>
            </div>
            <span class="text-white/70 text-xs w-10 font-mono">{{ formatTime(duration) }}</span>
          </div>
        </div>

        <!-- 播放按钮 -->
        <div class="flex items-center justify-center gap-8">
          <!-- 后退 10 秒 -->
          <button
            @click="seek(-10)"
            class="w-11 h-11 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.334 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
            </svg>
          </button>

          <!-- 播放/暂停 -->
          <button
            @click="togglePlay"
            class="w-16 h-16 rounded-full bg-white text-gray-900 flex items-center justify-center transition-transform hover:scale-105 shadow-xl"
          >
            <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 ml-1" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-7 h-7" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          </button>

          <!-- 前进 10 秒 -->
          <button
            @click="seek(10)"
            class="w-11 h-11 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 隐藏的音频播放器 -->
    <audio
      ref="audioRef"
      :src="audioUrl"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="onEnded"
      @error="onError"
      @play="isPlaying = true"
      @pause="isPlaying = false"
      loop
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { LyricsObject, TimestampedLyricItem } from '@/api/types'

const props = defineProps<{
  title: string
  audioUrl: string
  coverUrl?: string
  lyrics: string | LyricsObject
}>()

defineEmits<{
  back: []
}>()

const audioRef = ref<HTMLAudioElement | null>(null)
const progressBarRef = ref<HTMLElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const currentLyricIndex = ref(-1)

// 英文标签转中文映射
const sectionLabels: Record<string, string> = {
  '[Intro]': '【前奏】',
  '[Verse]': '【主歌】',
  '[Verse 1]': '【主歌一】',
  '[Verse 2]': '【主歌二】',
  '[Verse 3]': '【主歌三】',
  '[Pre-Chorus]': '【预副歌】',
  '[Prechorus]': '【预副歌】',
  '[PreChorus]': '【预副歌】',
  '[Chorus]': '【副歌】',
  '[Hook]': '【副歌】',
  '[Bridge]': '【桥段】',
  '[Outro]': '【尾奏】',
  '[Interlude]': '【间奏】',
  '[Instrumental]': '【纯音乐】',
  '[Break]': '【间断】',
  '[Refrain]': '【叠句】',
}

// 转换英文标签为中文
function convertLabels(text: string): string {
  let result = text
  for (const [en, zh] of Object.entries(sectionLabels)) {
    result = result.replace(new RegExp(en.replace(/[[\]]/g, '\\$&'), 'gi'), zh)
  }
  return result
}

// 获取时间戳歌词数组（逐字）
const timestampedWords = computed((): TimestampedLyricItem[] => {
  if (!props.lyrics || typeof props.lyrics === 'string') return []
  return props.lyrics.timestamped || []
})

// 按行分割的歌词文本
const lyricLines = computed(() => {
  let text = ''
  if (!props.lyrics) return []
  if (typeof props.lyrics === 'string') {
    text = props.lyrics
  } else {
    text = props.lyrics.full_text || ''
  }
  text = convertLabels(text)
  return text.split('\n').filter(line => line.trim())
})

// 为每行歌词计算时间范围
interface LineWithTime {
  text: string
  startTime: number
  endTime: number
}

const linesWithTime = computed((): LineWithTime[] => {
  const lines = lyricLines.value
  const words = timestampedWords.value

  if (lines.length === 0) return []

  // 如果没有时间戳，按比例分配
  if (words.length === 0) {
    const totalDuration = duration.value || 60
    const lineTime = totalDuration / lines.length
    return lines.map((text, i) => ({
      text,
      startTime: i * lineTime,
      endTime: (i + 1) * lineTime
    }))
  }

  // 有时间戳：将逐字时间戳映射到行
  // 策略：按顺序将词分配给各行，根据词在行中的出现来匹配
  const result: LineWithTime[] = []
  let wordIndex = 0

  for (const lineText of lines) {
    // 跳过标签行（如【前奏】），给它一个短时间
    if (lineText.match(/^【.+】$/)) {
      const prevEnd = result.length > 0 ? result[result.length - 1].endTime : 0
      result.push({
        text: lineText,
        startTime: prevEnd,
        endTime: prevEnd + 2 // 标签显示2秒
      })
      continue
    }

    // 找到这行对应的词的时间范围
    let lineStart = -1
    let lineEnd = -1

    // 清理行文本用于匹配
    const cleanLine = lineText.replace(/[，。！？、\s]/g, '').toLowerCase()
    let matchedChars = 0
    const targetChars = cleanLine.length

    // 从当前词索引开始，尝试匹配这行的词
    while (wordIndex < words.length && matchedChars < targetChars) {
      const word = words[wordIndex]
      const cleanWord = word.word.replace(/[，。！？、\s]/g, '').toLowerCase()

      if (lineStart < 0) {
        lineStart = word.start_s
      }
      lineEnd = word.end_s
      matchedChars += cleanWord.length
      wordIndex++
    }

    // 如果没找到匹配，使用估算
    if (lineStart < 0) {
      const prevEnd = result.length > 0 ? result[result.length - 1].endTime : 0
      const totalRemaining = duration.value - prevEnd
      const remainingLines = lines.length - result.length
      const lineTime = totalRemaining / remainingLines
      lineStart = prevEnd
      lineEnd = prevEnd + lineTime
    }

    result.push({
      text: lineText,
      startTime: lineStart,
      endTime: lineEnd
    })
  }

  return result
})

// 根据当前时间查找歌词行索引
function findCurrentLineIndex(time: number): number {
  const lines = linesWithTime.value
  for (let i = 0; i < lines.length; i++) {
    if (time >= lines[i].startTime && time < lines[i].endTime) {
      return i
    }
  }
  // 如果超过最后一行，返回最后一行
  if (lines.length > 0 && time >= lines[lines.length - 1].endTime) {
    return lines.length - 1
  }
  return -1
}

// 更新当前歌词索引
function updateCurrentLyricIndex() {
  currentLyricIndex.value = findCurrentLineIndex(currentTime.value)
}

// 获取歌词文本
function getLyricText(index: number): string {
  if (index < 0 || index >= linesWithTime.value.length) return ''
  return linesWithTime.value[index].text
}

// 歌词总数
const lyricCount = computed(() => linesWithTime.value.length)

// 上一行歌词
const prevLyricText = computed(() => getLyricText(currentLyricIndex.value - 1))

// 当前行歌词
const currentLyricText = computed(() => getLyricText(currentLyricIndex.value))

// 下一行歌词
const nextLyricText = computed(() => {
  const nextIdx = currentLyricIndex.value + 1
  return nextIdx < lyricCount.value ? getLyricText(nextIdx) : ''
})

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
  if (!audioRef.value) return
  if (isPlaying.value) {
    audioRef.value.pause()
  } else {
    audioRef.value.play().catch((err) => {
      console.warn('音频播放失败:', err)
    })
  }
}

// 快进/快退
function seek(seconds: number) {
  if (!audioRef.value) return
  const newTime = Math.max(0, Math.min(duration.value, currentTime.value + seconds))
  audioRef.value.currentTime = newTime
}

// 点击进度条跳转
function handleProgressClick(e: MouseEvent) {
  if (!progressBarRef.value || !audioRef.value) return
  const rect = progressBarRef.value.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  audioRef.value.currentTime = percent * duration.value
}

// 音频事件处理
function onTimeUpdate() {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime
    updateCurrentLyricIndex()
  }
}

function onLoadedMetadata() {
  if (audioRef.value) {
    duration.value = audioRef.value.duration
  }
}

function onEnded() {
  isPlaying.value = false
  currentLyricIndex.value = -1
}

function onError(e: Event) {
  console.warn('音频加载失败:', e)
}

// 键盘控制
function handleKeydown(e: KeyboardEvent) {
  if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  } else if (e.key === 'ArrowLeft') {
    seek(-10)
  } else if (e.key === 'ArrowRight') {
    seek(10)
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (audioRef.value) {
    audioRef.value.pause()
    audioRef.value.src = ''
  }
})
</script>

<style scoped>
.player-nursery-rhyme {
  background: #1a1a1a;
}

.glass-control-bar {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes pulse-subtle {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s ease-in-out infinite;
}
</style>
