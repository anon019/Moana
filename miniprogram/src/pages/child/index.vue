<template>
  <view class="wonderland">
    <!-- 梦幻背景层 -->
    <view class="bg-layer">
      <view class="bg-gradient"></view>
      <view class="clouds">
        <view class="cloud c1"></view>
        <view class="cloud c2"></view>
        <view class="cloud c3"></view>
      </view>
      <view class="stars">
        <view v-for="i in 12" :key="i" class="star" :class="'s' + i"></view>
      </view>
      <view class="rainbow"></view>
    </view>

    <!-- 主播放区域 - 魔法电视机 -->
    <view class="magic-tv" v-if="currentContent" @tap="startPlay">
      <view class="tv-frame">
        <view class="tv-antenna left"></view>
        <view class="tv-antenna right"></view>
        <view class="tv-screen">
          <image
            v-if="currentContent.cover_url"
            :src="currentContent.cover_url"
            mode="aspectFill"
            class="screen-image"
          />
          <view v-else class="screen-placeholder">
            <text class="placeholder-emoji">{{ getContentEmoji(currentContent) }}</text>
          </view>
          <!-- 播放按钮在屏幕中心 -->
          <view class="play-button">
            <view class="play-pulse"></view>
            <view class="play-icon">▶</view>
          </view>
          <!-- 类型角标 -->
          <view class="screen-badge" :class="getContentTypeClass(currentContent)">
            {{ getContentTypeBadge(currentContent) }}
          </view>
        </view>
        <view class="tv-controls">
          <view class="tv-dial"></view>
          <view class="tv-speaker">
            <view class="speaker-line" v-for="i in 5" :key="i"></view>
          </view>
        </view>
      </view>
      <!-- 标题在电视机下方 -->
      <view class="tv-title">
        <text class="title-text">{{ currentContent.title }}</text>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-else class="empty-magic">
      <view class="empty-wand">
        <text>🪄</text>
      </view>
      <text class="empty-title">等待魔法内容</text>
      <text class="empty-hint">请家长添加绘本或儿歌</text>
    </view>

    <!-- 素材选择区 - 旋转木马 -->
    <view class="carousel-section" v-if="allContentList.length > 0">
      <view class="carousel-header">
        <view class="header-star">⭐</view>
        <text class="header-title">选一个玩具</text>
        <view class="header-star">⭐</view>
      </view>

      <!-- 类型筛选按钮 -->
      <view class="type-filter">
        <view
          class="filter-btn"
          :class="{ active: currentFilter === 'all' }"
          @tap="setFilter('all')"
        >
          <text class="filter-icon">🎁</text>
          <text class="filter-label">全部</text>
        </view>
        <view
          class="filter-btn"
          :class="{ active: currentFilter === 'picture_book' }"
          @tap="setFilter('picture_book')"
        >
          <text class="filter-icon">📚</text>
          <text class="filter-label">绘本</text>
        </view>
        <view
          class="filter-btn"
          :class="{ active: currentFilter === 'nursery_rhyme' }"
          @tap="setFilter('nursery_rhyme')"
        >
          <text class="filter-icon">🎵</text>
          <text class="filter-label">儿歌</text>
        </view>
        <view
          class="filter-btn"
          :class="{ active: currentFilter === 'video' }"
          @tap="setFilter('video')"
        >
          <text class="filter-icon">🎬</text>
          <text class="filter-label">视频</text>
        </view>
      </view>

      <scroll-view
        class="carousel-track"
        scroll-x
        :show-scrollbar="false"
        enhanced
        :scroll-with-animation="true"
      >
        <view class="carousel-inner">
          <view
            v-for="(item, index) in filteredContentList"
            :key="item.id"
            class="carousel-item"
            :class="[
              getContentTypeClass(item),
              { active: currentContent?.id === item.id }
            ]"
            :style="{ animationDelay: index * 0.1 + 's' }"
            @tap="selectContent(item)"
          >
            <!-- 玩具盒子 -->
            <view class="toy-box">
              <view class="box-lid"></view>
              <view class="box-front">
                <view class="toy-icon">
                  <text>{{ getContentEmoji(item) }}</text>
                </view>
              </view>
              <view class="box-shine"></view>
            </view>
            <!-- 标签 -->
            <view class="item-label">
              <text>{{ formatTitle(item.title) }}</text>
            </view>
            <!-- 选中星星 -->
            <view class="select-star" v-if="currentContent?.id === item.id">
              <text>⭐</text>
            </view>
          </view>
        </view>
      </scroll-view>

      <!-- 滚动提示 -->
      <view class="scroll-hint">
        <text>👈 滑动看更多 👉</text>
      </view>
    </view>

    <!-- 底部退出区域 - 魔法按钮 -->
    <view class="exit-zone" @tap="exitChildMode">
      <view class="exit-button">
        <view class="exit-glow"></view>
        <view class="exit-inner">
          <text class="exit-icon">👋</text>
          <text class="exit-text">返回</text>
        </view>
      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useChildStore } from '@/stores/child'
