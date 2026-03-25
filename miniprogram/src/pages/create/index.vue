<template>
  <view class="page-container">
    <!-- 梦幻背景 -->
    <view class="magic-bg">
      <view class="magic-aurora a1"></view>
      <view class="magic-aurora a2"></view>
      <view class="magic-aurora a3"></view>
      <view class="magic-stars">
        <view class="star s1">✦</view>
        <view class="star s2">✧</view>
        <view class="star s3">⋆</view>
        <view class="star s4">✦</view>
        <view class="star s5">✧</view>
      </view>
    </view>

    <!-- 主内容区 -->
    <scroll-view class="main-scroll" scroll-y enhanced :show-scrollbar="false">
      <!-- 顶部导航区 -->
      <view class="nav-section">
        <view class="nav-back" @tap="goBack">
          <text class="back-icon">←</text>
        </view>
      </view>

      <!-- 页面头部 - 全新设计 -->
      <view class="header-section">
        <view class="header-magic-ring">
          <view class="ring-glow"></view>
          <view class="ring-icon">
            <text>✨</text>
          </view>
        </view>
        <view class="header-content">
          <view class="header-badge">
            <text class="badge-dot"></text>
            <text class="badge-label">创作工坊</text>
          </view>
          <text class="header-title">魔法创作中心</text>
          <text class="header-subtitle">为 {{ childName }} 创造独一无二的内容</text>
        </view>
      </view>

      <!-- 创作卡片区 - 全新沉浸式设计 -->
      <view class="creation-gallery">
        <!-- 绘本卡片 - 主推大卡片 -->
        <view class="gallery-card card-book" @tap="goToPictureBook">
          <view class="card-shine"></view>
          <view class="card-pattern">
            <view class="pattern-circle pc1"></view>
            <view class="pattern-circle pc2"></view>
            <view class="pattern-circle pc3"></view>
          </view>
          <view class="card-content">
            <view class="card-header">
              <view class="card-badge badge-hot">
                <text class="badge-star">★</text>
                <text class="badge-text">推荐</text>
              </view>
            </view>
            <view class="card-visual">
              <view class="visual-rings">
                <view class="v-ring vr1"></view>
                <view class="v-ring vr2"></view>
                <view class="v-ring vr3"></view>
              </view>
              <view class="visual-icon">
                <text>📚</text>
              </view>
              <view class="visual-particles">
                <view class="particle p1">✦</view>
                <view class="particle p2">✧</view>
                <view class="particle p3">⋆</view>
              </view>
            </view>
            <view class="card-info">
              <text class="card-title">AI 绘本</text>
              <text class="card-desc">个性化故事，独特插画</text>
              <view class="card-features">
                <view class="feature">
                  <text class="feature-icon">🎨</text>
                  <text class="feature-text">多种画风</text>
                </view>
                <view class="feature">
                  <text class="feature-icon">👶</text>
                  <text class="feature-text">宝贝主角</text>
                </view>
                <view class="feature">
                  <text class="feature-icon">🎯</text>
                  <text class="feature-text">教育主题</text>
                </view>
              </view>
            </view>
            <view class="card-action">
              <view class="action-btn">
                <text class="action-text">开始创作</text>
                <view class="action-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 儿歌和视频卡片 - 双列布局 -->
        <view class="gallery-row">
          <!-- 儿歌卡片 -->
          <view class="gallery-card-sm card-song" @tap="goToNurseryRhyme">
            <view class="card-shine"></view>
            <view class="sm-content">
              <view class="sm-badge">
                <text>New</text>
              </view>
              <view class="sm-visual">
                <view class="sm-icon">
                  <text>🎵</text>
                </view>
                <view class="sm-waves">
                  <view class="wave w1"></view>
                  <view class="wave w2"></view>
                  <view class="wave w3"></view>
                  <view class="wave w4"></view>
                </view>
              </view>
              <view class="sm-info">
                <text class="sm-title">AI 儿歌</text>
                <text class="sm-desc">原创旋律，专属歌词</text>
                <text class="sm-detail">唱出宝贝的故事</text>
              </view>
              <view class="sm-action">
                <view class="sm-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>
          </view>

          <!-- 视频卡片 -->
          <view class="gallery-card-sm card-video" @tap="goToVideo">
            <view class="card-shine"></view>
            <view class="sm-content">
              <view class="sm-badge">
                <text>New</text>
              </view>
              <view class="sm-visual">
                <view class="sm-icon">
                  <text>🎬</text>
                </view>
                <view class="sm-play">
                  <view class="play-ring"></view>
                  <text class="play-icon">▶</text>
                </view>
              </view>
              <view class="sm-info">
                <text class="sm-title">AI 视频</text>
                <text class="sm-desc">绘本动态化</text>
                <text class="sm-detail">让故事动起来</text>
              </view>
              <view class="sm-action">
                <view class="sm-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 智能创作区 - 全新设计 -->
      <view class="smart-section">
        <view class="smart-header">
          <view class="smart-icon-area">
            <view class="smart-glow"></view>
            <view class="smart-ring"></view>
            <view class="smart-icon">
              <text>🔮</text>
            </view>
          </view>
          <view class="smart-title-area">
            <text class="smart-title">智能创作</text>
            <text class="smart-subtitle">描述你的需求，AI 自动匹配最佳创作方式</text>
          </view>
        </view>

        <view class="smart-input-card">
          <view class="input-card-glow"></view>
          <view class="input-wrapper">
            <view class="input-decor">
              <text class="decor-icon">💭</text>
            </view>
            <textarea
              v-model="aiInput"
              class="smart-textarea"
              :placeholder="currentPlaceholder"
              :maxlength="200"
              auto-height
            />
            <view class="input-counter">
              <text>{{ aiInput.length }}/200</text>
            </view>
          </view>

          <!-- 快捷灵感标签 -->
          <view class="inspiration-tags">
            <view class="tags-label">
              <text class="label-icon">💡</text>
              <text class="label-text">快捷灵感</text>
              <text class="label-count">{{ inspirationItems.length }} 个主题</text>
            </view>
            <view class="tags-list">
              <view
                v-for="(item, index) in inspirationItems"
                :key="index"
                class="tag-item"
                @tap="fillTip(item.prompt)"
              >
                <text class="tag-emoji">{{ item.emoji }}</text>
                <text class="tag-text">{{ item.text }}</text>
              </view>
            </view>
          </view>

          <!-- 提交按钮 -->
          <view
            class="submit-btn"
            :class="{ disabled: !aiInput.trim() }"
            @tap="handleAICreate"
          >
            <view class="btn-bg">
              <view class="btn-shimmer"></view>
            </view>
            <view class="btn-content">
              <view class="btn-icon-wrap">
                <text class="btn-icon">✨</text>
              </view>
              <text class="btn-text">开始魔法创作</text>
              <view class="btn-arrow">
                <text>→</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useChildStore } from '@/stores/child'

