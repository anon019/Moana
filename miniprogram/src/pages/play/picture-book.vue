<template>
  <view class="storybook" @tap="handleTap">
    <!-- 魔法背景 -->
    <view class="magic-bg">
      <view class="sparkle" v-for="i in 4" :key="i" :style="getSparkleStyle(i)"></view>
    </view>

    <!-- 绘本内容 - 沉浸式全屏 -->
    <swiper
      v-if="content"
      :key="contentId"
      class="story-swiper"
      :current="currentPage"
      :circular="false"
      :duration="400"
      easing-function="easeInOutCubic"
      @change="onPageChange"
      @animationfinish="onAnimationFinish"
    >
      <swiper-item v-for="(page, index) in content.pages" :key="index">
        <view class="story-page">
          <!-- 全屏故事图片 - 原图窗口收窄到当前页前后 1 页，远页只保留缩略图 -->
          <view class="story-image-container">
            <!-- 缩略图（模糊背景，立即显示） -->
            <image
              v-if="thumbPages.has(index) && page.image_thumb_url && !imageLoaded[index]"
              class="story-image story-image-thumb"
              :src="page.image_thumb_url"
              mode="aspectFit"
            />

            <!-- 原图（淡入效果，仅近邻页加载） -->
            <image
              v-if="fullImagePages.has(index) && page.image_url"
              class="story-image story-image-full"
              :class="{ loaded: imageLoaded[index] }"
              :src="page.image_url"
              mode="aspectFit"
              @load="onImageLoad(index)"
              @error="onImageError(index)"
            />

            <!-- 图片加载占位（远页或无缩略图时显示） -->
            <view v-if="!thumbPages.has(index) || (!page.image_thumb_url && !imageLoaded[index])" class="image-placeholder">
              <view class="placeholder-shimmer"></view>
            </view>
          </view>

          <!-- 故事文字卡片 - 童话书页风格 -->
          <view
            class="story-card"
            :class="{ visible: currentPage === index && cardVisible }"
          >
            <!-- 书页装饰 -->
            <view class="page-decor">
              <view class="decor-corner corner-tl"></view>
              <view class="decor-corner corner-tr"></view>
              <view class="decor-corner corner-bl"></view>
              <view class="decor-corner corner-br"></view>
            </view>
            <!-- 纸张质感层 -->
            <view class="page-texture"></view>
            <!-- 文字内容 -->
            <view class="card-content">
              <view class="text-wrapper">
                <text class="story-text">{{ page.text }}</text>
              </view>
              <!-- 页码装饰 -->
              <view class="page-number">
                <text>{{ index + 1 }} / {{ content?.pages?.length || 0 }}</text>
              </view>
            </view>
          </view>
        </view>
      </swiper-item>
    </swiper>

    <!-- 极简顶部 - 只有返回 -->
    <view class="minimal-header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="back-touch" @tap.stop="handleClose">
        <view class="back-icon">
          <view class="back-line back-line-1"></view>
          <view class="back-line back-line-2"></view>
        </view>
      </view>
      <!-- 播放状态指示 -->
      <view class="play-indicator" :class="{ playing: isPlaying }">
        <view class="indicator-bar" v-for="i in 3" :key="i"></view>
      </view>
    </view>

    <!-- 底部页码指示器 -->
    <view class="page-dots">
      <view
        v-for="(_, index) in content?.pages || []"
        :key="index"
        class="dot"
        :class="{
          active: index === currentPage,
          passed: index < currentPage
        }"
      ></view>
    </view>

    <!-- 翻页提示 (首次显示) -->
    <view v-if="showSwipeHint" class="swipe-hint">
      <view class="hint-hand">👆</view>
      <text class="hint-label">滑动翻页</text>
    </view>

    <!-- 暂停遮罩 -->
    <view v-if="showPauseOverlay" class="pause-overlay">
      <view class="pause-icon">
        <view class="pause-bar"></view>
        <view class="pause-bar"></view>
      </view>
      <text class="pause-text">已暂停 · 点击继续</text>
    </view>

    <!-- 切换绘本过渡 -->
    <view v-if="showTransition" class="transition-screen">
      <view class="transition-content">
        <text class="transition-icon">📖</text>
        <text class="transition-title">下一个故事</text>
        <text class="transition-book" v-if="nextBookTitle">{{ nextBookTitle }}</text>
      </view>
    </view>

    <!-- 加载状态 - 优雅的书本动画 -->
    <view v-if="loading" class="loading-screen">
      <view class="book-loader">
        <view class="book-page page-left"></view>
        <view class="book-page page-right"></view>
        <view class="book-spine"></view>
      </view>
      <text class="loading-text">正在打开故事书...</text>
    </view>

    <!-- 完成动画 -->
    <view v-if="showComplete" class="complete-screen">
      <view class="complete-stars">
        <text v-for="i in 5" :key="i" class="star" :style="{ animationDelay: i * 0.1 + 's' }">⭐</text>
      </view>
      <text class="complete-title">故事结束啦！</text>
      <text class="complete-subtitle">{{ content?.title }}</text>
      <view class="complete-actions">
        <view class="action-btn share-btn" @tap.stop="handleSharePoster">
          <text class="btn-icon">📤</text>
          <text class="btn-text">分享海报</text>
        </view>
        <view class="action-btn close-btn" @tap.stop="closeComplete">
          <text class="btn-text">返回</text>
        </view>
      </view>
    </view>

    <!-- 海报生成画布（隐藏） -->
    <canvas
      canvas-id="posterCanvas"
      class="poster-canvas"
      style="position: fixed; left: -9999px; width: 540px; height: 960px;"
    />

  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, getCurrentInstance } from 'vue'
import { onLoad, onShareAppMessage, onShareTimeline } from '@dcloudio/uni-app'
import { useChildStore } from '@/stores/child'
import { useContentStore } from '@/stores/content'
import { startPlay, updateProgress, completePlay, submitInteraction } from '@/api/play'
import { generatePoster, savePosterToAlbum } from '@/utils/poster'
import { ensureHttps } from '@/utils/url'
import perf from '@/utils/performance'
import type { PictureBook, PictureBookPage } from '@/api/content'

const childStore = useChildStore()
const contentStore = useContentStore()

// 状态
const contentId = ref('')
const content = ref<PictureBook | null>(null)
const loading = ref(true)
const currentPage = ref(0)
const isPlaying = ref(true)  // 默认自动播放
const playHistoryId = ref('')
const showInteraction = ref(false)
const playStartTime = ref(0)
const lastUpdateTime = ref(0)
const UPDATE_INTERVAL = 5000

// UI 状态
const imageLoaded = ref<boolean[]>([])
const imageRetryCount = ref<number[]>([])  // each page's retry count
const MAX_IMAGE_RETRY = 3
const cardVisible = ref(false)
const showPauseOverlay = ref(false)
const showSwipeHint = ref(false)
const showComplete = ref(false)
const statusBarHeight = ref(44)

// 顺序播放队列
const playlist = ref<string[]>([])
let playIndex = 0
const showTransition = ref(false)
const nextBookTitle = ref('')

// 时间提醒

// 页面生命周期标记（防止 unmount 后异步回调继续执行）
let isUnmounted = false
// 防止 onImageLoad 和 onAnimationFinish 重复触发同一页音频
let audioStartedForPage = -1

// 海报分享
const generatingPoster = ref(false)
const instance = getCurrentInstance()

// 音频
let audioContext: UniApp.InnerAudioContext | null = null
let autoPlayTimer: number | null = null
let pageAdvanceTimer: number | null = null
let completeTimer: number | null = null  // 完成后自动返回的定时器
let resumePlayTimer: number | null = null
let audioBootstrapTimer: number | null = null
const audioReady = ref(false)
let currentAudioPage = -1
let currentAudioCacheKey = ''
let currentAudioNetworkSrc = ''
let currentAudioUsesCachedFile = false
let currentAudioRequestId = 0
let currentAudioStartedOnce = false
let currentAudioTime = 0
let currentAudioDuration = 0
let activeBookToken = 0
let warmingNextBookId = ''
let warmedNextBook: PictureBook | null = null
let warmedNextBookReadyTask: Promise<void> | null = null
let nextBookWarmTask: Promise<PictureBook | null> | null = null
let playSessionRequestToken = 0
let imageWarmGeneration = 0
let retainedAudioBookIds: Set<string> | null = null
const INITIAL_VIEWPORT_IMAGE_TIMEOUT = 700
const AUDIO_BOOTSTRAP_TIMEOUT = 7000
const MIN_AUDIO_FALLBACK_MS = 3500
const MAX_AUDIO_FALLBACK_MS = 15000
// 音频缓存：bookId:pageIndex:url -> 本地文件路径
const audioCache = new Map<string, string>()
// 图片预热去重，避免频繁重复 getImageInfo
const imagePreloading = new Set<number>()
const warmedImageUrls = new Set<string>()
const imageWarmQueue: Array<{
  taskKey: string
  src: string
  priority: number
  generation: number
  resolve: () => void
}> = []
const imageWarmTasks = new Map<string, Promise<void>>()
const queuedImageWarms = new Set<string>()
const MAX_IMAGE_WARM_CONCURRENCY = 2
let activeImageWarmCount = 0
// 事件驱动的音频缓存通知（替代轮询）
const audioCacheCallbacks = new Map<string, Array<() => void>>()
const audioDownloadQueue: Array<{
  key: string
  url: string
  priority: number
  bookId: string
  bookToken: number
}> = []
const queuedAudioDownloads = new Map<string, {
  key: string
  url: string
  priority: number
  bookId: string
  bookToken: number
}>()
const audioDownloading = new Set<string>()
const MAX_AUDIO_PRELOAD_CONCURRENCY = 1
let activeAudioDownloadCount = 0