import { useContentStore } from '@/stores/content'
import type { PictureBook } from '@/api/content'

const childStore = useChildStore()
const contentStore = useContentStore()

type PlayableContent = PictureBook & {
  content_type?: string
}

// 状态
const currentContent = ref<PlayableContent | null>(null)
const allContentList = ref<PlayableContent[]>([])
const currentFilter = ref<'all' | 'picture_book' | 'nursery_rhyme' | 'video'>('all')
const preferredContentId = ref('')
const contentCatalogReady = ref(false)
let loadContentTask: Promise<void> | null = null
let backgroundCatalogTask: Promise<void> | null = null
let contentLoadGeneration = 0

// 筛选后的内容列表
const filteredContentList = computed(() => {
  if (currentFilter.value === 'all') {
    return allContentList.value
  }
  return allContentList.value.filter(item => item.content_type === currentFilter.value)
})

// 设置筛选类型
function setFilter(type: 'all' | 'picture_book' | 'nursery_rhyme' | 'video') {
  currentFilter.value = type
  // 如果当前选中的内容不在筛选结果中，选择筛选后的第一个
  if (filteredContentList.value.length > 0) {
    const currentInList = filteredContentList.value.find(item => item.id === currentContent.value?.id)
    if (!currentInList) {
      currentContent.value = filteredContentList.value[0]
      warmContentSelection(currentContent.value)
    }
  }
}

function selectContent(item: PlayableContent) {
  currentContent.value = item
  warmContentSelection(item)
}

function warmContentSelection(item: PlayableContent | null | undefined) {
  if (!item?.id) return

  contentStore.primeContentCache(item)

  const playable = item as any
  if (playable.pages?.length || playable.audio_url || playable.video_url) {
    return
  }

  void contentStore.fetchContentDetail(item.id).then((detail) => {
    const index = allContentList.value.findIndex(entry => entry.id === detail.id)
    if (index !== -1) {
      const merged = {
        ...allContentList.value[index],
        ...detail,
        content_type: inferContentType({ ...allContentList.value[index], ...detail })
      }
      allContentList.value[index] = merged
      if (currentContent.value?.id === detail.id) {
        currentContent.value = merged
      }
    }
  }).catch(() => {
    /* silent */
  })
}

function startPlay() {
  if (!currentContent.value) return

  contentStore.primeContentCache(currentContent.value)
  const content = (contentStore.getCachedContent(currentContent.value.id) || currentContent.value) as any
  const type = content.content_type || 'picture_book'

  if (type === 'picture_book' && content.pages?.length) {
    uni.setStorageSync('temp_picture_book', content)
  } else if (type === 'nursery_rhyme' && content.audio_url) {
    uni.setStorageSync('temp_nursery_rhyme', content)
  } else if (type === 'video' && content.video_url) {
    uni.setStorageSync('temp_video', content)
  }

  // 绘本：存储播放队列，支持顺序播放
  if (type === 'picture_book') {
    if (contentCatalogReady.value) {
      const bookIds = allContentList.value
        .filter(item => (item as any).content_type === 'picture_book')
        .map(item => item.id)
      uni.setStorageSync('picture_book_playlist', bookIds)
    } else {
      uni.removeStorageSync('picture_book_playlist')
    }
  }

  const playerMap: Record<string, string> = {
    'picture_book': '/pages/play/picture-book',
    'nursery_rhyme': '/pages/play/nursery-rhyme',
    'video': '/pages/play/video'
  }

  const playerPath = playerMap[type] || '/pages/play/picture-book'

  uni.navigateTo({
    url: `${playerPath}?id=${content.id}&autoplay=1`
  })
}

