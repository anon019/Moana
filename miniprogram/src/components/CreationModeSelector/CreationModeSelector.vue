<template>
  <view class="mode-selector">
    <!-- 梦幻背景装饰 -->
    <view class="floating-decor">
      <view class="bubble bubble-1"></view>
      <view class="bubble bubble-2"></view>
      <view class="bubble bubble-3"></view>
      <view class="star star-1">✦</view>
      <view class="star star-2">✧</view>
      <view class="star star-3">✦</view>
    </view>

    <!-- 标题区 -->
    <view class="header-area">
      <view class="mascot">
        <text class="mascot-emoji">{{ contentTypeEmoji }}</text>
        <view class="mascot-glow"></view>
      </view>
      <text class="title">{{ title }}</text>
      <text class="subtitle">选择你喜欢的创作方式</text>
    </view>

    <!-- 模式选择卡片 -->
    <view class="mode-cards">
      <!-- 主题预设模式 -->
      <view
        class="mode-card preset-card"
        :class="{ selected: selectedMode === 'preset' }"
        @tap="selectMode('preset')"
      >
        <view class="card-glow"></view>
        <view class="card-content">
          <view class="card-icon-area">
            <view class="icon-bg preset-icon-bg">
              <text class="card-icon">📋</text>
            </view>
            <view class="icon-sparkle">✨</view>
          </view>
          <view class="card-text">
            <text class="card-title">主题精选</text>
            <text class="card-desc">从精心准备的主题中选择</text>
          </view>
          <view class="card-tags">
            <view class="tag">快速开始</view>
            <view class="tag">推荐</view>
          </view>
        </view>
        <view v-if="selectedMode === 'preset'" class="check-mark">
          <text>✓</text>
        </view>
      </view>

      <!-- 智能创作模式 -->
      <view
        class="mode-card smart-card"
        :class="{ selected: selectedMode === 'smart' }"
        @tap="selectMode('smart')"
      >
        <view class="card-glow"></view>
        <view class="card-content">
          <view class="card-icon-area">
            <view class="icon-bg smart-icon-bg">
              <text class="card-icon">🪄</text>
            </view>
            <view class="icon-sparkle magic">✨</view>
          </view>
          <view class="card-text">
            <text class="card-title">智能创作</text>
            <text class="card-desc">描述你的想法，AI 帮你实现</text>
          </view>
          <view class="card-tags">
            <view class="tag magic-tag">自由创意</view>
            <view class="tag magic-tag">个性化</view>
          </view>
        </view>
        <view v-if="selectedMode === 'smart'" class="check-mark magic-check">
          <text>✓</text>
        </view>
      </view>
    </view>

    <!-- 智能创作输入区 (当选择智能模式时展开) -->
    <view v-if="selectedMode === 'smart'" class="smart-input-area animate-slideIn">
      <view class="input-container">
        <view class="input-header">
          <text class="input-icon">💭</text>
          <text class="input-label">告诉 AI 你的想法</text>
        </view>
        <textarea
          v-model="smartPrompt"
          class="prompt-textarea"
          placeholder="例如：宝宝不爱刷牙，做一个有趣的刷牙故事..."
          :maxlength="300"
          auto-height
        />
        <view class="input-footer">
          <text class="char-count">{{ smartPrompt.length }}/300</text>
        </view>
      </view>

      <!-- 快捷灵感标签 -->
      <view class="inspiration-area">
        <text class="inspiration-title">💡 快捷灵感</text>
        <view class="inspiration-tags">
          <view
            v-for="(tag, index) in inspirationTags"
            :key="index"
            class="inspiration-tag"
            @tap="fillInspiration(tag)"
          >
            <text class="tag-emoji">{{ tag.emoji }}</text>
            <text class="tag-text">{{ tag.label }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作区 -->
    <view class="action-area">
      <view
        class="start-btn"
        :class="{ disabled: !canStart, [contentTypeClass]: true }"
        @tap="handleStart"
      >
        <view class="btn-shine"></view>
        <view class="btn-content">
          <text class="btn-icon">{{ selectedMode === 'smart' ? '✨' : '🚀' }}</text>
          <text class="btn-text">{{ startButtonText }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

type ContentType = 'picture_book' | 'nursery_rhyme' | 'video'
type CreationMode = 'preset' | 'smart'

const props = defineProps<{
  contentType: ContentType
}>()

const emit = defineEmits<{
  (e: 'select', mode: CreationMode, prompt?: string): void
}>()

const selectedMode = ref<CreationMode | ''>('')
const smartPrompt = ref('')

// 根据内容类型显示不同的标题和图标
const contentTypeConfig = computed(() => {
  const configs: Record<ContentType, { title: string; emoji: string; class: string }> = {
    picture_book: { title: '创作绘本', emoji: '📚', class: 'book' },
    nursery_rhyme: { title: '创作儿歌', emoji: '🎵', class: 'song' },
    video: { title: '创作视频', emoji: '🎬', class: 'video' }
  }
  return configs[props.contentType]
})

const title = computed(() => contentTypeConfig.value.title)
const contentTypeEmoji = computed(() => contentTypeConfig.value.emoji)
const contentTypeClass = computed(() => contentTypeConfig.value.class)

// 根据内容类型区分的灵感标签
const inspirationTagsConfig: Record<ContentType, Array<{ emoji: string; label: string; text: string }>> = {
  // 绘本：故事类型导向（20条）
  picture_book: [
    { emoji: '🏰', label: '童话冒险', text: '创作一个充满魔法的童话冒险故事' },
    { emoji: '🔍', label: '悬疑探险', text: '创作一个小侦探破解谜题的探险故事' },
    { emoji: '🌈', label: '奇幻世界', text: '创作一个发生在奇幻王国的神奇故事' },
    { emoji: '💕', label: '温馨日常', text: '创作一个温暖治愈的家庭日常故事' },
    { emoji: '🦸', label: '英雄成长', text: '创作一个小英雄克服困难、勇敢成长的故事' },
    { emoji: '🌲', label: '森林奇遇', text: '创作一个在神秘森林中发生的奇遇故事' },
    { emoji: '🚀', label: '太空探索', text: '创作一个探索宇宙星球的科幻冒险故事' },
    { emoji: '🐾', label: '动物伙伴', text: '创作一个可爱动物们之间的友谊故事' },
    { emoji: '🎪', label: '欢乐派对', text: '创作一个充满惊喜和欢笑的派对故事' },
    { emoji: '🌊', label: '海底世界', text: '创作一个探索神秘海底王国的冒险故事' },
    { emoji: '🦄', label: '梦境奇缘', text: '创作一个发生在梦境中的奇妙故事' },
    { emoji: '🎭', label: '寓言故事', text: '创作一个蕴含人生道理的寓言故事' },
    { emoji: '🏝️', label: '荒岛求生', text: '创作一个在神秘小岛上的冒险故事' },
    { emoji: '🎨', label: '创意想象', text: '创作一个天马行空的想象故事' },
    { emoji: '🦁', label: '动物王国', text: '创作一个动物王国里的精彩故事' },
    { emoji: '🧙', label: '魔法学院', text: '创作一个在魔法学校学习的故事' },
    { emoji: '🌸', label: '四季变换', text: '创作一个关于春夏秋冬四季的故事' },
    { emoji: '🎠', label: '游乐园', text: '创作一个在神奇游乐园的冒险故事' },
    { emoji: '🌟', label: '追逐梦想', text: '创作一个追逐梦想、永不放弃的故事' },
    { emoji: '🤝', label: '友谊万岁', text: '创作一个关于真挚友谊的感人故事' }
  ],
  // 儿歌：功能性 + 场景结合（20条）
  nursery_rhyme: [
    { emoji: '🔢', label: '数字启蒙', text: '编一首教宝宝认识数字的儿歌' },
    { emoji: '🔤', label: '字母学习', text: '编一首朗朗上口的字母学习歌' },
    { emoji: '🎵', label: '律动舞蹈', text: '编一首可以跟着跳舞的律动儿歌' },
    { emoji: '😴', label: '摇篮曲', text: '编一首温柔舒缓的哄睡摇篮曲' },
    { emoji: '🌅', label: '早安歌', text: '编一首元气满满的起床早安歌' },
    { emoji: '🍽️', label: '吃饭歌', text: '编一首让宝宝爱上吃饭的儿歌' },
    { emoji: '🚗', label: '出行歌', text: '编一首出门坐车时唱的欢乐儿歌' },
    { emoji: '🛁', label: '洗澡歌', text: '编一首让洗澡变有趣的儿歌' },
    { emoji: '🌙', label: '晚安歌', text: '编一首甜蜜温馨的睡前晚安歌' },
    { emoji: '🎂', label: '生日歌', text: '编一首专属宝宝的生日祝福歌' },
    { emoji: '🦷', label: '刷牙歌', text: '编一首让宝宝爱上刷牙的儿歌' },
    { emoji: '🌈', label: '颜色歌', text: '编一首教宝宝认识颜色的儿歌' },
    { emoji: '🐻', label: '动物歌', text: '编一首认识各种小动物的儿歌' },
    { emoji: '🍎', label: '水果歌', text: '编一首认识各种水果的儿歌' },
    { emoji: '👋', label: '礼貌歌', text: '编一首教宝宝讲礼貌的儿歌' },
    { emoji: '🏃', label: '运动歌', text: '编一首鼓励宝宝爱运动的儿歌' },
    { emoji: '🧹', label: '收拾歌', text: '编一首教宝宝收拾玩具的儿歌' },
    { emoji: '👨‍👩‍👧', label: '家人歌', text: '编一首认识家庭成员的儿歌' },
    { emoji: '🌞', label: '天气歌', text: '编一首认识天气变化的儿歌' },
    { emoji: '🎄', label: '节日歌', text: '编一首庆祝节日的欢乐儿歌' }
  ],
  // 视频：特殊时刻/纪念（20条）
  video: [
    { emoji: '🎂', label: '生日祝福', text: '制作一个生日快乐祝福视频' },
    { emoji: '🎄', label: '节日庆典', text: '制作一个节日主题的庆祝视频' },
    { emoji: '📸', label: '成长纪念', text: '制作一个记录宝宝成长瞬间的视频' },
    { emoji: '🏆', label: '荣誉时刻', text: '制作一个表彰宝宝获得荣誉的视频' },
    { emoji: '👨‍👩‍👧', label: '全家福', text: '制作一个温馨的家庭合影视频' },
    { emoji: '🎓', label: '毕业典礼', text: '制作一个幼儿园/学校毕业纪念视频' },
    { emoji: '✈️', label: '旅行回忆', text: '制作一个记录美好旅途的回忆视频' },
    { emoji: '💝', label: '感恩祝福', text: '制作一个送给亲人的感恩祝福视频' },
    { emoji: '🌟', label: '才艺展示', text: '制作一个展示宝宝才艺的精彩视频' },
    { emoji: '🎁', label: '惊喜礼物', text: '制作一个给家人朋友的惊喜视频' },
    { emoji: '🏠', label: '新家乔迁', text: '制作一个庆祝搬新家的纪念视频' },
    { emoji: '👶', label: '满月百天', text: '制作一个宝宝满月或百天的纪念视频' },
    { emoji: '🎀', label: '周岁庆典', text: '制作一个宝宝周岁生日的纪念视频' },
    { emoji: '🏫', label: '开学典礼', text: '制作一个开学第一天的纪念视频' },
    { emoji: '🎹', label: '演出纪念', text: '制作一个记录表演演出的精彩视频' },
    { emoji: '⚽', label: '运动会', text: '制作一个运动会精彩瞬间的视频' },
    { emoji: '🌺', label: '母亲节', text: '制作一个送给妈妈的母亲节视频' },
    { emoji: '👔', label: '父亲节', text: '制作一个送给爸爸的父亲节视频' },
    { emoji: '👴', label: '敬老节', text: '制作一个送给爷爷奶奶的祝福视频' },
    { emoji: '📅', label: '年度回顾', text: '制作一个回顾一年精彩时刻的视频' }
  ]
}

// 根据当前内容类型获取对应的灵感标签
const inspirationTags = computed(() => inspirationTagsConfig[props.contentType])

const canStart = computed(() => {
  if (!selectedMode.value) return false
  if (selectedMode.value === 'smart' && !smartPrompt.value.trim()) return false
  return true
})

const startButtonText = computed(() => {
  if (!selectedMode.value) return '请选择创作方式'
  if (selectedMode.value === 'smart' && !smartPrompt.value.trim()) return '请输入创意描述'
  return selectedMode.value === 'smart' ? '开始智能创作' : '选择主题'
})

function selectMode(mode: CreationMode) {
  selectedMode.value = mode
}

function fillInspiration(tag: { text: string }) {
  smartPrompt.value = tag.text
}

function handleStart() {
  if (!canStart.value) return
  emit('select', selectedMode.value as CreationMode, smartPrompt.value || undefined)
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.mode-selector {
  min-height: 100%;
  padding: 0 32rpx;
  padding-bottom: 200rpx;
  position: relative;
  overflow: hidden;
}

// 浮动装饰
.floating-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 400rpx;
  pointer-events: none;
  z-index: 0;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;

  &.bubble-1 {
    width: 120rpx;
    height: 120rpx;
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.4), rgba(139, 92, 246, 0.2));
    top: 80rpx;
    right: 40rpx;
    animation: float 4s ease-in-out infinite;
  }

  &.bubble-2 {
    width: 80rpx;
    height: 80rpx;
    background: linear-gradient(135deg, rgba(244, 114, 182, 0.4), rgba(236, 72, 153, 0.2));
    top: 160rpx;
    left: 60rpx;
    animation: float 3.5s ease-in-out infinite 0.5s;
  }

  &.bubble-3 {
    width: 60rpx;
    height: 60rpx;
    background: linear-gradient(135deg, rgba(96, 165, 250, 0.4), rgba(59, 130, 246, 0.2));
    top: 240rpx;
    right: 120rpx;
    animation: float 5s ease-in-out infinite 1s;
  }
}

