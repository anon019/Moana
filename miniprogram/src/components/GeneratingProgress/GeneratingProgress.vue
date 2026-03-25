<template>
  <view class="generating-overlay">
    <view class="generating-modal">
      <!-- 装饰背景 -->
      <view class="modal-decor">
        <view class="decor-circle c1"></view>
        <view class="decor-circle c2"></view>
        <view class="decor-circle c3"></view>
      </view>

      <!-- 动画图标 -->
      <view class="generating-icon">
        <view class="icon-ring ring-1"></view>
        <view class="icon-ring ring-2"></view>
        <view class="icon-center">
          <text>{{ currentEmoji }}</text>
        </view>
      </view>

      <!-- 状态文字 -->
      <text class="generating-title">{{ statusText }}</text>
      <text class="generating-desc">{{ statusDesc }}</text>

      <!-- 进度条 -->
      <view class="progress-wrapper">
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: progress + '%' }">
            <view class="progress-glow"></view>
          </view>
        </view>
        <text class="progress-text">{{ Math.round(progress) }}%</text>
      </view>

      <!-- 阶段指示器 -->
      <view class="stages">
        <view
          v-for="(stage, index) in stages"
          :key="stage.id"
          class="stage-item"
          :class="{ active: currentStage >= index, done: currentStage > index }"
        >
          <view class="stage-dot">
            <text v-if="currentStage > index">✓</text>
          </view>
          <text class="stage-name">{{ stage.name }}</text>
        </view>
      </view>

      <!-- 提示文字 -->
      <text class="generating-tip">{{ currentTip }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// Suno 任务阶段类型（后端回调: text, first, complete）
type SunoTaskStage = 'waiting' | 'text' | 'first' | 'complete' | 'error'

const props = withDefaults(defineProps<{
  progress: number
  type?: 'book' | 'song' | 'video'  // 内容类型
  stage?: SunoTaskStage | string   // 后端返回的真实阶段
  message?: string                  // 后端返回的真实消息
}>(), {
  type: 'book',
  stage: '',
  message: ''
})

// 绘本生成阶段
const bookStages = [
  { id: 'story', name: '编写故事' },
  { id: 'image', name: '生成插画' },
  { id: 'audio', name: '合成语音' }
]

// 儿歌生成阶段（严格对应 Suno 回调阶段）
// text: 文本生成完成 → first: 第一首音乐完成 → complete: 所有音乐完成
const songStages = [
  { id: 'text', name: '文本生成' },      // waiting 进行中 → text 完成
  { id: 'first', name: '首曲生成' },     // text 后进行中 → first 完成
  { id: 'complete', name: '全部完成' }   // first 后进行中 → complete 完成
]

// 视频生成阶段
const videoStages = [
  { id: 'prepare', name: '准备素材' },
  { id: 'render', name: '渲染动画' },
  { id: 'compose', name: '合成视频' }
]

// 根据类型选择阶段
const stages = computed(() => {
  if (props.type === 'song') return songStages
  if (props.type === 'video') return videoStages
  return bookStages
})

const bookTips = [
  '正在为宝贝编织一个温馨的故事...',
  'AI 正在创作独一无二的插画...',
  '每一页都充满爱与想象力...',
  '即将完成，敬请期待...',
  '好故事值得等待～'
]

const songTips = [
  '正在为宝贝创作专属歌词...',
  'AI 正在谱写欢乐的旋律...',
  '每一个音符都充满爱意...',
  '即将完成，准备开唱～',
  '好音乐值得等待～'
]

const videoTips = [
  '正在为绘本注入生命力...',
  'AI 正在创作精彩动画...',
  '每一帧都充满童趣...',
  '即将完成，敬请期待...',
  '好视频值得等待～'
]

const tips = computed(() => {
  if (props.type === 'song') return songTips
  if (props.type === 'video') return videoTips
  return bookTips
})

const emojis = computed(() => {
  if (props.type === 'song') return ['✨', '🎵', '🎤', '🎶', '🌟']
  if (props.type === 'video') return ['✨', '🎬', '🎥', '🎞️', '🌟']
  return ['✨', '📚', '🎨', '🎵', '🌟']
})

const currentTipIndex = ref(0)
const currentEmojiIndex = ref(0)
let tipInterval: number
let emojiInterval: number

// 儿歌阶段映射 (Suno 回调: text → first → complete)
const songStageMapping: Record<string, number> = {
  waiting: 0,   // 初始状态，"文本生成"进行中
  text: 1,      // text 回调 = 文本完成，"首曲生成"进行中
  first: 2,     // first 回调 = 首曲完成，"全部完成"进行中
  complete: 3,  // complete 回调 = 全部完成，所有阶段 done
  error: -1     // 错误状态
}

// 绘本阶段映射 (后端返回: init → story → image_N → audio_N → saving → completed)
// 映射到 UI 阶段索引: 0=故事, 1=插画, 2=语音, 3=完成
const bookStageMapping: Record<string, number> = {
  init: 0,         // 初始化
  story: 0,        // 故事生成中
  story_done: 1,   // 故事完成，开始图片
  saving: 2,       // 保存中
  completed: 3,    // 全部完成
  error: -1
}

// 动态匹配 image_N 和 audio_N 阶段
function getBookStageIndex(stage: string): number {
  if (!stage) return 0
  if (stage in bookStageMapping) return bookStageMapping[stage]
  if (stage.startsWith('image_')) return 1  // 所有图片阶段映射到"插画"
  if (stage.startsWith('audio_')) return 2  // 所有音频阶段映射到"语音"
  return 0
}

const currentStage = computed(() => {
  if (props.stage) {
    // 根据类型选择映射
    if (props.type === 'song') {
      return songStageMapping[props.stage] ?? 0
    }
    if (props.type === 'book') {
      return getBookStageIndex(props.stage)
    }
  }
  // 无阶段信息时根据进度估算
  if (props.progress < 20) return 0   // 0-20%: 故事
  if (props.progress < 70) return 1   // 20-70%: 插画
  if (props.progress < 95) return 2   // 70-95%: 语音
  return 3                            // 95-100%: 完成
})

// 阶段标题映射（严格对应 Suno 回调阶段）
const songStageTexts: Record<string, string> = {
  waiting: '文本生成中',      // 初始状态，正在生成歌词文本
  text: '音乐生成中',         // text 回调后，文本完成，正在生成音乐
  first: '继续生成中',        // first 回调后，首曲完成，生成第二首
  complete: '生成完成',       // complete 回调，全部完成
  error: '生成失败'
}

// 绘本阶段标题映射（基础阶段）
const bookStageTexts: Record<string, string> = {
  init: '准备中',
  story: '故事创作中',
  story_done: '故事完成',
  saving: '保存中',
  completed: '生成完成',
  error: '生成失败'
}

// 动态获取绘本阶段标题（支持 image_N 和 audio_N）
function getBookStageText(stage: string): string {
  if (!stage) return '生成中'
  if (stage in bookStageTexts) return bookStageTexts[stage]
  // 匹配 image_1, image_2 等
  const imageMatch = stage.match(/^image_(\d+)$/)
  if (imageMatch) return `第${imageMatch[1]}张插画`
  // 匹配 audio_1, audio_2 等
  const audioMatch = stage.match(/^audio_(\d+)$/)
  if (audioMatch) return `第${audioMatch[1]}段语音`
  return '生成中'
}

const statusText = computed(() => {
  // 优先使用后端返回的 message（人类可读文本）
  if (props.message) {
    return props.message
  }

  // 如果有后端返回的阶段代码，使用映射
  if (props.stage) {
    if (props.type === 'song') {
      return songStageTexts[props.stage] || '生成中'
    }
    if (props.type === 'book') {
      return getBookStageText(props.stage)
    }
  }

  // 无阶段时根据进度估算
  if (props.type === 'song') {
    if (props.progress < 30) return '歌词创作中'
    if (props.progress < 70) return '音乐生成中'
    if (props.progress < 95) return '封面绘制中'
    return '即将完成'
  }
  if (props.type === 'video') {
    if (props.progress < 30) return '准备素材中'
    if (props.progress < 70) return '渲染动画中'
    if (props.progress < 95) return '合成视频中'
    return '即将完成'
  }
  // 绘本
  if (props.progress < 20) return '故事创作中'
  if (props.progress < 70) return '插画生成中'
  if (props.progress < 95) return '语音合成中'
  return '即将完成'
})

const statusDesc = computed(() => {
  // statusDesc 显示鼓励性文字，不使用 message（message 已在 statusText 显示）
  if (props.type === 'song') {
    if (props.progress < 30) return 'AI 正在为宝贝编写专属歌词'
    if (props.progress < 70) return '正在谱写欢乐的旋律'
    if (props.progress < 95) return '为儿歌绘制精美封面'
    return '最后的润色中'
  }
  if (props.type === 'video') {
    if (props.progress < 30) return '正在处理绘本素材'
    if (props.progress < 70) return 'AI 正在生成精彩动画'
    if (props.progress < 95) return '正在合成最终视频'
    return '最后的润色中'
  }
  // 绘本 - 根据进度范围匹配后端分配
  if (props.progress < 20) return 'AI 正在为宝贝编写专属故事'
  if (props.progress < 70) return '正在绘制精美的插画'
  if (props.progress < 95) return '为每一页配上温柔的声音'
  return '最后的润色中'
})

const currentTip = computed(() => tips.value[currentTipIndex.value])
const currentEmoji = computed(() => emojis.value[currentEmojiIndex.value])

onMounted(() => {
  tipInterval = setInterval(() => {
    currentTipIndex.value = (currentTipIndex.value + 1) % tips.value.length
  }, 3000)

  emojiInterval = setInterval(() => {
    currentEmojiIndex.value = (currentEmojiIndex.value + 1) % emojis.value.length
  }, 800)
})

onUnmounted(() => {
  clearInterval(tipInterval)
  clearInterval(emojiInterval)
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.generating-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: $z-modal;
  padding: $spacing-lg;
}

.generating-modal {
  position: relative;
  width: 100%;
  max-width: 600rpx;
  background: $bg-card;
  border-radius: $radius-xl;
  padding: $spacing-xl $spacing-lg;
  text-align: center;
  overflow: hidden;
}

.modal-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.decor-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.5;

  &.c1 {
    width: 200rpx;
    height: 200rpx;
    background: $accent-soft;
    top: -80rpx;
    right: -60rpx;
  }

  &.c2 {
    width: 150rpx;
    height: 150rpx;
    background: rgba($secondary, 0.2);
    bottom: -50rpx;
    left: -30rpx;
  }

  &.c3 {
    width: 100rpx;
    height: 100rpx;
    background: rgba($primary, 0.15);
    top: 50%;
    left: 80%;
  }
}

.generating-icon {
  position: relative;
  width: 160rpx;
  height: 160rpx;
  margin: 0 auto $spacing-lg;
}

.icon-ring {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  border: 4rpx solid transparent;

  &.ring-1 {
    border-top-color: $primary;
    animation: spin 1.5s linear infinite;
  }

  &.ring-2 {
    top: 16rpx;
    left: 16rpx;
    right: 16rpx;
    bottom: 16rpx;
    border-right-color: $secondary;
    animation: spin 2s linear infinite reverse;
  }
}

.icon-center {
  position: absolute;
  top: 32rpx;
  left: 32rpx;
  right: 32rpx;
  bottom: 32rpx;
  background: $gradient-warm;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  text {
    font-size: 56rpx;
    animation: pulse 1s ease-in-out infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.generating-title {
  display: block;
  font-size: $font-xl;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.generating-desc {
  display: block;
  font-size: $font-base;
  color: $text-secondary;
  margin-bottom: $spacing-lg;
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-lg;
}

.progress-bar {
  flex: 1;
  height: 16rpx;
  background: rgba($primary, 0.15);
  border-radius: $radius-full;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: $gradient-primary;
  border-radius: $radius-full;
  position: relative;
  transition: width 0.5s ease-out;
}

.progress-glow {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 40rpx;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6));
  animation: glow 1.5s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.progress-text {
  font-size: $font-md;
  font-weight: $font-bold;
  color: $primary;
  min-width: 80rpx;
  text-align: right;
}

.stages {
  display: flex;
  justify-content: center;
  gap: $spacing-lg;
  margin-bottom: $spacing-lg;
}

.stage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  opacity: 0.4;
  transition: opacity $duration-base;

  &.active {
    opacity: 1;
  }

  &.done .stage-dot {
    background: $success;
    border-color: $success;
  }
}

.stage-dot {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  border: 4rpx solid $text-light;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $duration-base;

  .active & {
    border-color: $primary;
    background: $primary;
  }

  text {
    font-size: 20rpx;
    color: $text-white;
  }
}

.stage-name {
  font-size: $font-xs;
  color: $text-secondary;
}

.generating-tip {
  display: block;
  font-size: $font-sm;
  color: $text-light;
  font-style: italic;
}
</style>