const childStore = useChildStore()

const aiInput = ref('')

const childName = computed(() => childStore.currentChild?.name || '宝贝')

// 占位符示例池（不带内容类型预设）
const placeholderExamples = [
  '例如：宝宝最近不爱吃蔬菜，需要培养吃蔬菜的好习惯',
  '例如：宝宝不爱刷牙，帮我做一个关于刷牙习惯的内容',
  '例如：宝宝晚上不愿意睡觉，需要建立早睡早起的作息',
  '例如：宝宝不愿意和小朋友分享玩具，需要学会分享',
  '例如：宝宝胆小害羞，需要培养勇敢自信的性格',
  '例如：教宝宝认识各种小动物及它们的特点',
  '例如：宝宝容易发脾气，需要学会管理情绪',
  '例如：教宝宝安全过马路，遵守交通规则',
  '例如：带宝宝来一场充满想象力的太空冒险',
  '例如：教宝宝学会说谢谢、对不起等礼貌用语'
]

// 当前显示的占位符
const currentPlaceholder = ref('')

// 随机选择占位符
function randomizePlaceholder() {
  const randomIndex = Math.floor(Math.random() * placeholderExamples.length)
  currentPlaceholder.value = placeholderExamples[randomIndex]
}

// 快捷灵感数据（25个，精简版）
const inspirationItems = [
  // 生活习惯类 (5)
  { emoji: '🦷', text: '刷牙习惯', prompt: '宝宝不爱刷牙，需要培养刷牙的好习惯' },
  { emoji: '🥦', text: '吃蔬菜', prompt: '宝宝不爱吃蔬菜，帮我做一个关于吃蔬菜的内容' },
  { emoji: '🛏', text: '早睡早起', prompt: '宝宝晚上不愿意睡觉，需要建立作息规律' },
  { emoji: '🚿', text: '洗澡洗手', prompt: '教宝宝养成爱干净的好习惯' },
  { emoji: '🧸', text: '收拾玩具', prompt: '教宝宝学会收拾玩具，养成整理的习惯' },

  // 情绪社交类 (5)
  { emoji: '🖐', text: '学会分享', prompt: '宝宝不愿意和小朋友分享玩具' },
  { emoji: '👭', text: '交朋友', prompt: '帮助宝宝学会如何交朋友，融入集体' },
  { emoji: '💬', text: '礼貌用语', prompt: '教宝宝学会说谢谢、对不起等礼貌用语' },
  { emoji: '😌', text: '情绪管理', prompt: '宝宝容易发脾气，帮助学会管理情绪' },
  { emoji: '💪', text: '勇敢自信', prompt: '宝宝胆小害羞，需要培养勇敢自信的性格' },

  // 认知学习类 (7)
  { emoji: '🐰', text: '认识动物', prompt: '帮宝宝认识各种小动物及它们的特点' },
  { emoji: '🎨', text: '认识颜色', prompt: '教宝宝认识和区分各种颜色' },
  { emoji: '🔢', text: '学习数数', prompt: '用有趣的方式教宝宝学会数数' },
  { emoji: '🔺', text: '认识形状', prompt: '教宝宝认识圆形、三角形、正方形等形状' },
  { emoji: '🌈', text: '认识天气', prompt: '教宝宝认识晴天、雨天、雪天等天气' },
  { emoji: '🍊', text: '认识水果', prompt: '带宝宝认识各种水果的名称和特征' },
  { emoji: '🏠', text: '认识家人', prompt: '教宝宝认识家庭成员和亲情关系' },

  // 安全教育类 (3)
  { emoji: '🚦', text: '过马路', prompt: '教宝宝安全过马路，遵守交通规则' },
  { emoji: '👨‍👩‍👧', text: '不跟陌生人', prompt: '教育宝宝不要跟陌生人走，保护自己' },
  { emoji: '🔥', text: '防火安全', prompt: '教宝宝认识火灾危险，学会基本的防火知识' },

  // 想象探索类 (5)
  { emoji: '🚀', text: '太空冒险', prompt: '带宝宝来一场充满想象力的太空冒险' },
  { emoji: '🐠', text: '海底世界', prompt: '探索神奇的海底世界，认识海洋生物' },
  { emoji: '🌲', text: '森林探险', prompt: '在魔法森林里展开一场奇妙的冒险' },
  { emoji: '🦕', text: '恐龙世界', prompt: '穿越到恐龙时代，认识各种恐龙' },
  { emoji: '👸', text: '童话王国', prompt: '走进美丽的童话王国，遇见童话人物' }
]