.star {
  position: absolute;
  font-size: 24rpx;
  color: rgba(251, 191, 36, 0.7);
  animation: twinkle 2s ease-in-out infinite;

  &.star-1 { top: 100rpx; left: 30%; animation-delay: 0s; }
  &.star-2 { top: 180rpx; right: 25%; animation-delay: 0.7s; font-size: 20rpx; }
  &.star-3 { top: 280rpx; left: 50%; animation-delay: 1.4s; font-size: 16rpx; }
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20rpx) scale(1.05); }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

// 标题区
.header-area {
  position: relative;
  z-index: 1;
  text-align: center;
  padding-top: 60rpx;
  margin-bottom: 48rpx;
}

.mascot {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 24rpx;
}

.mascot-emoji {
  font-size: 64rpx;
  position: relative;
  z-index: 1;
  animation: bounce 2s ease-in-out infinite;
}

.mascot-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 140rpx;
  height: 140rpx;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8rpx); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 12rpx;
  letter-spacing: 2rpx;
}

.subtitle {
  display: block;
  font-size: 28rpx;
  color: $text-tertiary;
}

// 模式卡片
.mode-cards {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 32rpx;
}

.mode-card {
  position: relative;
  background: $bg-card;
  border-radius: 32rpx;
  padding: 32rpx;
  border: 3rpx solid $border-light;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;

  &:active {
    transform: scale(0.98);
  }

  &.selected {
    border-color: transparent;
    box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.1);

    .card-glow {
      opacity: 1;
    }
  }
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.preset-card {
  .card-glow {
    background: linear-gradient(135deg, rgba(96, 165, 250, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
  }

  &.selected {
    border-color: rgba(59, 130, 246, 0.4);
  }
}

.smart-card {
  .card-glow {
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.15) 0%, rgba(139, 92, 246, 0.05) 100%);
  }

  &.selected {
    border-color: rgba(139, 92, 246, 0.4);
  }
}