function notifyAudioCached(cacheKey: string) {
  const callbacks = audioCacheCallbacks.get(cacheKey)
  if (callbacks) {
    callbacks.forEach(cb => cb())
    audioCacheCallbacks.delete(cacheKey)
  }
}
// Event-driven image load notification (replaces polling)
const imageLoadCallbacks = new Map<number, Array<() => void>>()

function notifyImageLoaded(index: number) {
  const callbacks = imageLoadCallbacks.get(index)
  if (callbacks) {
    callbacks.forEach(cb => cb())
    imageLoadCallbacks.delete(index)
  }
}

const activeTimeouts = new Set<number>()

function scheduleTimeout(handler: () => void, delay = 0): number {
  const timer = setTimeout(() => {
    activeTimeouts.delete(timer as unknown as number)
    handler()
  }, delay) as unknown as number

  activeTimeouts.add(timer)
  return timer
}

function cancelTimeout(timer: number | null | undefined) {
  if (timer == null) return
  clearTimeout(timer)
  activeTimeouts.delete(timer)
}

function waitMs(delay = 0): Promise<void> {
  return new Promise(resolve => {
    scheduleTimeout(resolve, delay)
  })
}

function clearAllTimeouts() {
  activeTimeouts.forEach(timer => clearTimeout(timer))
  activeTimeouts.clear()
  autoPlayTimer = null
  pageAdvanceTimer = null
  audioBootstrapTimer = null
}

function cancelPageAdvanceTimer() {
  cancelTimeout(pageAdvanceTimer)
  pageAdvanceTimer = null
}

function cancelAudioBootstrapTimer() {
  cancelTimeout(audioBootstrapTimer)
  audioBootstrapTimer = null
}

function invalidatePlaySessionRequest() {
  playSessionRequestToken++
}

function resetRetainedAudioBookIds(bookIds?: Iterable<string>) {
  const ids = Array.from(bookIds || []).filter(Boolean)
  retainedAudioBookIds = ids.length ? new Set(ids) : null
}

function getRelevantAudioBookIds() {
  if (retainedAudioBookIds) {
    return retainedAudioBookIds
  }

  const ids = new Set<string>()
  if (content.value?.id) {
    ids.add(content.value.id)
  }
  if (warmingNextBookId) {
    ids.add(warmingNextBookId)
  }
  if (warmedNextBook?.id) {
    ids.add(warmedNextBook.id)
  }
  return ids
}

function isAudioBookRelevant(bookId: string) {
  return !!bookId && !isUnmounted && getRelevantAudioBookIds().has(bookId)
}

function canAutoStartCurrentPage(pageIndex = currentPage.value) {
  return !isUnmounted
    && isPlaying.value
    && !loading.value
    && !showTransition.value
    && pageIndex === currentPage.value
}

function requestCurrentPagePlayback(pageIndex = currentPage.value) {
  if (!canAutoStartCurrentPage(pageIndex) || audioStartedForPage === pageIndex) {
    return
  }

  audioStartedForPage = pageIndex
  void playCurrentPageAudio()
}

function getFallbackDelay(page?: PictureBookPage) {
  const apiDurationMs = Number(page?.duration || 0) > 0
    ? Math.round(Number(page?.duration || 0) * 1000)
    : 0
  const remainingAudioMs = currentAudioDuration > 0
    ? Math.max(0, Math.round((currentAudioDuration - currentAudioTime) * 1000))
    : 0
  const baseMs = remainingAudioMs > 0 ? remainingAudioMs + 400 : (apiDurationMs || 5000)

  return Math.max(MIN_AUDIO_FALLBACK_MS, Math.min(MAX_AUDIO_FALLBACK_MS, baseMs))
}

function schedulePageAdvance(delay = 600, expectedPage = currentPage.value, requestId = currentAudioRequestId) {
  cancelPageAdvanceTimer()
  pageAdvanceTimer = scheduleTimeout(() => {
    pageAdvanceTimer = null
    if (!isPlaying.value || loading.value || showTransition.value) return
    if (expectedPage !== currentPage.value) return
    if (requestId !== currentAudioRequestId) return
    goToNextPage()
  }, delay)
}

function startAudioBootstrapWatchdog(pageIndex: number, requestId: number) {
  cancelAudioBootstrapTimer()
  audioBootstrapTimer = scheduleTimeout(() => {
    audioBootstrapTimer = null
    if (!isPlaying.value || loading.value || showTransition.value) return
    if (pageIndex !== currentPage.value) return
    if (requestId !== currentAudioRequestId) return
    if (currentAudioStartedOnce || audioReady.value) return

    console.warn(`[绘本音频] 第 ${pageIndex + 1} 页长时间未就绪，使用保守降级计时`)
    startFallbackTimer(undefined, pageIndex, requestId)
  }, AUDIO_BOOTSTRAP_TIMEOUT)
}

function getAudioCacheKey(pageIndex: number, audioUrl?: string, bookId = content.value?.id || contentId.value || 'temp-book') {
  const normalizedUrl = audioUrl ? ensureHttps(audioUrl) : ''
  return JSON.stringify([bookId, pageIndex, normalizedUrl])
}

function getBookIdFromAudioCacheKey(cacheKey: string): string {
  try {
    const parsed = JSON.parse(cacheKey)
    return Array.isArray(parsed) ? String(parsed[0] || '') : ''
  } catch (e) {
    return ''
  }
}

function queueImageWarm(src?: string, priority = 1): Promise<void> {
  const normalizedSrc = src ? ensureHttps(src) : ''
  if (!normalizedSrc || warmedImageUrls.has(normalizedSrc)) {
    return Promise.resolve()
  }

  const taskKey = `${imageWarmGeneration}:${normalizedSrc}`
  const existingTask = imageWarmTasks.get(taskKey)
  if (existingTask) {
    return existingTask
  }

  let resolveTask!: () => void
  const taskPromise = new Promise<void>((resolve) => {
    resolveTask = resolve
  })

  imageWarmTasks.set(taskKey, taskPromise)
  imageWarmQueue.push({
    taskKey,
    src: normalizedSrc,
    priority,
    generation: imageWarmGeneration,
    resolve: resolveTask
  })
  queuedImageWarms.add(taskKey)
  pumpImageWarmQueue()

  return taskPromise
}

function pumpImageWarmQueue() {
  while (activeImageWarmCount < MAX_IMAGE_WARM_CONCURRENCY && imageWarmQueue.length > 0) {
    imageWarmQueue.sort((a, b) => a.priority - b.priority)
    const task = imageWarmQueue.shift()
    if (!task) return

    queuedImageWarms.delete(task.taskKey)
    if (task.generation !== imageWarmGeneration) {
      imageWarmTasks.delete(task.taskKey)
      task.resolve()
      continue
    }
    activeImageWarmCount++
    let succeeded = false

    uni.getImageInfo({
      src: task.src,
      success: () => {
        succeeded = true
      },
      complete: () => {
        if (succeeded && task.generation === imageWarmGeneration) {
          warmedImageUrls.add(task.src)
        }
        imageWarmTasks.delete(task.taskKey)
        activeImageWarmCount = Math.max(0, activeImageWarmCount - 1)
        task.resolve()
        pumpImageWarmQueue()
      }
    })
  }
}

function queueAudioDownload(pageIndex: number, audioUrl?: string, priority = 1, bookId = content.value?.id || contentId.value || 'temp-book') {
  if (!audioUrl) return

  const key = getAudioCacheKey(pageIndex, audioUrl, bookId)
  if (audioCache.has(key) || audioDownloading.has(key)) {
    return
  }

  const queuedTask = queuedAudioDownloads.get(key)
  if (queuedTask) {
    if (priority < queuedTask.priority) {
      queuedTask.priority = priority
    }
    return
  }

  const task = {
    key,
    url: ensureHttps(audioUrl),
    priority,
    bookId,
    bookToken: activeBookToken
  }

  queuedAudioDownloads.set(key, task)
  audioDownloadQueue.push(task)
  pumpAudioDownloadQueue()
}