function goBack() {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

function goToPictureBook() {
  uni.navigateTo({ url: '/pages/create/picture-book' })
}

function goToNurseryRhyme() {
  uni.navigateTo({ url: '/pages/create/nursery-rhyme' })
}

function goToVideo() {
  uni.navigateTo({ url: '/pages/create/video' })
}

function fillTip(text: string) {
  aiInput.value = text
}

async function handleAICreate() {
  if (!aiInput.value.trim()) return
  uni.navigateTo({
    url: `/pages/create/smart?input=${encodeURIComponent(aiInput.value)}`
  })
}

onShow(() => {
  // 每次进入页面时随机选择占位符
  randomizePlaceholder()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.page-container {
  min-height: 100vh;
  background: $bg-cream;
  width: 750rpx;
  position: relative;
  overflow: hidden;
}

// ============================================
// 梦幻背景
// ============================================
.magic-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.magic-aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(80rpx);
  opacity: 0.5;

  &.a1 {
    width: 450rpx;
    height: 450rpx;
    background: linear-gradient(135deg, $book-light 0%, rgba($book-primary, 0.4) 100%);
    top: -100rpx;
    right: -80rpx;
    animation: auroraMove 10s ease-in-out infinite;
  }

  &.a2 {
    width: 380rpx;
    height: 380rpx;
    background: linear-gradient(135deg, $song-light 0%, rgba($song-primary, 0.4) 100%);
    top: 35%;
    left: -100rpx;
    animation: auroraMove 12s ease-in-out infinite 2s;
  }

  &.a3 {
    width: 320rpx;
    height: 320rpx;
    background: linear-gradient(135deg, $video-light 0%, rgba($video-primary, 0.4) 100%);
    bottom: 10%;
    right: -60rpx;
    animation: auroraMove 14s ease-in-out infinite 4s;
  }
}

@keyframes auroraMove {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30rpx, -20rpx) scale(1.1); }
  50% { transform: translate(-20rpx, 30rpx) scale(0.95); }
  75% { transform: translate(15rpx, 15rpx) scale(1.05); }
}