.card-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.card-icon-area {
  position: relative;
  width: fit-content;
}

.icon-bg {
  width: 80rpx;
  height: 80rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  &.preset-icon-bg {
    background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
  }

  &.smart-icon-bg {
    background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%);
  }
}

.card-icon {
  font-size: 40rpx;
}

.icon-sparkle {
  position: absolute;
  top: -8rpx;
  right: -12rpx;
  font-size: 20rpx;
  animation: sparkle 1.5s ease-in-out infinite;

  &.magic {
    animation: magicSparkle 1.5s ease-in-out infinite;
  }
}

@keyframes sparkle {
  0%, 100% { opacity: 0.3; transform: scale(0.8) rotate(0deg); }
  50% { opacity: 1; transform: scale(1.2) rotate(20deg); }
}

@keyframes magicSparkle {
  0%, 100% { opacity: 0.3; transform: scale(0.8) rotate(0deg); }
  33% { opacity: 1; transform: scale(1.2) rotate(20deg); }
  66% { opacity: 0.6; transform: scale(1) rotate(-10deg); }
}

.card-text {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.card-title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.card-desc {
  font-size: 26rpx;
  color: $text-secondary;
  line-height: 1.5;
}

.card-tags {
  display: flex;
  gap: 12rpx;
  margin-top: 8rpx;
}

.tag {
  padding: 8rpx 16rpx;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #3B82F6;

  &.magic-tag {
    background: rgba(139, 92, 246, 0.1);
    color: #8B5CF6;
  }
}

.check-mark {
  position: absolute;
  top: 24rpx;
  right: 24rpx;
  width: 48rpx;
  height: 48rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

  text {
    color: white;
    font-size: 28rpx;
    font-weight: bold;
  }

  &.magic-check {
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  }
}

@keyframes popIn {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

// 智能输入区
.smart-input-area {
  position: relative;
  z-index: 1;
  margin-bottom: 32rpx;
}

.animate-slideIn {
  animation: slideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes slideIn {
  0% { opacity: 0; transform: translateY(-20rpx); }
  100% { opacity: 1; transform: translateY(0); }
}

.input-container {
  background: $bg-card;
  border-radius: 24rpx;
  padding: 24rpx;
  border: 2rpx solid rgba(139, 92, 246, 0.2);
  margin-bottom: 24rpx;
}

.input-header {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.input-icon {
  font-size: 28rpx;
}

.input-label {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.prompt-textarea {
  width: 100%;
  min-height: 120rpx;
  padding: 20rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: $text-primary;
  line-height: 1.6;
  box-sizing: border-box;
}

.input-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 12rpx;
}

.char-count {
  font-size: 22rpx;
  color: $text-placeholder;
}

.inspiration-area {
  background: rgba(139, 92, 246, 0.05);
  border-radius: 20rpx;
  padding: 20rpx;
}

.inspiration-title {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: $text-secondary;
  margin-bottom: 16rpx;
}

.inspiration-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.inspiration-tag {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 10rpx 16rpx;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: 20rpx;
  transition: all 0.2s;

  &:active {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.3);
  }
}

.tag-emoji {
  font-size: 20rpx;
}

.tag-text {
  font-size: 24rpx;
  color: $text-secondary;
}

// 底部操作区
.action-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: rgba(255, 251, 247, 0.95);
  backdrop-filter: blur(20rpx);
  border-top: 1rpx solid $border-light;
  z-index: 100;
}

.start-btn {
  position: relative;
  height: 100rpx;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: all 0.3s;

  // 根据内容类型应用不同的渐变色
  &.book {
    background: $book-gradient;
  }

  &.song {
    background: $song-gradient;
  }

  &.video {
    background: $video-gradient;
  }

  &.disabled {
    background: $border-medium !important;

    .btn-shine {
      display: none;
    }
  }

  &:active:not(.disabled) {
    transform: scale(0.98);
  }
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shine 2.5s infinite;
}

@keyframes shine {
  0% { left: -100%; }
  50%, 100% { left: 100%; }
}

.btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: 32rpx;
  font-weight: 600;
  color: white;
}
</style>