function getContentEmoji(item: any): string {
  const type = item.content_type || 'picture_book'
  const emojiMap: Record<string, string> = {
    'picture_book': '📚',
    'nursery_rhyme': '🎵',
    'video': '🎬'
  }
  return emojiMap[type] || '📚'
}

function getContentTypeClass(item: any): string {
  const type = item.content_type || 'picture_book'
  return `type-${type.replace('_', '-')}`
}

function getContentTypeBadge(item: any): string {
  const type = item.content_type || 'picture_book'
  const badgeMap: Record<string, string> = {
    'picture_book': '绘本',
    'nursery_rhyme': '儿歌',
    'video': '视频'
  }
  return badgeMap[type] || '绘本'
}

function formatTitle(title: string): string {
  if (!title) return ''
  const match = title.match(/的(.+)/)
  if (match && match[1].length > 2) {
    return match[1].slice(0, 5)
  }
  return title.slice(0, 5)
}

function exitChildMode() {
  if (getCurrentPages().length > 1) {
    uni.navigateBack()
    return
  }

  uni.switchTab({ url: '/pages/index/index' })
}


// 推断内容类型（与内容库完全一致）
function inferContentType(item: any): string {
  if (item.content_type) return item.content_type
  if (item.video_url) return 'video'
  if (item.audio_url && !item.pages) return 'nursery_rhyme'
  return 'picture_book'
}

function toPlayableContent(item: PictureBook): PlayableContent {
  return {
    ...item,
    content_type: inferContentType(item)
  }
}

function mergeContentBatch(items: PictureBook[]) {
  if (!items.length) return

  const merged = new Map(allContentList.value.map(item => [item.id, item]))
  items.forEach(item => {
    const playable = toPlayableContent(item)
    merged.set(playable.id, {
      ...(merged.get(playable.id) || {}),
      ...playable
    })
  })
  allContentList.value = Array.from(merged.values())
}

function syncSelectedContent() {
  const targetId = preferredContentId.value || currentContent.value?.id || ''
  if (targetId) {
    const matched = allContentList.value.find(item => item.id === targetId)
    if (matched) {
      currentContent.value = matched
      warmContentSelection(matched)
      return
    }
  }

  if (!currentContent.value && allContentList.value.length > 0) {
    currentContent.value = allContentList.value[0]
    warmContentSelection(currentContent.value)
    return
  }

  if (currentContent.value) {
    warmContentSelection(currentContent.value)
  }
}

async function loadContent() {
  if (loadContentTask) {
    return loadContentTask
  }

  const generation = ++contentLoadGeneration
  contentCatalogReady.value = false

  const task = (async () => {
    try {
      const firstPage = await contentStore.fetchGeneratedList(true)
      if (generation !== contentLoadGeneration) return

      allContentList.value = []
      mergeContentBatch(firstPage)
      syncSelectedContent()
      contentCatalogReady.value = !contentStore.hasMoreContent

      if (contentStore.hasMoreContent) {
        void loadRemainingContentInBackground(generation)
      }
    } catch (e) {
      console.log('加载内容失败', e)
    }
  })().finally(() => {
    if (loadContentTask === task) {
      loadContentTask = null
    }
  })

  loadContentTask = task
  return task
}

function loadRemainingContentInBackground(generation: number) {
  if (backgroundCatalogTask) {
    return backgroundCatalogTask
  }

  const task = (async () => {
    try {
      while (generation === contentLoadGeneration && contentStore.hasMoreContent) {
        const moreItems = await contentStore.fetchMoreContent()
        if (generation !== contentLoadGeneration) return

        mergeContentBatch(moreItems)
        syncSelectedContent()
      }
    } catch (e) {
      console.log('[child] 后台补齐内容失败', e)
    }

    if (generation === contentLoadGeneration) {
      contentCatalogReady.value = !contentStore.hasMoreContent
      if (contentCatalogReady.value) {
        console.log('[child] 内容目录后台补齐完成:', allContentList.value.length, '个')
      }
    }
  })().finally(() => {
    if (backgroundCatalogTask === task) {
      backgroundCatalogTask = null
    }
  })

  backgroundCatalogTask = task
  return task
}