.magic-stars {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.star {
  position: absolute;
  color: $accent;
  opacity: 0.6;
  animation: starFloat 4s ease-in-out infinite;

  &.s1 { top: 15%; left: 20%; font-size: 24rpx; animation-delay: 0s; }
  &.s2 { top: 25%; right: 15%; font-size: 20rpx; animation-delay: 0.8s; }
  &.s3 { top: 45%; left: 10%; font-size: 18rpx; animation-delay: 1.6s; }
  &.s4 { top: 60%; right: 25%; font-size: 22rpx; animation-delay: 2.4s; }
  &.s5 { top: 80%; left: 30%; font-size: 20rpx; animation-delay: 3.2s; }
}

@keyframes starFloat {
  0%, 100% { opacity: 0.3; transform: translateY(0) rotate(0deg); }
  50% { opacity: 0.8; transform: translateY(-20rpx) rotate(180deg); }
}

// ============================================
// 主滚动区
// ============================================
.main-scroll {
  position: relative;
  z-index: 1;
  height: 100vh;
  padding: 0 32rpx;
  width: 750rpx;
  box-sizing: border-box;
}

// ============================================
// 导航区
// ============================================
.nav-section {
  padding-top: calc(env(safe-area-inset-top) + 24rpx);
  padding-bottom: 16rpx;
}

.nav-back {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: $radius-xl;
  box-shadow: $shadow-md;
  border: 1rpx solid rgba(255, 255, 255, 0.8);

  &:active {
    transform: scale(0.92);
    background: rgba(255, 255, 255, 0.95);
  }
}

.back-icon {
  font-size: 40rpx;
  color: $text-secondary;
  font-weight: 300;
}

// ============================================
// 页面头部
// ============================================
.header-section {
  text-align: center;
  padding: 24rpx 0 48rpx;
}

.header-magic-ring {
  position: relative;
  width: 100rpx;
  height: 100rpx;
  margin: 0 auto 24rpx;
}

.ring-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: $gradient-dreamy;
  filter: blur(20rpx);
  opacity: 0.6;
  animation: ringGlow 3s ease-in-out infinite;
}

@keyframes ringGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.2); opacity: 0.4; }
}

.ring-icon {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  box-shadow: $shadow-lg;

  text {
    font-size: 48rpx;
  }
}

.header-content {
  position: relative;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 10rpx;
  padding: 10rpx 24rpx;
  background: rgba($accent, 0.1);
  border: 1rpx solid rgba($accent, 0.2);
  border-radius: $radius-full;
  margin-bottom: 20rpx;
}