function pumpAudioDownloadQueue() {
  while (activeAudioDownloadCount < MAX_AUDIO_PRELOAD_CONCURRENCY && audioDownloadQueue.length > 0) {
    audioDownloadQueue.sort((a, b) => a.priority - b.priority)
    const task = audioDownloadQueue.shift()
    if (!task) return

    if (queuedAudioDownloads.get(task.key) !== task) {
      continue
    }

    queuedAudioDownloads.delete(task.key)
    audioDownloading.add(task.key)
    activeAudioDownloadCount++

    uni.downloadFile({
      url: task.url,
      success: (res) => {
        if (res.statusCode === 200 && res.tempFilePath) {
          if (task.bookToken !== activeBookToken || !isAudioBookRelevant(task.bookId)) {
            try {
              uni.getFileSystemManager().unlink({
                filePath: res.tempFilePath,
                fail: () => { /* silent */ }
              })
            } catch (e) { /* silent */ }
            notifyAudioCached(task.key)
            return
          }

          audioCache.set(task.key, res.tempFilePath)
          notifyAudioCached(task.key)
          return
        }

        notifyAudioCached(task.key)
      },
      fail: () => {
        notifyAudioCached(task.key)
      },
      complete: () => {
        audioDownloading.delete(task.key)
        activeAudioDownloadCount = Math.max(0, activeAudioDownloadCount - 1)
        pumpAudioDownloadQueue()
      }
    })
  }
}

function clearPendingAudioDownloads(keepBookIds?: Set<string>) {
  if (!keepBookIds || keepBookIds.size === 0) {
    audioDownloadQueue.length = 0
    queuedAudioDownloads.clear()
    return
  }

  for (let i = audioDownloadQueue.length - 1; i >= 0; i--) {
    const task = audioDownloadQueue[i]
    if (!keepBookIds.has(task.bookId)) {
      audioDownloadQueue.splice(i, 1)
      queuedAudioDownloads.delete(task.key)
    }
  }
}

function getUpcomingBookId(offset = 1): string {
  if (playlist.value.length <= 1) return ''

  const nextIndex = playIndex + offset
  if (nextIndex < 0 || nextIndex >= playlist.value.length) {
    return ''
  }

  return playlist.value[nextIndex]
}

function warmBookEntryAssets(book: PictureBook, startPage = 0): Promise<void> {
  if (!book.pages?.length) {
    return Promise.resolve()
  }

  const safePage = Math.max(0, Math.min(book.pages.length - 1, startPage))
  const current = book.pages[safePage]
  const next = book.pages[safePage + 1]

  const imageTasks: Promise<void>[] = []
  if (current?.image_thumb_url || current?.image_url) {
    imageTasks.push(queueImageWarm(current.image_thumb_url || current.image_url, 0))
  }
  if (current?.image_url) {
    imageTasks.push(queueImageWarm(current.image_url, 0))
  }
  if (next?.image_thumb_url || next?.image_url) {
    imageTasks.push(queueImageWarm(next.image_thumb_url || next.image_url, 1))
  }
  if (next?.image_url) {
    imageTasks.push(queueImageWarm(next.image_url, 1))
  }

  cacheAudioForPage(safePage, current?.audio_url, 0, book.id)
  cacheAudioForPage(safePage + 1, next?.audio_url, 1, book.id)

  const criticalAudioReady = current?.audio_url
    ? Promise.race([
      waitForAudioCache(safePage, current.audio_url, 220, book.id).then(() => undefined),
      waitMs(220)
    ])
    : Promise.resolve()

  const criticalImageReady = current?.image_thumb_url || current?.image_url
    ? Promise.race([
      warmImage(current.image_thumb_url || current.image_url, 900),
      waitMs(900)
    ])
    : Promise.resolve()

  return Promise.all([criticalImageReady, criticalAudioReady, Promise.allSettled(imageTasks)]).then(() => undefined)
}

function warmUpcomingBook(force = false): Promise<PictureBook | null> {
  const nextId = getUpcomingBookId()
  if (!nextId) {
    return Promise.resolve(null)
  }

  if (!force && warmedNextBook?.id === nextId) {
    return Promise.resolve(warmedNextBook)
  }

  if (!force && warmingNextBookId === nextId && nextBookWarmTask) {
    return nextBookWarmTask
  }

  warmingNextBookId = nextId
  nextBookWarmTask = (async () => {
    const cached = contentStore.getCachedContent(nextId)
    const nextBook = cached?.pages?.length ? cached : await contentStore.fetchContentDetail(nextId)
    if (!nextBook?.pages?.length) {
      return null
    }

    warmedNextBook = nextBook
    warmedNextBookReadyTask = warmBookEntryAssets(nextBook)
    return nextBook
  })().catch(() => {
    return null
  }).finally(() => {
    if (warmingNextBookId === nextId) {
      warmingNextBookId = ''
    }
  })

  return nextBookWarmTask
}

// 本地是否已有存储的播放进度（区分"从头开始"和"无记录"）
let hasLocalProgress = false

// 计算属性
const totalPages = computed(() => content.value?.pages?.length || 0)

function clampPageIndex(pageIndex: number): number {
  if (totalPages.value <= 0) return 0
  return Math.max(0, Math.min(totalPages.value - 1, pageIndex))
}

function getStoredResumePage(): number {
  if (!contentId.value) return 0

  const progress = uni.getStorageSync(`play_progress_${contentId.value}`)
  if (!progress) return 0

  const pageIndex = Number(progress?.page)

  if (!Number.isFinite(pageIndex) || pageIndex < 0) {
    return 0
  }

  const clamped = clampPageIndex(pageIndex)
  // 如果存储的进度是最后一页，说明上次已播完，从头开始
  if (totalPages.value > 0 && clamped >= totalPages.value - 1) {
    uni.removeStorageSync(`play_progress_${contentId.value}`)
    return 0
  }

  hasLocalProgress = true
  return clamped
}

// 缩略图窗口稍宽，保证滑动时过渡平滑
const thumbPages = computed(() => {
  const s = new Set<number>()
  const lo = Math.max(0, currentPage.value - 2)
  const hi = Math.min(totalPages.value - 1, currentPage.value + 2)
  for (let i = lo; i <= hi; i++) s.add(i)
  return s
})

// 原图窗口收窄，避免远页同时解码占用内存和主线程
const fullImagePages = computed(() => {
  const s = new Set<number>()
  const lo = Math.max(0, currentPage.value - 1)
  const hi = Math.min(totalPages.value - 1, currentPage.value + 1)
  for (let i = lo; i <= hi; i++) s.add(i)
  return s
})

// 星星闪烁样式
function getSparkleStyle(i: number) {
  const positions = [
    { top: '10%', left: '8%' }, { top: '15%', left: '85%' },
    { top: '35%', left: '5%' }, { top: '40%', left: '92%' }
  ]
  const pos = positions[i - 1] || { top: '50%', left: '50%' }
  const size = 4 + (i % 3) * 2
  return `top: ${pos.top}; left: ${pos.left}; width: ${size}rpx; height: ${size}rpx;`
}

// 互动图标
function getInteractionIcon(type: string) {
  const icons: Record<string, string> = {
    tap: '👆',
    drag: '✋',
    shake: '📱'
  }
  return icons[type] || '✨'
}

// 页面切换
function onPageChange(e: any) {
  const newPage = e.detail.current
  cancelPageAdvanceTimer()
  cancelAudioBootstrapTimer()
  stopAutoPlay()
  currentPage.value = newPage
  cardVisible.value = false
  showInteraction.value = false
  audioStartedForPage = -1  // 重置防重复标记
  cancelTimeout(resumePlayTimer)
  resumePlayTimer = null

  // 停止当前音频
  stopCurrentAudio()

  // 智能预加载相邻页
  preloadAdjacentImages(newPage)

  // 更新进度
  updatePlayProgress()
}

// 动画完成后显示文字卡片
function onAnimationFinish() {
  nextTick(() => {
    cardVisible.value = true
    // 如果 onImageLoad 还没触发音频，这里作为后备触发
    scheduleTimeout(() => {
      requestCurrentPagePlayback()
    }, 100)
  })
}

// 点击屏幕 - 暂停/播放
function handleTap() {
  if (loading.value || showComplete.value) return

  isPlaying.value = !isPlaying.value
  showPauseOverlay.value = !isPlaying.value

  if (isPlaying.value) {
    // 继续播放：同一页优先从已暂停音频直接续播
    cancelTimeout(resumePlayTimer)
    if (audioContext && currentAudioPage === currentPage.value) {
      showPauseOverlay.value = false
      audioContext.play()
      return
    }

    resumePlayTimer = scheduleTimeout(() => {
      resumePlayTimer = null
      if (!isPlaying.value) return
      showPauseOverlay.value = false
      requestCurrentPagePlayback()
    }, 120)
  } else {
    // 暂停
    cancelTimeout(resumePlayTimer)
    resumePlayTimer = null
    cancelPageAdvanceTimer()
    cancelAudioBootstrapTimer()
    pauseCurrentAudio()
    stopAutoPlay()
  }
}