onLoad((options) => {
  if (options?.contentId) {
    preferredContentId.value = options.contentId
    contentStore.fetchContentDetail(options.contentId).then(() => {
      currentContent.value = contentStore.getCachedContent(options.contentId)
    }).catch(() => {
      /* silent */
    })
  }

})

onMounted(() => {
  loadContent()
})

onUnmounted(() => {
  contentLoadGeneration++
})
</script>

<style lang="scss" scoped>
// ============================================
// 🎠 梦幻游乐园 - 儿童模式
// ============================================

// 变量定义
$candy-pink: #FF6B9D;
$candy-orange: #FF9F43;
$candy-yellow: #FECA57;
$candy-green: #5CD85A;
$candy-blue: #54A0FF;
$candy-purple: #A55EEA;
$cream: #FFF9F0;
$soft-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);

// 主容器
.wonderland {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

// ============================================
// 背景层
// ============================================
.bg-layer {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    180deg,
    #FFE8F5 0%,
    #FFF0E8 25%,
    #E8F8FF 50%,
    #F0FFF4 75%,
    #FFF8E8 100%
  );
}

// 云朵
.clouds {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 400rpx;
}

.cloud {
  position: absolute;
  background: white;
  border-radius: 100rpx;
  opacity: 0.8;

  &::before, &::after {
    content: '';
    position: absolute;
    background: white;
    border-radius: 50%;
  }

  &.c1 {
    width: 200rpx;
    height: 60rpx;
    top: 120rpx;
    left: -50rpx;
    animation: float-cloud 20s ease-in-out infinite;

    &::before {
      width: 80rpx;
      height: 80rpx;
      top: -40rpx;
      left: 30rpx;
    }
    &::after {
      width: 60rpx;
      height: 60rpx;
      top: -30rpx;
      left: 90rpx;
    }
  }

  &.c2 {
    width: 160rpx;
    height: 50rpx;
    top: 80rpx;
    right: 20rpx;
    animation: float-cloud 15s ease-in-out infinite reverse;

    &::before {
      width: 70rpx;
      height: 70rpx;
      top: -35rpx;
      left: 20rpx;
    }
    &::after {
      width: 50rpx;
      height: 50rpx;
      top: -25rpx;
      left: 80rpx;
    }
  }

  &.c3 {
    width: 140rpx;
    height: 45rpx;
    top: 200rpx;
    left: 40%;
    animation: float-cloud 18s ease-in-out infinite 2s;

    &::before {
      width: 60rpx;
      height: 60rpx;
      top: -30rpx;
      left: 15rpx;
    }
    &::after {
      width: 45rpx;
      height: 45rpx;
      top: -22rpx;
      left: 70rpx;
    }
  }
}

@keyframes float-cloud {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(60rpx); }
}

// 星星
.stars {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
}

.star {
  position: absolute;
  width: 16rpx;
  height: 16rpx;
  background: $candy-yellow;
  clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
  animation: twinkle 2s ease-in-out infinite;

  @for $i from 1 through 12 {
    &.s#{$i} {
      top: random(60) + 5%;
      left: random(90) + 5%;
      animation-delay: $i * 0.2s;
      transform: scale(0.5 + random(10) / 10);
    }
  }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

// 彩虹
.rainbow {
  position: absolute;
  bottom: 30%;
  left: -100rpx;
  width: 400rpx;
  height: 200rpx;
  border-radius: 200rpx 200rpx 0 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(255, 107, 157, 0.2) 20%,
    rgba(255, 159, 67, 0.2) 35%,
    rgba(254, 202, 87, 0.2) 50%,
    rgba(92, 216, 90, 0.2) 65%,
    rgba(84, 160, 255, 0.2) 80%,
    rgba(165, 94, 234, 0.2) 95%
  );
  opacity: 0.6;
}

// ============================================
// 时间气球
// ============================================
// ============================================
// 魔法电视机
// ============================================
.magic-tv {
  position: relative;
  z-index: 10;
  margin: 0 40rpx 40rpx;
}

