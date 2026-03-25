<template>
  <view
    class="content-card"
    :class="[`card-${type}`, { 'card-large': large }]"
    @tap="$emit('tap')"
    @longpress="$emit('longpress')"
  >
    <!-- 封面图 -->
    <view class="card-cover">
      <image
        v-if="coverUrl"
        class="cover-image"
        :src="coverUrl"
        mode="aspectFill"
      />
      <view v-else class="cover-placeholder">
        <text class="placeholder-emoji">{{ placeholderEmoji }}</text>
      </view>

      <!-- 类型标签 -->
      <view class="type-tag" :class="`tag-${type}`">
        <text class="tag-icon">{{ typeIcon }}</text>
        <text class="tag-text">{{ typeLabel }}</text>
      </view>

      <!-- 时长标签 -->
      <view v-if="duration" class="duration-tag">
        <text>{{ formatDuration(duration) }}</text>
      </view>

      <!-- 播放按钮浮层 -->
      <view v-if="showPlay" class="play-overlay" @tap.stop="$emit('play')">
        <view class="play-btn-inner">
          <text class="play-icon">▶</text>
        </view>
      </view>
    </view>

    <!-- 卡片信息 -->
    <view class="card-info">
      <text class="card-title">{{ title }}</text>
      <view class="card-meta">
        <text v-if="childName" class="meta-child">
          <text class="meta-icon">👶</text>
          {{ childName }}的专属
        </text>
        <text v-if="createdAt" class="meta-time">{{ formatTime(createdAt) }}</text>
      </view>
    </view>

    <!-- 进度条 -->
    <view v-if="progress > 0 && progress < 1" class="progress-bar">
      <view class="progress-fill" :style="{ width: progress * 100 + '%' }"></view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  type: 'picture_book' | 'nursery_rhyme' | 'video'
  coverUrl?: string
  duration?: number
  childName?: string
  createdAt?: string
  progress?: number
  large?: boolean
  showPlay?: boolean
}>()

defineEmits(['tap', 'play', 'longpress'])

const typeLabel = computed(() => {
  const labels = {
    picture_book: '绘本',
    nursery_rhyme: '儿歌',
    video: '视频'
  }
  return labels[props.type] || '内容'
})

const typeIcon = computed(() => {
  const icons = {
    picture_book: '📚',
    nursery_rhyme: '🎵',
    video: '🎬'
  }
  return icons[props.type] || '📖'
})

const placeholderEmoji = computed(() => {
  const emojis = {
    picture_book: '📚',
    nursery_rhyme: '🎵',
    video: '🎬'
  }
  return emojis[props.type] || '📖'
})

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.content-card {
  position: relative;
  background: $bg-card;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: $shadow-soft;
  transition: transform $duration-base $ease-bounce;
  width: 100%;
  box-sizing: border-box;

  &:active {
    transform: scale(0.98);
  }
}

// === 不同类型卡片的主题色 ===
.card-picture_book {
  .type-tag { background: rgba($book-primary, 0.95); }
  .play-btn-inner { background: $book-gradient; box-shadow: 0 4rpx 12rpx rgba($book-primary, 0.4); }
  .progress-fill { background: $book-primary; }
  .cover-placeholder { background: $book-bg; }
}

.card-nursery_rhyme {
  .type-tag { background: rgba($song-primary, 0.95); }
  .play-btn-inner { background: $song-gradient; box-shadow: 0 4rpx 12rpx rgba($song-primary, 0.4); }
  .progress-fill { background: $song-primary; }
  .cover-placeholder { background: $song-bg; }
}

.card-video {
  .type-tag { background: rgba($video-primary, 0.95); }
  .play-btn-inner { background: $video-gradient; box-shadow: 0 4rpx 12rpx rgba($video-primary, 0.4); }
  .progress-fill { background: $video-primary; }
  .cover-placeholder { background: $video-bg; }
}

// === 封面区域 ===
.card-cover {
  position: relative;
  width: 100%;
  padding-top: 65%; // 宽高比
  overflow: hidden;
}

.cover-image {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  .placeholder-emoji {
    font-size: 80rpx;
    opacity: 0.6;
  }
}

// === 类型标签 ===
.type-tag {
  position: absolute;
  top: $spacing-sm;
  left: $spacing-sm;
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 6rpx 14rpx;
  border-radius: $radius-full;
}

.tag-icon {
  font-size: 20rpx;
}

.tag-text {
  font-size: $font-xs;
  font-weight: $font-medium;
  color: $text-white;
}

// === 时长标签 ===
.duration-tag {
  position: absolute;
  bottom: $spacing-sm;
  right: $spacing-sm;
  padding: 4rpx 12rpx;
  border-radius: $radius-sm;
  background: rgba(0, 0, 0, 0.6);
  font-size: $font-xs;
  color: $text-white;
}

// === 播放按钮浮层 ===
.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.15);
  opacity: 1;
  transition: opacity $duration-fast;
}

.play-btn-inner {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform $duration-fast $ease-bounce;

  &:active {
    transform: scale(0.9);
  }
}

.play-icon {
  color: $text-white;
  font-size: 28rpx;
  margin-left: 4rpx;
}

// === 卡片信息 ===
.card-info {
  padding: $spacing-sm;
}

.card-title {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  margin-top: $spacing-xs;
  font-size: $font-xs;
  color: $text-secondary;
  flex-wrap: wrap;
}

.meta-child {
  display: inline-flex;
  align-items: center;
  gap: 4rpx;
  padding: 4rpx 10rpx;
  background: rgba($primary, 0.08);
  border-radius: $radius-xs;
  color: $primary;
}

.meta-icon {
  font-size: 18rpx;
}

.meta-time {
  color: $text-light;
}

// === 进度条 ===
.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 6rpx;
  background: rgba(0, 0, 0, 0.1);
}

.progress-fill {
  height: 100%;
  border-radius: 0 3rpx 3rpx 0;
  transition: width $duration-base ease-out;
}

// === 大卡片样式 ===
.card-large {
  .card-cover {
    padding-top: 56%; // 16:9
  }

  .cover-placeholder .placeholder-emoji {
    font-size: 120rpx;
  }

  .card-title {
    font-size: $font-md;
  }

  .play-btn-inner {
    width: 100rpx;
    height: 100rpx;

    .play-icon {
      font-size: 36rpx;
    }
  }
}
</style>