// 图片加载
function onImageLoad(index: number) {
  imageLoaded.value[index] = true
  notifyImageLoaded(index)

  // 首图加载性能埋点
  if (index === 0) {
    perf.measure('首图加载时间', 'pageLoad')
  }

  // 当前页图片加载完成后立即显示卡片并播放音频（无延迟）
  if (index === currentPage.value && !cardVisible.value) {
    cardVisible.value = true
    requestCurrentPagePlayback(index)
  }
}

function onImageError(index: number) {
  const retries = imageRetryCount.value[index] || 0
  if (retries < MAX_IMAGE_RETRY) {
    imageRetryCount.value[index] = retries + 1
    const delay = Math.pow(2, retries) * 500 // 500ms, 1s, 2s
    console.warn(`[image] page ${index + 1} load failed, retry ${retries + 1}/${MAX_IMAGE_RETRY} in ${delay}ms`)
    scheduleTimeout(() => {
      const page = content.value?.pages?.[index]
      if (page?.image_url) {
        const cleanUrl = page.image_url.replace(/[?&]_retry=\d+/, '')
        const sep = cleanUrl.includes('?') ? '&' : '?'
        page.image_url = cleanUrl + `${sep}_retry=${retries + 1}`
      }
    }, delay)
  } else {
    console.error(`[image] page ${index + 1} failed after ${MAX_IMAGE_RETRY} retries`)
    imageLoaded.value[index] = true
    notifyImageLoaded(index)
  }
}

function preloadAdjacentImages(centerIndex: number, range = 3, excludeIndices?: Set<number>) {
  if (!content.value?.pages?.length) return

  const indices: number[] = []
  for (let i = centerIndex; i <= centerIndex + range && i < content.value.pages.length; i++) {
    indices.push(i)
  }
  if (centerIndex > 0) indices.unshift(centerIndex - 1)

  indices.forEach((index, offset) => {
    if (excludeIndices?.has(index)) return
    const page = content.value!.pages[index]
    if (imageLoaded.value[index] || imagePreloading.has(index)) return
    imagePreloading.add(index)

    scheduleTimeout(() => {
      const warmTasks: Promise<void>[] = []

      if (page.image_thumb_url) {
        warmTasks.push(queueImageWarm(page.image_thumb_url, index === currentPage.value ? 0 : 1))
      }

      if (page.image_url) {
        warmTasks.push(queueImageWarm(page.image_url, index <= currentPage.value + 1 ? 0 : 1))
      }

      Promise.allSettled(warmTasks).finally(() => {
        imagePreloading.delete(index)
      })
    }, 100 * offset)
  })
}

function warmImage(src?: string, timeout = 1200): Promise<void> {
  if (!src) return Promise.resolve()

  return new Promise((resolve) => {
    let settled = false
    const done = () => {
      if (settled) return
      settled = true
      cancelTimeout(timer)
      resolve()
    }

    void queueImageWarm(src, 0).finally(done)

    const timer = scheduleTimeout(done, timeout)
  })
}

function cacheAudioForPage(pageIndex: number, audioUrl?: string, priority = 1, bookId = content.value?.id || contentId.value || 'temp-book') {
  queueAudioDownload(pageIndex, audioUrl, priority, bookId)
}

// 预加载指定页音频（下载到本地缓存）
function preloadAudio(pageIndex: number, priority = 1, book: PictureBook | null = content.value) {
  if (!book?.pages?.length) return
  if (pageIndex < 0 || pageIndex >= book.pages.length) return

  const page = book.pages[pageIndex]
  cacheAudioForPage(pageIndex, page.audio_url, priority, book.id)
}

// 批量预加载多页音频
function preloadAudioBatch(startIndex: number, count = 3, priority = 1, book: PictureBook | null = content.value) {
  for (let i = startIndex; i < startIndex + count; i++) {
    preloadAudio(i, priority, book)
  }
}

// 等待图片加载完成（事件驱动，替代轮询）
function waitForImageLoad(pageIndex: number, timeout = 5000): Promise<boolean> {
  return new Promise((resolve) => {
    if (imageLoaded.value[pageIndex]) {
      resolve(true)
      return
    }

    let settled = false
    let timer = 0

    const cb = () => {
      if (!settled) {
        settled = true
        cancelTimeout(timer)
        resolve(true)
      }
    }

    timer = scheduleTimeout(() => {
      if (!settled) {
        settled = true
        // Remove callback
        const cbs = imageLoadCallbacks.get(pageIndex)
        if (cbs) {
          const idx = cbs.indexOf(cb)
          if (idx >= 0) cbs.splice(idx, 1)
        }
        console.warn(`[wait] page ${pageIndex + 1} image timeout`)
        resolve(false)
      }
    }, timeout)

    if (!imageLoadCallbacks.has(pageIndex)) {
      imageLoadCallbacks.set(pageIndex, [])
    }
    imageLoadCallbacks.get(pageIndex)!.push(cb)
  })
}

// 等待音频缓存完成（事件驱动，替代轮询）
function waitForAudioCache(pageIndex: number, audioUrl?: string, timeout = 2000, bookId = content.value?.id || contentId.value || 'temp-book'): Promise<string | null> {
  const cacheKey = getAudioCacheKey(pageIndex, audioUrl, bookId)

  return new Promise((resolve) => {
    // 已缓存
    if (audioCache.has(cacheKey)) {
      resolve(audioCache.get(cacheKey)!)
      return
    }

    let settled = false
    let timer = 0

    const cb = () => {
      if (!settled) {
        settled = true
        cancelTimeout(timer)
        // 检查是否真的缓存了（可能是下载失败通知）
        const cached = audioCache.get(cacheKey)
        resolve(cached || null)
      }
    }

    timer = scheduleTimeout(() => {
      if (!settled) {
        settled = true
        const cbs = audioCacheCallbacks.get(cacheKey)
        if (cbs) {
          const idx = cbs.indexOf(cb)
          if (idx >= 0) cbs.splice(idx, 1)
        }
        resolve(null)
      }
    }, timeout)

    if (!audioCacheCallbacks.has(cacheKey)) {
      audioCacheCallbacks.set(cacheKey, [])
    }
    audioCacheCallbacks.get(cacheKey)!.push(cb)
  })
}

function ensureAudioContext() {
  if (audioContext) {
    return audioContext
  }

  try {
    uni.setInnerAudioOption({ obeyMuteSwitch: false, mixWithOther: true })
  } catch (e) { /* 开发工具不支持 */ }

  audioContext = uni.createInnerAudioContext()
  audioContext.volume = 1.0

  audioContext.onCanplay(() => {
    if (currentAudioPage === currentPage.value) {
      audioReady.value = true
      currentAudioDuration = Math.max(currentAudioDuration, Number(audioContext?.duration || 0))
      cancelAudioBootstrapTimer()
    }
  })

  audioContext.onPlay(() => {
    if (currentAudioPage === currentPage.value) {
      audioReady.value = true
      currentAudioStartedOnce = true
      currentAudioDuration = Math.max(currentAudioDuration, Number(audioContext?.duration || 0))
      cancelAudioBootstrapTimer()
    }
  })

  audioContext.onTimeUpdate(() => {
    if (currentAudioPage !== currentPage.value) return

    currentAudioStartedOnce = true
    currentAudioTime = Number(audioContext?.currentTime || 0)
    const duration = Number(audioContext?.duration || 0)
    if (duration > 0) {
      currentAudioDuration = duration
    }
  })

  audioContext.onPause(() => {
    if (currentAudioPage === currentPage.value) {
      audioReady.value = false
    }
  })

  audioContext.onStop(() => {
    audioReady.value = false
    cancelAudioBootstrapTimer()
  })

  audioContext.onEnded(() => {
    cancelAudioBootstrapTimer()
    if (currentAudioPage !== currentPage.value) return
    onAudioEnded()
  })

  audioContext.onError((err: any) => {
    console.error('[绘本音频] 播放错误:', err?.errMsg || err?.errCode || err)
    audioReady.value = false

    if (currentAudioUsesCachedFile && currentAudioNetworkSrc && audioContext && currentAudioPage === currentPage.value && isPlaying.value) {
      audioCache.delete(currentAudioCacheKey)
      currentAudioUsesCachedFile = false
      try { audioContext.stop() } catch (e) { /* ignore */ }
      audioContext.src = currentAudioNetworkSrc
      audioContext.play()
      startAudioBootstrapWatchdog(currentAudioPage, currentAudioRequestId)
      return
    }

    startFallbackTimer(undefined, currentAudioPage, currentAudioRequestId)
  })

  return audioContext
}