.badge-dot {
  width: 12rpx;
  height: 12rpx;
  background: $accent;
  border-radius: 50%;
  animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
}

.badge-label {
  font-size: 24rpx;
  color: $accent;
  font-weight: 600;
}

.header-title {
  display: block;
  font-size: 56rpx;
  font-weight: 800;
  color: $text-primary;
  letter-spacing: 3rpx;
  margin-bottom: 12rpx;
}

.header-subtitle {
  display: block;
  font-size: 28rpx;
  color: $text-tertiary;
}

// ============================================
// 创作卡片区
// ============================================
.creation-gallery {
  margin-bottom: 48rpx;
}

// 主推大卡片
.gallery-card {
  position: relative;
  border-radius: 40rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
  box-shadow: $shadow-xl;

  &:active {
    transform: scale(0.98);
  }

  &.card-book {
    background: linear-gradient(160deg, #FFF9F6 0%, $book-light 40%, rgba($book-primary, 0.15) 100%);
    border: 1rpx solid rgba($book-primary, 0.1);

    .card-badge { background: $book-primary; }
    .v-ring { border-color: rgba($book-primary, 0.15); }
    .action-btn { background: $book-gradient; box-shadow: $shadow-colored-book; }
    .particle { color: $book-primary; }
  }
}

.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: cardShine 4s ease-in-out infinite;
}

@keyframes cardShine {
  0% { left: -100%; }
  50%, 100% { left: 150%; }
}

.card-pattern {
  position: absolute;
  top: 0;
  right: 0;
  width: 60%;
  height: 100%;
  pointer-events: none;
}

.pattern-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba($book-primary, 0.05);

  &.pc1 {
    width: 200rpx;
    height: 200rpx;
    top: -40rpx;
    right: -40rpx;
  }

  &.pc2 {
    width: 150rpx;
    height: 150rpx;
    top: 50%;
    right: 20%;
  }

  &.pc3 {
    width: 100rpx;
    height: 100rpx;
    bottom: 20rpx;
    right: 40%;
  }
}

.card-content {
  position: relative;
  z-index: 1;
  padding: 40rpx;
}

.card-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20rpx;
}

.card-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 20rpx;
  border-radius: $radius-full;

  .badge-star {
    font-size: 20rpx;
    color: #fff;
  }

  .badge-text {
    font-size: 24rpx;
    color: #fff;
    font-weight: 600;
  }
}

.card-visual {
  position: relative;
  width: 140rpx;
  height: 140rpx;
  margin-bottom: 32rpx;
}

.visual-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 140rpx;
  height: 140rpx;
}

.v-ring {
  position: absolute;
  border-radius: 50%;
  border: 2rpx solid;

  &.vr1 {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    animation: vRingPulse 3s ease-out infinite;
  }

  &.vr2 {
    top: -15rpx;
    left: -15rpx;
    right: -15rpx;
    bottom: -15rpx;
    opacity: 0.6;
    animation: vRingPulse 3s ease-out infinite 0.5s;
  }

  &.vr3 {
    top: -30rpx;
    left: -30rpx;
    right: -30rpx;
    bottom: -30rpx;
    opacity: 0.3;
    animation: vRingPulse 3s ease-out infinite 1s;
  }
}

@keyframes vRingPulse {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(1.4); opacity: 0; }
}

.visual-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  text {
    font-size: 72rpx;
  }
}

.visual-particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.particle {
  position: absolute;
  font-size: 20rpx;
  animation: particleFloat 3s ease-in-out infinite;

  &.p1 { top: 10rpx; right: 20rpx; animation-delay: 0s; }
  &.p2 { bottom: 20rpx; right: 0; animation-delay: 0.5s; }
  &.p3 { top: 50%; left: -20rpx; animation-delay: 1s; }
}

@keyframes particleFloat {
  0%, 100% { opacity: 0.4; transform: translateY(0) rotate(0deg); }
  50% { opacity: 1; transform: translateY(-15rpx) rotate(180deg); }
}