.tv-frame {
  position: relative;
  background: linear-gradient(145deg, #6B5B95, #5A4A84);
  border-radius: 40rpx;
  padding: 24rpx;
  box-shadow:
    0 20rpx 60rpx rgba(107, 91, 149, 0.4),
    inset 0 2rpx 0 rgba(255, 255, 255, 0.2);
}

.tv-antenna {
  position: absolute;
  top: -50rpx;
  width: 8rpx;
  height: 60rpx;
  background: linear-gradient(180deg, #888, #666);
  border-radius: 4rpx;

  &::after {
    content: '';
    position: absolute;
    top: -16rpx;
    left: 50%;
    transform: translateX(-50%);
    width: 24rpx;
    height: 24rpx;
    background: $candy-yellow;
    border-radius: 50%;
    box-shadow: 0 0 16rpx rgba($candy-yellow, 0.6);
  }

  &.left {
    left: 80rpx;
    transform: rotate(-15deg);
  }

  &.right {
    right: 80rpx;
    transform: rotate(15deg);
  }
}

.tv-screen {
  position: relative;
  width: 100%;
  height: 360rpx;
  background: #222;
  border-radius: 24rpx;
  overflow: hidden;
  border: 8rpx solid #333;
}

.screen-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.screen-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
}

.placeholder-emoji {
  font-size: 120rpx;
  animation: float-emoji 2s ease-in-out infinite;
}

@keyframes float-emoji {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-10rpx) scale(1.05); }
}

.screen-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    ellipse at center,
    transparent 50%,
    rgba(0, 0, 0, 0.3) 100%
  );
  pointer-events: none;
}

.scanlines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2rpx,
    rgba(0, 0, 0, 0.1) 2rpx,
    rgba(0, 0, 0, 0.1) 4rpx
  );
  pointer-events: none;
  opacity: 0.5;
}

.tv-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20rpx;
  padding: 0 20rpx;
}

.tv-dial {
  width: 50rpx;
  height: 50rpx;
  background: linear-gradient(145deg, #FFD700, #FFA500);
  border-radius: 50%;
  box-shadow:
    inset 0 2rpx 4rpx rgba(255, 255, 255, 0.4),
    0 4rpx 8rpx rgba(0, 0, 0, 0.2);

  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8rpx;
    height: 20rpx;
    background: #333;
    border-radius: 4rpx;
  }
}

.tv-speaker {
  display: flex;
  gap: 6rpx;
}

.speaker-line {
  width: 6rpx;
  height: 30rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3rpx;

  &:nth-child(odd) { height: 20rpx; }
}

// 播放按钮 - 在屏幕中心
.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
}

.play-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 140rpx;
  height: 140rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: pulse 1.5s ease-out infinite;
}

@keyframes pulse {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.play-icon {
  position: relative;
  width: 100rpx;
  height: 100rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.3);
  font-size: 44rpx;
  color: $candy-pink;
  padding-left: 8rpx;
}

// 屏幕上的类型角标
.screen-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 600;
  color: white;
  z-index: 10;

  &.type-picture-book { background: $candy-pink; }
  &.type-nursery-rhyme { background: $candy-green; }
  &.type-video { background: $candy-blue; }
}

// 电视机下方标题
.tv-title {
  margin-top: 24rpx;
  padding: 0 20rpx;
  text-align: center;
}

.title-text {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// ============================================
// 空状态
// ============================================
.empty-magic {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 80rpx 40rpx;
}

.empty-wand {
  font-size: 120rpx;
  margin-bottom: 24rpx;
  animation: wave-wand 2s ease-in-out infinite;
}

@keyframes wave-wand {
  0%, 100% { transform: rotate(-10deg); }
  50% { transform: rotate(10deg); }
}

.empty-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 12rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: #999;
}

// ============================================
// 素材旋转木马
// ============================================
.carousel-section {
  position: relative;
  z-index: 10;
  padding-bottom: 220rpx;
}

.carousel-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

// 类型筛选按钮
.type-filter {
  display: flex;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
  padding: 0 30rpx;
}

.filter-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12rpx 20rpx;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  min-width: 100rpx;

  &.active {
    background: linear-gradient(145deg, $candy-pink, $candy-purple);
    transform: scale(1.05);
    box-shadow: 0 6rpx 20rpx rgba($candy-pink, 0.4);

    .filter-icon {
      transform: scale(1.2);
    }

    .filter-label {
      color: white;
    }
  }
}