// 音频播放 - 优化：复用单一播放器 + 当前页音频优先预热
async function playCurrentPageAudio() {
  if (!content.value?.pages?.length || !isPlaying.value) return

  cancelPageAdvanceTimer()
  cancelAudioBootstrapTimer()
  stopAutoPlay()
  const pageIndex = currentPage.value
  const page = content.value.pages[pageIndex]
  if (!page) return
  const requestId = ++currentAudioRequestId
  currentAudioStartedOnce = false
  currentAudioTime = 0
  currentAudioDuration = Number(page.duration || 0)

  // 不等图片 —— 音频立即开始准备，图片和音频互不阻塞

  // 后台预加载下一页资源（不阻塞当前播放）
  preloadAdjacentImages(pageIndex + 1, 2)
  preloadAudio(pageIndex, 0)
  preloadAudio(pageIndex + 1, 0)
  preloadAudio(pageIndex + 2, 1)

  // 快到最后了，预加载下一本绘本数据
  if (playlist.value.length > 1 && pageIndex >= totalPages.value - 3) {
    void warmUpcomingBook()
  }

  if (page.audio_url) {
    const context = ensureAudioContext()
    audioReady.value = false
    currentAudioPage = pageIndex
    currentAudioCacheKey = getAudioCacheKey(pageIndex, page.audio_url)
    currentAudioNetworkSrc = encodeURI(ensureHttps(page.audio_url))
    currentAudioUsesCachedFile = false
    cacheAudioForPage(pageIndex, page.audio_url, 0)
    startAudioBootstrapWatchdog(pageIndex, requestId)

    // 当前页只给极短的本地缓存等待窗口，未命中就直接流式播放
    const cachedPath = await waitForAudioCache(pageIndex, page.audio_url, 220)

    if (requestId !== currentAudioRequestId || !isPlaying.value || currentPage.value !== pageIndex) {
      return
    }

    let audioSrc = currentAudioNetworkSrc
    if (cachedPath) {
      audioSrc = cachedPath
      currentAudioUsesCachedFile = true
    }

    try { context.stop() } catch (e) { /* ignore */ }
    context.src = audioSrc
    if (isPlaying.value) {
      context.play()
    }
  } else {
    currentAudioPage = -1
    currentAudioCacheKey = ''
    currentAudioNetworkSrc = ''
    currentAudioUsesCachedFile = false
    // 无音频，使用定时器
    startFallbackTimer(undefined, pageIndex, requestId)
  }
}

function pauseCurrentAudio() {
  if (audioContext && currentAudioPage === currentPage.value) {
    try { audioContext.pause() } catch (e) { /* ignore */ }
  }
}

function stopCurrentAudio() {
  cancelPageAdvanceTimer()
  cancelAudioBootstrapTimer()
  stopAutoPlay()
  currentAudioRequestId++
  if (audioContext) {
    try { audioContext.stop() } catch (e) { /* ignore */ }
  }
  audioReady.value = false
  currentAudioStartedOnce = false
  currentAudioTime = 0
  currentAudioDuration = 0
  currentAudioPage = -1
  currentAudioUsesCachedFile = false
  currentAudioCacheKey = ''
  currentAudioNetworkSrc = ''
}

function destroyCurrentAudio() {
  cancelPageAdvanceTimer()
  cancelAudioBootstrapTimer()
  stopAutoPlay()
  currentAudioRequestId++
  if (audioContext) {
    try { audioContext.stop() } catch (e) { /* ignore */ }
    try { audioContext.destroy() } catch (e) { /* ignore */ }
    audioContext = null
  }
  currentAudioStartedOnce = false
  currentAudioTime = 0
  currentAudioDuration = 0
  currentAudioPage = -1
  currentAudioCacheKey = ''
  currentAudioNetworkSrc = ''
  currentAudioUsesCachedFile = false
  audioReady.value = false
}

// 翻到下一页 - 支持顺序播放队列
async function goToNextPage() {
  if (!isPlaying.value) return

  cancelPageAdvanceTimer()
  stopAutoPlay()
  let nextPage = currentPage.value + 1

  if (nextPage >= totalPages.value) {
    // 有播放队列且不止一本 → 切换到下一本
    if (playlist.value.length > 1) {
      await switchToNextBook()
      return
    }
    // 只有一本 → 保持原来的循环行为
    nextPage = 0
    console.log('[绘本] 循环播放：回到第一页')
  }

  // 等待下一页图片加载完成（最多等 3 秒）
  if (!imageLoaded.value[nextPage]) {
    console.log(`[绘本] 等待下一页 ${nextPage + 1} 图片加载...`)
    await waitForImageLoad(nextPage, 3000)
  }

  // 再次检查播放状态
  if (!isPlaying.value) return

  // 重置防重复标记（程序翻页不触发 swiper @change）
  audioStartedForPage = -1
  cardVisible.value = false
  currentPage.value = nextPage
}

// 清理音频临时文件
function cleanupAudioTempFiles(keepBookIds?: Set<string>) {
  audioCache.forEach((tempPath, cacheKey) => {
    const cacheBookId = getBookIdFromAudioCacheKey(cacheKey)
    if (keepBookIds?.has(cacheBookId)) {
      return
    }

    try {
      uni.getFileSystemManager().unlink({
        filePath: tempPath,
        fail: () => { /* silent */ }
      })
    } catch (e) { /* silent */ }
    audioCache.delete(cacheKey)
  })
  if (!keepBookIds || keepBookIds.size === 0) {
    audioDownloading.clear()
  }
  clearPendingAudioDownloads(keepBookIds)
}

async function prepareInitialViewport(targetPage = currentPage.value, excludeIndices?: Set<number>) {
  if (!content.value?.pages?.length) return

  const safePage = clampPageIndex(targetPage)
  preloadAdjacentImages(safePage, 3, excludeIndices)

  const firstPage = content.value.pages[safePage]
  const firstImageReady = Promise.race([
    waitForImageLoad(safePage, INITIAL_VIEWPORT_IMAGE_TIMEOUT).then(() => undefined),
    warmImage(firstPage?.image_thumb_url || firstPage?.image_url, INITIAL_VIEWPORT_IMAGE_TIMEOUT),
    waitMs(INITIAL_VIEWPORT_IMAGE_TIMEOUT)
  ])
  await firstImageReady
}

// 切换到下一本绘本
async function switchToNextBook() {
  const prevIndex = playIndex
  const nextIndex = playIndex + 1
  const playSnapshot = createPlayProgressSnapshot()

  // 播完所有绘本后停止（不循环），立即显示完成界面
  if (nextIndex >= playlist.value.length) {
    console.log(`[绘本] 播放队列全部完成`)
    invalidatePlaySessionRequest()
    resetRetainedAudioBookIds()
    isPlaying.value = false
    showComplete.value = true
    // fire-and-forget：不阻塞 UI
    void flushPlaySnapshot(playSnapshot, true)
    return
  }

  playIndex = nextIndex
  const nextId = playlist.value[playIndex]
  console.log(`[绘本] 切换到下一本: ${nextId} (${playIndex + 1}/${playlist.value.length})`)
  nextBookTitle.value = warmedNextBook?.id === nextId ? warmedNextBook.title || '' : ''
  invalidatePlaySessionRequest()
  imageWarmGeneration++
  warmedImageUrls.clear()
  resetRetainedAudioBookIds([nextId])

  // 立即进入过渡态，缩短首本结束到次本出现的空档
  showTransition.value = true

  // 停止当前播放、清理资源
  isPlaying.value = false
  cardVisible.value = false
  stopAutoPlay()
  stopCurrentAudio()
  destroyCurrentAudio()
  // 主动 resolve 挂起的图片等待回调，避免 5s 超时悬空
  imageLoadCallbacks.forEach(callbacks => callbacks.forEach(cb => cb()))
  imageLoadCallbacks.clear()
  cleanupAudioTempFiles(new Set([nextId]))
  clearAllTimeouts()

  // 清理完成后再启动后台上报和下一本预热，避免新预热任务被旧 timeout 清空
  void flushPlaySnapshot(playSnapshot, true)
  const nextBookPromise = warmedNextBook?.id === nextId
    ? Promise.resolve(warmedNextBook)
    : warmUpcomingBook()

  try {
    const nextBook = await nextBookPromise
    if (isUnmounted) return
    if (!nextBook?.pages?.length) throw new Error('无效内容')

    nextBookTitle.value = nextBook.title || ''
    const entryWarmTask = warmedNextBook?.id === nextId && warmedNextBookReadyTask
      ? warmedNextBookReadyTask
      : warmBookEntryAssets(nextBook)

    const transitionDelay = waitMs(warmedNextBook?.id === nextId ? 240 : 420)
    const entryReady = Promise.race([
      entryWarmTask.catch(() => { /* silent */ }),
      waitMs(warmedNextBook?.id === nextId ? 260 : 520)
    ])

    await Promise.all([transitionDelay, entryReady])
    if (isUnmounted) return

    // 先重置状态，再设置新内容
    imageLoaded.value = new Array(nextBook.pages.length).fill(false)
    imageRetryCount.value = new Array(nextBook.pages.length).fill(0)
    imagePreloading.clear()
    imageLoadCallbacks.clear()
    audioStartedForPage = -1
    // isPlaying 在 content 之前设为 true，确保 onImageLoad 能立即触发音频
    isPlaying.value = true

    // 设置新内容（触发 swiper 重新渲染，图片开始加载）
    contentId.value = nextId
    content.value = nextBook
    currentPage.value = 0
    playHistoryId.value = ''
    playStartTime.value = 0
    showTransition.value = false
    warmedNextBook = null
    warmedNextBookReadyTask = null
    nextBookWarmTask = null
    resetRetainedAudioBookIds()

    // nextTick + 小延迟确保原生层 swiper DOM 就绪
    await nextTick()
    await waitMs(24)
    if (isUnmounted) return

    // 图片已经通过模板开始加载，追加预加载后续页面
    await prepareInitialViewport(0, new Set([0, 1]))
    startPlaySession()
    requestCurrentPagePlayback()
  } catch (e) {
    if (isUnmounted) return
    console.error('[绘本] 切换失败，降级为当前绘本循环', e)
    audioDownloading.clear()
    clearPendingAudioDownloads()
    clearAllTimeouts()
    playIndex = prevIndex
    showTransition.value = false
    isPlaying.value = true
    currentPage.value = 0
    resetRetainedAudioBookIds()
    requestCurrentPagePlayback()
    uni.showToast({ title: '加载下一本失败', icon: 'none' })
  }
}