.card-info {
  margin-bottom: 32rpx;
}

.card-title {
  display: block;
  font-size: 52rpx;
  font-weight: 800;
  color: $text-primary;
  margin-bottom: 12rpx;
}

.card-desc {
  display: block;
  font-size: 30rpx;
  color: $text-secondary;
  margin-bottom: 24rpx;
}

.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.feature {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  background: rgba(255, 255, 255, 0.8);
  border-radius: $radius-full;
  border: 1rpx solid rgba($book-primary, 0.1);
}

.feature-icon {
  font-size: 22rpx;
}

.feature-text {
  font-size: 24rpx;
  color: $text-secondary;
}

.card-action {
  display: flex;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx 40rpx;
  border-radius: $radius-2xl;
}

.action-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.action-arrow {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;

  text {
    font-size: 28rpx;
    color: #fff;
  }
}

// 双列卡片
.gallery-row {
  display: flex;
  gap: 20rpx;
}

.gallery-card-sm {
  flex: 1;
  position: relative;
  border-radius: 32rpx;
  overflow: hidden;
  box-shadow: $shadow-lg;

  &:active {
    transform: scale(0.96);
  }

  &.card-song {
    background: linear-gradient(160deg, #F9FFF9 0%, $song-light 50%, rgba($song-primary, 0.15) 100%);
    border: 1rpx solid rgba($song-primary, 0.1);

    .sm-badge { background: $song-primary; }
    .wave { background: $song-primary; }
    .sm-arrow { background: $song-gradient; box-shadow: $shadow-colored-song; }
  }

  &.card-video {
    background: linear-gradient(160deg, #FFFEF8 0%, $video-light 50%, rgba($video-primary, 0.15) 100%);
    border: 1rpx solid rgba($video-primary, 0.1);

    .sm-badge { background: $video-primary; }
    .play-ring { border-color: rgba($video-primary, 0.3); }
    .play-icon { color: $video-primary; }
    .sm-arrow { background: $video-gradient; box-shadow: $shadow-colored-video; }
  }
}

.sm-content {
  position: relative;
  z-index: 1;
  padding: 28rpx;
}

.sm-badge {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  padding: 6rpx 14rpx;
  border-radius: $radius-full;

  text {
    font-size: 20rpx;
    color: #fff;
    font-weight: 600;
  }
}

.sm-visual {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  margin-bottom: 20rpx;
}

.sm-icon {
  position: relative;
  z-index: 1;

  text {
    font-size: 52rpx;
  }
}

.sm-waves {
  position: absolute;
  top: 8rpx;
  right: -24rpx;
  display: flex;
  gap: 4rpx;
  align-items: flex-end;
  height: 32rpx;
}

.wave {
  width: 4rpx;
  border-radius: 2rpx;
  animation: waveHeight 1s ease-in-out infinite;

  &.w1 { height: 12rpx; animation-delay: 0s; }
  &.w2 { height: 24rpx; animation-delay: 0.15s; }
  &.w3 { height: 18rpx; animation-delay: 0.3s; }
  &.w4 { height: 28rpx; animation-delay: 0.45s; }
}

@keyframes waveHeight {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.4); }
}

.sm-play {
  position: absolute;
  top: 0;
  right: -20rpx;
  width: 36rpx;
  height: 36rpx;
}

.play-ring {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  border: 2rpx solid;
  animation: playRingPulse 2s ease-out infinite;
}

@keyframes playRingPulse {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.5); opacity: 0; }
}

.play-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16rpx;
}

.sm-info {
  margin-bottom: 20rpx;
}

.sm-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 6rpx;
}

.sm-desc {
  display: block;
  font-size: 26rpx;
  color: $text-secondary;
  margin-bottom: 4rpx;
}

.sm-detail {
  display: block;
  font-size: 24rpx;
  color: $text-tertiary;
}

.sm-action {
  display: flex;
  justify-content: flex-end;
}

.sm-arrow {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;

  text {
    font-size: 28rpx;
    color: #fff;
    font-weight: 600;
  }
}