.filter-icon {
  font-size: 32rpx;
  margin-bottom: 4rpx;
  transition: transform 0.3s ease;
}

.filter-label {
  font-size: 20rpx;
  color: #666;
  font-weight: 600;
  transition: color 0.3s ease;
}

.header-star {
  font-size: 28rpx;
  animation: spin-star 3s linear infinite;
}

@keyframes spin-star {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #555;
  letter-spacing: 4rpx;
}

.carousel-track {
  width: 100%;
  white-space: nowrap;
}

.carousel-inner {
  display: inline-flex;
  padding: 20rpx 30rpx 40rpx;
  gap: 24rpx;
}

.carousel-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 160rpx;
  animation: pop-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) backwards;

  &.active {
    .toy-box {
      transform: scale(1.1) translateY(-10rpx);

      .box-front {
        animation: wobble 0.6s ease-in-out;
      }
    }

    .item-label {
      color: #333;
      font-weight: 700;
    }
  }
}

@keyframes pop-in {
  from {
    opacity: 0;
    transform: scale(0.5) translateY(40rpx);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes wobble {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}

.toy-box {
  position: relative;
  width: 120rpx;
  height: 120rpx;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.box-lid {
  position: absolute;
  top: 0;
  left: -5rpx;
  right: -5rpx;
  height: 24rpx;
  background: linear-gradient(180deg,
    rgba(255, 255, 255, 0.4),
    rgba(255, 255, 255, 0.1)
  );
  border-radius: 12rpx 12rpx 4rpx 4rpx;
  z-index: 2;
}

.box-front {
  position: absolute;
  top: 20rpx;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 8rpx 24rpx rgba(0, 0, 0, 0.15),
    inset 0 2rpx 0 rgba(255, 255, 255, 0.3);
}

.type-picture-book .box-front {
  background: linear-gradient(145deg, #FF8A9B, $candy-pink);
}

.type-nursery-rhyme .box-front {
  background: linear-gradient(145deg, #7ED687, $candy-green);
}

.type-video .box-front {
  background: linear-gradient(145deg, #6BB3FF, $candy-blue);
}

.toy-icon text {
  font-size: 48rpx;
  filter: drop-shadow(0 2rpx 4rpx rgba(0, 0, 0, 0.2));
}

.box-shine {
  position: absolute;
  top: 24rpx;
  left: 8rpx;
  width: 24rpx;
  height: 24rpx;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  filter: blur(4rpx);
}

.item-label {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #666;
  text-align: center;
  max-width: 140rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.select-star {
  position: absolute;
  top: -10rpx;
  right: 10rpx;
  font-size: 32rpx;
  animation: star-bounce 1s ease-in-out infinite;
}

@keyframes star-bounce {
  0%, 100% { transform: scale(1) rotate(0); }
  50% { transform: scale(1.2) rotate(10deg); }
}

.scroll-hint {
  text-align: center;
  padding-top: 8rpx;

  text {
    font-size: 22rpx;
    color: #aaa;
    animation: hint-fade 2s ease-in-out infinite;
  }
}

@keyframes hint-fade {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

// ============================================
// 返回按钮
// ============================================
.exit-zone {
  position: fixed;
  bottom: calc(30rpx + env(safe-area-inset-bottom));
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  -webkit-touch-callout: none;
  user-select: none;
}

.exit-button {
  position: relative;
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;

  &:active {
    transform: scale(1.06);
    box-shadow: 0 12rpx 40rpx rgba($candy-pink, 0.4);

    .exit-glow {
      opacity: 1;
    }
  }
}

.exit-glow {
  position: absolute;
  top: -10rpx;
  left: -10rpx;
  right: -10rpx;
  bottom: -10rpx;
  border-radius: 50%;
  background: linear-gradient(45deg, $candy-pink, $candy-yellow, $candy-green);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
  filter: blur(10rpx);
}

.exit-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rpx;
}

.exit-icon {
  font-size: 40rpx;
  line-height: 1;
}

.exit-text {
  font-size: 22rpx;
  color: #666;
  font-weight: 600;
}

// ============================================
// 休息提醒 - 月亮睡眠
// ============================================
</style>