function onAudioEnded() {
  if (!isPlaying.value) return

  // 短暂延迟后翻页
  schedulePageAdvance(600, currentPage.value, currentAudioRequestId)
}

function startFallbackTimer(delayMs?: number, expectedPage = currentPage.value, requestId = currentAudioRequestId) {
  cancelPageAdvanceTimer()
  cancelAudioBootstrapTimer()
  stopAutoPlay()
  if (isUnmounted || !content.value?.pages?.length || !isPlaying.value) return

  const page = content.value.pages[expectedPage]
  const duration = delayMs ?? getFallbackDelay(page)

  autoPlayTimer = scheduleTimeout(() => {
    autoPlayTimer = null
    if (!isPlaying.value || loading.value || showTransition.value) return
    if (expectedPage !== currentPage.value) return
    if (requestId !== currentAudioRequestId) return
    goToNextPage()
  }, duration)
}

function stopAutoPlay() {
  if (autoPlayTimer) {
    cancelTimeout(autoPlayTimer)
    autoPlayTimer = null
  }
}

interface PlayProgressSnapshot {
  playHistoryId: string
  contentId: string
  currentPage: number
  playStartTime: number
}

function createPlayProgressSnapshot(): PlayProgressSnapshot | null {
  if (!playHistoryId.value || !contentId.value) {
    return null
  }

  return {
    playHistoryId: playHistoryId.value,
    contentId: contentId.value,
    currentPage: currentPage.value,
    playStartTime: playStartTime.value
  }
}

async function flushPlaySnapshot(snapshot: PlayProgressSnapshot | null, markComplete = false) {
  if (!snapshot?.playHistoryId) return

  const now = Date.now()
  const timeSpent = Math.max(0, Math.round((now - snapshot.playStartTime) / 1000))

  try {
    await updateProgress(snapshot.playHistoryId, snapshot.currentPage + 1, timeSpent)

    uni.setStorageSync(`play_progress_${snapshot.contentId}`, {
      page: snapshot.currentPage,
      time: timeSpent,
      updatedAt: now
    })
  } catch (e) {
    // 静默失败，已本地缓存
  }

  if (markComplete) {
    try { await completePlay(snapshot.playHistoryId) } catch (e) { /* ignore */ }
    // 播放完成后清除本地进度，下次打开从头开始
    uni.removeStorageSync(`play_progress_${snapshot.contentId}`)
  }
}

// 进度更新
async function updatePlayProgress(force = false, snapshot?: PlayProgressSnapshot | null) {
  const effectiveSnapshot = snapshot || createPlayProgressSnapshot()
  if (!effectiveSnapshot?.playHistoryId) return

  const now = Date.now()
  if (!force && now - lastUpdateTime.value < UPDATE_INTERVAL) return
  lastUpdateTime.value = now

  await flushPlaySnapshot(effectiveSnapshot, false)
}

// 完成
async function handleComplete() {
  isPlaying.value = false
  stopAutoPlay()
  showComplete.value = true

  if (playHistoryId.value) {
    try { await completePlay(playHistoryId.value) } catch (e) { /* ignore */ }
  }

  // 不在这里结束会话，让儿童模式页面统一管理

  // 延长等待时间，给用户分享海报的机会
  // 保存定时器引用，以便在页面销毁或用户主动关闭时清除
  cancelTimeout(completeTimer)
  completeTimer = scheduleTimeout(() => {
    if (showComplete.value && !generatingPoster.value) {
      uni.navigateBack()
    }
  }, 8000)
}

// 关闭完成界面
function closeComplete() {
  if (generatingPoster.value) return
  if (completeTimer) {
    cancelTimeout(completeTimer)
    completeTimer = null
  }
  uni.navigateBack()
}

// 互动
async function handleInteraction(page: PictureBookPage, pageIndex: number) {
  if (!page.interaction || !playHistoryId.value) return

  showInteraction.value = false
  const startTime = Date.now()

  try {
    await submitInteraction({
      play_history_id: playHistoryId.value,
      page_number: pageIndex + 1,
      interaction_type: page.interaction.type,
      response_data: { completed: true },
      response_time_ms: Date.now() - startTime
    })

    uni.showToast({ title: '太棒了！', icon: 'success' })
  } catch (e) { /* ignore */ }
}


function handleClose() {
  invalidatePlaySessionRequest()
  resetRetainedAudioBookIds()
  isPlaying.value = false
  stopAutoPlay()
  stopCurrentAudio()
  destroyCurrentAudio()
  cancelTimeout(resumePlayTimer)
  resumePlayTimer = null
  if (completeTimer) {
    cancelTimeout(completeTimer)
    completeTimer = null
  }
  // 不在这里结束会话，让儿童模式页面统一管理
  uni.navigateBack()
}

// 生成分享海报
async function handleSharePoster() {
  if (!content.value || generatingPoster.value) return

  generatingPoster.value = true
  uni.showLoading({ title: '生成海报中...', mask: true })

  try {
    const posterPath = await generatePoster('posterCanvas', {
      title: content.value.title || '童话绘本',
      coverUrl: content.value.pages?.[0]?.image_url || content.value.cover_url || '',
      childName: childStore.currentChild?.name || '宝贝',
      theme: content.value.theme_topic || ''
    }, instance)

    uni.hideLoading()

    // 保存到相册
    await savePosterToAlbum(posterPath)
    uni.showToast({ title: '已保存到相册', icon: 'success' })
  } catch (e: any) {
    uni.hideLoading()
    console.error('[海报生成失败]', e)
    uni.showToast({
      title: e.message || '生成失败，请重试',
      icon: 'none'
    })
  } finally {
    generatingPoster.value = false
  }
}

// 加载内容 - 优化：优先使用临时存储
async function loadContent() {
  // 1. 优先从临时存储读取（刚生成的绘本，最快）
  const tempBook = uni.getStorageSync('temp_picture_book')
  if (tempBook && (!contentId.value || tempBook.id === contentId.value) && tempBook.pages?.length) {
    console.log('[loadContent] 使用临时存储数据')
    content.value = tempBook
    contentStore.primeContentCache(tempBook)
    uni.removeStorageSync('temp_picture_book')
    perf.measure('数据加载（临时存储）', 'pageLoad')
    await initAfterLoad()
    loading.value = false
    requestCurrentPagePlayback()
    return
  } else if (tempBook && contentId.value && tempBook.id !== contentId.value) {
    uni.removeStorageSync('temp_picture_book')
  }

  // 2. 使用 store 中的数据（从生成页跳转，需要 ID 匹配或无 ID 参数）
  // 修复：只有当 store 中的内容 ID 与 URL 参数 ID 匹配时才使用缓存
  const storeContent = contentId.value
    ? contentStore.getCachedContent(contentId.value)
    : (contentStore.currentContent as PictureBook | null)
  if (storeContent && (!contentId.value || storeContent.id === contentId.value)) {
    console.log('[loadContent] 使用 store 数据, ID:', storeContent.id)
    content.value = storeContent
    perf.measure('数据加载（Store 缓存）', 'pageLoad')
    await initAfterLoad()
    loading.value = false
    requestCurrentPagePlayback()
    return
  }

  // 3. 从 API 加载
  if (!contentId.value) {
    loading.value = false
    return
  }

  try {
    content.value = await contentStore.fetchContentDetail(contentId.value)
    perf.measure('API 响应时间', 'pageLoad')
    await initAfterLoad()
    loading.value = false
    requestCurrentPagePlayback()
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
    scheduleTimeout(() => uni.navigateBack(), 1500)
  } finally {
    if (!content.value?.pages?.length) {
      loading.value = false
    }
  }
}