// ============================================
// 智能创作区
// ============================================
.smart-section {
  margin-bottom: 32rpx;
}

.smart-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 28rpx;
}

.smart-icon-area {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  flex-shrink: 0;
}

.smart-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: $radius-lg;
  background: $gradient-dreamy;
  filter: blur(16rpx);
  opacity: 0.6;
  animation: smartGlow 3s ease-in-out infinite;
}

@keyframes smartGlow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.smart-ring {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: $radius-lg;
  border: 2rpx solid rgba($primary, 0.2);
  animation: smartRingSpin 8s linear infinite;
}

@keyframes smartRingSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.smart-icon {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: $radius-lg;
  box-shadow: $shadow-md;

  text {
    font-size: 44rpx;
  }
}

.smart-title-area {
  flex: 1;
}

.smart-title {
  display: block;
  font-size: $font-lg;
  font-weight: 700;
  color: $text-primary;
}

.smart-subtitle {
  display: block;
  font-size: $font-sm;
  color: $text-tertiary;
  margin-top: 4rpx;
}

// 输入卡片
.smart-input-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 36rpx;
  padding: 32rpx;
  box-shadow: $shadow-lg;
  border: 1rpx solid rgba(255, 255, 255, 0.8);
  overflow: hidden;
}

.input-card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 30%, rgba($primary, 0.03) 0%, transparent 50%);
  pointer-events: none;
}

.input-wrapper {
  position: relative;
  margin-bottom: 24rpx;
}

.input-decor {
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  opacity: 0.5;
}

.decor-icon {
  font-size: 28rpx;
}

.smart-textarea {
  width: 100%;
  min-height: 140rpx;
  padding: 56rpx 20rpx 40rpx 20rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  font-size: $font-base;
  color: $text-primary;
  line-height: 1.7;
  box-sizing: border-box;

  &::placeholder {
    color: $text-placeholder;
  }
}

.input-counter {
  position: absolute;
  bottom: 16rpx;
  right: 20rpx;

  text {
    font-size: 22rpx;
    color: $text-placeholder;
  }
}

// 灵感标签
.inspiration-tags {
  margin-bottom: 28rpx;
}

.tags-label {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.label-icon {
  font-size: 22rpx;
}

.label-text {
  font-size: 24rpx;
  color: $text-tertiary;
  font-weight: 500;
}

.label-count {
  margin-left: auto;
  font-size: 20rpx;
  color: $text-placeholder;
  background: rgba($primary, 0.06);
  padding: 4rpx 12rpx;
  border-radius: $radius-full;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 16rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-full;

  &:active {
    background: rgba($primary, 0.08);
    border-color: $primary-light;
  }
}

.tag-emoji {
  font-size: 20rpx;
}

.tag-text {
  font-size: 24rpx;
  color: $text-secondary;
}

// 提交按钮
.submit-btn {
  position: relative;
  height: 108rpx;
  border-radius: 54rpx;
  overflow: hidden;

  &:active {
    transform: scale(0.98);
  }

  &.disabled {
    .btn-bg {
      background: $bg-soft;
    }

    .btn-shimmer {
      display: none;
    }

    .btn-text {
      color: $text-placeholder;
    }

    .btn-icon-wrap {
      background: transparent;
    }

    .btn-arrow {
      opacity: 0.3;
    }
  }
}

.btn-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: $gradient-primary;
  box-shadow: $shadow-button;
}

.btn-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: btnShimmer 3s ease-in-out infinite;
}

@keyframes btnShimmer {
  0% { left: -100%; }
  50%, 100% { left: 150%; }
}

.btn-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}

.btn-icon-wrap {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.btn-icon {
  font-size: 28rpx;
}

.btn-text {
  font-size: 34rpx;
  font-weight: 600;
  color: #fff;
}

.btn-arrow {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;

  text {
    font-size: 28rpx;
    color: #fff;
  }
}

// ============================================
// 底部安全区
// ============================================
.safe-bottom {
  height: calc(env(safe-area-inset-bottom) + 100rpx);
}
</style>