// 加载后初始化
async function initAfterLoad() {
  if (!content.value?.pages?.length) return

  // Initialize state
  activeBookToken++
  imageWarmGeneration++
  hasLocalProgress = false
  invalidatePlaySessionRequest()
  resetRetainedAudioBookIds()
  currentPage.value = getStoredResumePage()
  imageLoaded.value = new Array(content.value.pages.length).fill(false)
  imageRetryCount.value = new Array(content.value.pages.length).fill(0)
  imagePreloading.clear()
  warmedImageUrls.clear()
  clearPendingAudioDownloads()
  // 不 clear audioCache —— switchToNextBook 已经预缓存了前 2 页音频
  imageLoadCallbacks.clear()
  audioCacheCallbacks.clear()
  audioStartedForPage = -1
  playHistoryId.value = ''
  playStartTime.value = 0
  cardVisible.value = false
  showPauseOverlay.value = false
  cancelPageAdvanceTimer()
  cancelAudioBootstrapTimer()
  stopAutoPlay()

  console.log(`[book] start preloading, ${content.value.pages.length} pages total`)

  await nextTick()

  // 首屏资源优先预热，减少首图和首句旁白等待
  await prepareInitialViewport(currentPage.value)

  // Start play session (non-blocking)
  startPlaySession()

  // First-time hint
  const hasSeenHint = uni.getStorageSync('storybook_hint_seen')
  if (!hasSeenHint) {
    showSwipeHint.value = true
    scheduleTimeout(() => {
      showSwipeHint.value = false
      uni.setStorageSync('storybook_hint_seen', true)
    }, 3000)
  }
}

async function startPlaySession() {
  if (!childStore.currentChild || !content.value) return

  // 防御性检查：content.id 可能为 undefined（后端返回数据不完整）
  if (!content.value.id) {
    console.warn('[startPlaySession] 缺少 content.id，跳过播放会话创建')
    return
  }

  const requestToken = playSessionRequestToken
  const expectedContentId = content.value.id

  try {
    const res = await startPlay(childStore.currentChild.id, expectedContentId, 'picture_book')
    if (isUnmounted || requestToken !== playSessionRequestToken || content.value?.id !== expectedContentId) {
      return
    }

    playHistoryId.value = res.play_history_id
    playStartTime.value = Date.now()

    // 断点续播：仅当本地无进度记录且当前在第0页时，才用后端的断点位置
    // 额外检查：如果恢复页是最后一页，说明上次已播完，从头开始
    if (res.resumed_from?.page && res.resumed_from.page > 0 && !hasLocalProgress && currentPage.value === 0 && audioStartedForPage < 0 && currentAudioRequestId === 0) {
      const resumeIndex = clampPageIndex(res.resumed_from.page - 1)
      if (resumeIndex < totalPages.value - 1) {
        currentPage.value = resumeIndex
        cardVisible.value = false
        audioStartedForPage = -1
        preloadAdjacentImages(currentPage.value, 3)
        preloadAudioBatch(currentPage.value, 2, 0)
        requestCurrentPagePlayback(currentPage.value)
      }
    }
  } catch (e) {
    console.warn('[startPlaySession] 播放会话创建失败')
  }
}

// 生命周期
onLoad((options) => {
  // 性能监控：页面加载开始
  perf.clear()
  perf.mark('pageLoad')

  contentId.value = options?.id || ''

  // 读取播放队列
  const storedPlaylist = uni.getStorageSync('picture_book_playlist')
  if (storedPlaylist && Array.isArray(storedPlaylist) && storedPlaylist.length > 1) {
    const idx = storedPlaylist.indexOf(contentId.value)
    if (idx >= 0) {
      playlist.value = storedPlaylist
      playIndex = idx
      console.log(`[绘本] 播放队列: ${storedPlaylist.length} 本, 当前第 ${playIndex + 1} 本`)
    }
    // ID 不在列表中则不使用队列模式，保持单本循环
  }

  const sysInfo = uni.getSystemInfoSync()
  statusBarHeight.value = sysInfo.statusBarHeight || 44

  if (options?.autoplay === '1') {
    isPlaying.value = true
  }
})

onMounted(() => {
  loadContent()
})

onShareAppMessage(() => ({
  title: content.value?.title || '来看这个有趣的绘本',
  path: `/pages/play/picture-book?id=${contentId.value}`,
  imageUrl: content.value?.cover_url || ''
}))

onShareTimeline(() => ({
  title: content.value?.title || '来看这个有趣的绘本',
  query: `id=${contentId.value}`,
  imageUrl: content.value?.cover_url || ''
}))

onUnmounted(() => {
  isUnmounted = true
  activeBookToken++
  imageWarmGeneration++
  invalidatePlaySessionRequest()
  resetRetainedAudioBookIds()
  updatePlayProgress(true)
  stopAutoPlay()
  cancelTimeout(completeTimer)
  completeTimer = null
  cancelTimeout(resumePlayTimer)
  resumePlayTimer = null
  clearAllTimeouts()
  destroyCurrentAudio()
  imagePreloading.clear()
  warmedImageUrls.clear()
  imageLoadCallbacks.forEach(callbacks => callbacks.forEach(cb => cb()))
  imageLoadCallbacks.clear()
  audioCacheCallbacks.clear()
  cleanupAudioTempFiles()
})
</script>

<style lang="scss" scoped>
// ============================================
// 童话故事书风格 - Storybook Whimsy
// ============================================

// 色彩系统 - 温暖童话色
$story-cream: #FFF8F0;
$story-warm: #FFE4C9;
$story-gold: #FFB347;
$story-rose: #FFB5BA;
$story-sage: #B8D4C3;
$story-night: #2D3047;
$story-text: #4A4458;

// 字体 - 如果没有自定义字体，使用系统圆角字体
$font-story: -apple-system, 'PingFang SC', 'Hiragino Sans GB', sans-serif;

.storybook {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
  overflow: hidden;
}

// 魔法背景星星
.magic-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.sparkle {
  position: absolute;
  background: radial-gradient(circle, rgba(255, 215, 0, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0.5;
}

// 故事轮播
.story-swiper {
  width: 100%;
  height: 100%;
  z-index: 1;
}

.story-page {
  width: 100%;
  height: 100%;
  position: relative;
}

// 全屏故事图片
.story-image-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.story-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

// 缩略图样式 - 模糊放大背景
.story-image-thumb {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  filter: blur(20rpx);
  transform: scale(1.05);
  z-index: 1;
}

// 原图样式 - 淡入效果
.story-image-full {
  position: relative;
  z-index: 2;
  opacity: 0;
  transition: opacity 0.4s ease-in-out;

  &.loaded {
    opacity: 1;
  }
}

// 图片占位 - 优雅的闪烁效果
.image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #2d3047 0%, #1a1a2e 100%);
  overflow: hidden;
}

.placeholder-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.05) 50%,
    transparent 100%
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  to { left: 100%; }
}

// 故事文字卡片 - 童话书页风格
.story-card {
  position: absolute;
  bottom: 32rpx;
  left: 24rpx;
  right: 24rpx;
  margin-bottom: env(safe-area-inset-bottom);
  background: linear-gradient(
    165deg,
    #FDF8F3 0%,
    #F9F3EC 30%,
    #FBF6F0 70%,
    #F5EEE6 100%
  );
  border-radius: 24rpx;
  padding: 40rpx 36rpx 32rpx;
  transform: translateY(60rpx) scale(0.95);
  opacity: 0;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow:
    0 8rpx 32rpx rgba(0, 0, 0, 0.25),
    0 2rpx 8rpx rgba(0, 0, 0, 0.15),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
  overflow: hidden;

  &.visible {
    transform: translateY(0) scale(1);
    opacity: 1;
    animation: gentle-float 4s ease-in-out infinite 0.6s;
  }
}

@keyframes gentle-float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-4rpx) scale(1); }
}

// 书页装饰角
.page-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.decor-corner {
  position: absolute;
  width: 48rpx;
  height: 48rpx;
  opacity: 0.4;

  &::before, &::after {
    content: '';
    position: absolute;
    background: linear-gradient(135deg, #C9A86C 0%, #E8D5B7 100%);
  }

  &.corner-tl {
    top: 12rpx;
    left: 12rpx;
    &::before { top: 0; left: 0; width: 20rpx; height: 3rpx; border-radius: 2rpx; }
    &::after { top: 0; left: 0; width: 3rpx; height: 20rpx; border-radius: 2rpx; }
  }

  &.corner-tr {
    top: 12rpx;
    right: 12rpx;
    &::before { top: 0; right: 0; width: 20rpx; height: 3rpx; border-radius: 2rpx; }
    &::after { top: 0; right: 0; width: 3rpx; height: 20rpx; border-radius: 2rpx; }
  }

  &.corner-bl {
    bottom: 12rpx;
    left: 12rpx;
    &::before { bottom: 0; left: 0; width: 20rpx; height: 3rpx; border-radius: 2rpx; }
    &::after { bottom: 0; left: 0; width: 3rpx; height: 20rpx; border-radius: 2rpx; }
  }

  &.corner-br {
    bottom: 12rpx;
    right: 12rpx;
    &::before { bottom: 0; right: 0; width: 20rpx; height: 3rpx; border-radius: 2rpx; }
    &::after { bottom: 0; right: 0; width: 3rpx; height: 20rpx; border-radius: 2rpx; }
  }
}

// 书签装饰
.page-bookmark {
  position: absolute;
  top: -8rpx;
  right: 40rpx;
  width: 44rpx;
  height: 56rpx;
  background: linear-gradient(180deg, #E85D4A 0%, #D64A3A 100%);
  border-radius: 0 0 8rpx 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(232, 93, 74, 0.3);

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    border-left: 22rpx solid transparent;
    border-right: 22rpx solid transparent;
    border-bottom: 12rpx solid #FDF8F3;
  }

  .bookmark-icon {
    font-size: 20rpx;
    position: relative;
    top: -4rpx;
  }
}

// 纸张纹理
.page-texture {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(ellipse at 20% 80%, rgba(200, 180, 140, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(180, 160, 120, 0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(220, 200, 160, 0.04) 0%, transparent 70%);
  pointer-events: none;
}

.card-content {
  position: relative;
  z-index: 1;
}

.text-wrapper {
  position: relative;
}

.story-text {
  display: block;
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 34rpx;
  line-height: 2;
  color: #3D3425;
  letter-spacing: 1.5rpx;
  text-align: center;
  text-shadow: 0 1rpx 0 rgba(255, 255, 255, 0.8);
}

// 页码装饰
.page-number {
  display: flex;
  justify-content: center;
  margin-top: 20rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid rgba(201, 168, 108, 0.2);

  text {
    font-size: 22rpx;
    color: #B8A88A;
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    letter-spacing: 4rpx;
  }
}

// 互动提示 - 童话书页配色
.interaction-hint {
  display: inline-flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 24rpx;
  padding: 18rpx 32rpx;
  background: linear-gradient(135deg, #C9A86C 0%, #D4B87A 100%);
  border-radius: 100rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.3);
  box-shadow:
    0 4rpx 16rpx rgba(201, 168, 108, 0.4),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
  animation: hint-pulse 2s ease-in-out infinite;
}

@keyframes hint-pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4rpx 16rpx rgba(201, 168, 108, 0.4), inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 6rpx 24rpx rgba(201, 168, 108, 0.6), inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
  }
}

.hint-icon {
  font-size: 28rpx;
}

.hint-text {
  font-size: 26rpx;
  color: #3D3425;
  font-weight: 600;
  letter-spacing: 1rpx;
}

// 极简顶部
.minimal-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx;
  z-index: 10;
}

.back-touch {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  width: 44rpx;
  height: 44rpx;
  position: relative;
}

.back-line {
  position: absolute;
  left: 8rpx;
  width: 24rpx;
  height: 3rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 2rpx;

  &.back-line-1 {
    top: 15rpx;
    transform: rotate(-45deg);
    transform-origin: left center;
  }

  &.back-line-2 {
    bottom: 15rpx;
    transform: rotate(45deg);
    transform-origin: left center;
  }
}

// 播放状态指示器
.play-indicator {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 16rpx;
}

.indicator-bar {
  width: 6rpx;
  height: 24rpx;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 3rpx;
  transition: all 0.3s ease;
}

.play-indicator.playing .indicator-bar {
  background: $story-gold;
  animation: sound-wave 0.8s ease-in-out infinite;

  &:nth-child(1) { animation-delay: 0s; }
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

@keyframes sound-wave {
  0%, 100% { height: 16rpx; }
  50% { height: 32rpx; }
}

// 页码指示器
.page-dots {
  position: absolute;
  bottom: calc(200rpx + env(safe-area-inset-bottom));
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 16rpx;
  z-index: 10;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transition: all 0.3s ease;

  &.passed {
    background: rgba($story-gold, 0.5);
  }

  &.active {
    width: 36rpx;
    border-radius: 6rpx;
    background: $story-gold;
  }
}

// 滑动提示
.swipe-hint {
  position: absolute;
  bottom: calc(320rpx + env(safe-area-inset-bottom));
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  animation: hint-float 2s ease-in-out infinite;
  z-index: 20;
}

@keyframes hint-float {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-20rpx); }
}

.hint-hand {
  font-size: 60rpx;
  animation: swipe-motion 1.5s ease-in-out infinite;
}

@keyframes swipe-motion {
  0%, 100% { transform: translateX(-20rpx); }
  50% { transform: translateX(20rpx); }
}

.hint-label {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(0, 0, 0, 0.5);
  padding: 8rpx 24rpx;
  border-radius: 20rpx;
}

// 暂停遮罩
.pause-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 32rpx;
  z-index: 30;
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.pause-icon {
  display: flex;
  gap: 20rpx;
}

.pause-bar {
  width: 16rpx;
  height: 80rpx;
  background: $story-cream;
  border-radius: 8rpx;
}

.pause-text {
  font-size: 30rpx;
  color: rgba(255, 255, 255, 0.8);
}

// 切换绘本过渡
.transition-screen {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(160deg, #1a1a2e, #16213e);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fade-in 0.3s ease;
}

.transition-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.transition-icon {
  font-size: 80rpx;
  animation: gentle-float 2s ease-in-out infinite;
}

.transition-title {
  font-size: 36rpx;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 4rpx;
}

.transition-book {
  font-size: 40rpx;
  color: $story-cream;
  font-weight: 600;
  max-width: 80%;
  text-align: center;
}

// 加载屏幕 - 书本动画
.loading-screen {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(160deg, #1a1a2e, #16213e);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 48rpx;
  z-index: 100;
}

.book-loader {
  width: 120rpx;
  height: 100rpx;
  position: relative;
  perspective: 600rpx;
}

.book-page {
  position: absolute;
  width: 50%;
  height: 100%;
  background: $story-cream;
  transform-origin: left center;

  &.page-left {
    left: 0;
    border-radius: 4rpx 0 0 4rpx;
  }

  &.page-right {
    right: 0;
    border-radius: 0 4rpx 4rpx 0;
    animation: page-flip 1.2s ease-in-out infinite;
    transform-style: preserve-3d;
  }
}

@keyframes page-flip {
  0%, 100% { transform: rotateY(0deg); }
  50% { transform: rotateY(-160deg); }
}

.book-spine {
  position: absolute;
  left: 50%;
  top: 0;
  width: 8rpx;
  height: 100%;
  background: $story-gold;
  transform: translateX(-50%);
  border-radius: 4rpx;
}

.loading-text {
  font-size: 30rpx;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 2rpx;
}

// 完成屏幕
.complete-screen {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(160deg, #1a1a2e, #16213e);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 32rpx;
  z-index: 100;
  animation: fade-in 0.5s ease;
}

.complete-stars {
  display: flex;
  gap: 16rpx;
}

.star {
  font-size: 60rpx;
  animation: star-pop 0.5s ease backwards;
}

@keyframes star-pop {
  0% { transform: scale(0) rotate(-180deg); opacity: 0; }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

.complete-title {
  font-size: 48rpx;
  color: $story-cream;
  font-weight: 600;
  letter-spacing: 4rpx;
}

.complete-subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.6);
}

.complete-actions {
  display: flex;
  gap: 24rpx;
  margin-top: 48rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 40rpx;
  border-radius: 100rpx;
  transition: transform 0.2s ease;

  &:active {
    transform: scale(0.95);
  }
}

.share-btn {
  background: linear-gradient(135deg, $story-gold, #FF9500);
  box-shadow: 0 8rpx 24rpx rgba($story-gold, 0.4);
}

.close-btn {
  background: rgba(255, 255, 255, 0.15);
  border: 2rpx solid rgba(255, 255, 255, 0.3);

  .btn-text {
    color: rgba(255, 255, 255, 0.9);
  }
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: 28rpx;
  font-weight: 600;
  color: $story-night;
}

// 时间提醒
</style>
