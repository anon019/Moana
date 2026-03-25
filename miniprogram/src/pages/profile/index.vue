<template>
  <view class="page-container">
    <!-- 梦幻背景层 -->
    <view class="dreamy-bg">
      <view class="aurora aurora-1"></view>
      <view class="aurora aurora-2"></view>
      <view class="aurora aurora-3"></view>
      <view class="floating-orb orb-1"></view>
      <view class="floating-orb orb-2"></view>
      <view class="floating-orb orb-3"></view>
    </view>

    <!-- 自定义导航栏 -->
    <view class="nav-bar">
      <view class="nav-title">
        <view class="title-icon-wrap">
          <view class="icon-glow"></view>
          <text class="title-icon">👤</text>
        </view>
        <text class="title-text">我的</text>
      </view>
    </view>

    <scroll-view class="main-scroll" scroll-y>
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <view class="card-glow"></view>
        <view class="user-info">
          <view class="avatar-wrapper">
            <view class="avatar-ring"></view>
            <view class="avatar-ring-inner"></view>
            <image
              v-if="userStore.user?.avatar_url"
              class="avatar"
              :src="userStore.user.avatar_url"
              mode="aspectFill"
            />
            <view v-else class="avatar-placeholder">
              <text>{{ (userStore.user?.nickname || '用')[0] }}</text>
            </view>
            <view class="avatar-sparkle sparkle-1">✦</view>
            <view class="avatar-sparkle sparkle-2">✦</view>
          </view>
          <view class="user-detail">
            <text class="user-name">{{ userStore.user?.nickname || '未登录' }}</text>
            <view class="user-id-wrap">
              <text class="user-id-label">ID</text>
              <text class="user-id">{{ userStore.user?.id?.slice(0, 8) || '--------' }}</text>
            </view>
          </view>
          <view class="user-badge">
            <text class="badge-icon">⭐</text>
            <text class="badge-text">VIP</text>
          </view>
        </view>
      </view>

      <!-- 当前孩子 -->
      <view class="section">
        <view class="section-header">
          <view class="section-title-wrap">
            <view class="section-icon-bg">
              <text class="section-icon">👶</text>
            </view>
            <text class="section-title">我的宝贝</text>
          </view>
          <view class="section-action" @tap="goToAddChild">
            <text class="action-icon">✨</text>
            <text class="action-text">添加</text>
          </view>
        </view>

        <view v-if="childStore.children.length === 0" class="empty-child">
          <view class="empty-illustration">
            <view class="empty-ring ring-1"></view>
            <view class="empty-ring ring-2"></view>
            <text class="empty-emoji">👶</text>
          </view>
          <text class="empty-text">还没有添加宝贝</text>
          <view class="empty-btn" @tap="goToAddChild">
            <view class="btn-shimmer"></view>
            <text>✨ 添加宝贝</text>
          </view>
        </view>

        <view v-else class="child-list">
          <view
            v-for="child in childStore.children"
            :key="child.id"
            class="child-card"
            :class="{ active: childStore.currentChild?.id === child.id }"
            @tap="selectChild(child)"
          >
            <view class="child-card-glow" v-if="childStore.currentChild?.id === child.id"></view>
            <view class="child-avatar">
              <text>👶</text>
            </view>
            <view class="child-info">
              <text class="child-name">{{ child.name }}</text>
              <text class="child-age">{{ getChildAge(child.birth_date) }}</text>
            </view>
            <view v-if="childStore.currentChild?.id === child.id" class="child-check">
              <view class="check-ring"></view>
              <text>✓</text>
            </view>
            <view v-else class="child-select-hint">
              <text>点击选择</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 功能菜单 -->
      <view class="section">
        <view class="section-header">
          <view class="section-title-wrap">
            <view class="section-icon-bg icon-settings">
              <text class="section-icon">⚙️</text>
            </view>
            <text class="section-title">功能</text>
          </view>
        </view>

        <view class="menu-card">
          <view class="menu-item" @tap="goToFavorites">
            <view class="menu-icon-wrap icon-heart">
              <text class="menu-icon">❤️</text>
            </view>
            <view class="menu-content">
              <text class="menu-label">我的收藏</text>
              <text class="menu-desc">喜欢的内容</text>
            </view>
            <view class="menu-arrow">
              <text>›</text>
            </view>
          </view>

          <view class="menu-item" @tap="goToFeedback">
            <view class="menu-icon-wrap icon-chat">
              <text class="menu-icon">💬</text>
            </view>
            <view class="menu-content">
              <text class="menu-label">意见反馈</text>
              <text class="menu-desc">帮助我们改进</text>
            </view>
            <view class="menu-arrow">
              <text>›</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 更多 -->
      <view class="section">
        <view class="menu-card">
          <view class="menu-item" @tap="showAbout">
            <view class="menu-icon-wrap icon-info">
              <text class="menu-icon">ℹ️</text>
            </view>
            <view class="menu-content">
              <text class="menu-label">关于 Moana</text>
              <text class="menu-desc">版本 1.0.0</text>
            </view>
            <view class="menu-arrow">
              <text>›</text>
            </view>
          </view>

          <view class="menu-item logout" @tap="handleLogout">
            <view class="menu-icon-wrap icon-logout">
              <text class="menu-icon">🚪</text>
            </view>
            <view class="menu-content">
              <text class="menu-label">退出登录</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 底部装饰 -->
      <view class="footer-decor">
        <text class="footer-wave">〰️</text>
        <text class="footer-text">Made with ❤️ for kids</text>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { useChildStore, type Child } from '@/stores/child'

const userStore = useUserStore()
const childStore = useChildStore()

function getChildAge(birthDate: string | undefined | null): string {
  if (!birthDate) return '未知'

  const birth = new Date(birthDate)
  const now = new Date()
  const months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())

  if (months <= 0) return '刚出生'

  const years = Math.floor(months / 12)
  const remainMonths = months % 12
  if (years === 0) return `${remainMonths}个月`
  if (remainMonths === 0) return `${years}岁`
  return `${years}岁${remainMonths}个月`
}

function selectChild(child: Child) {
  childStore.setCurrentChild(child)
  uni.showToast({ title: `已切换到 ${child.name}`, icon: 'success' })
}

function goToAddChild() {
  uni.navigateTo({ url: '/pages/profile/add-child' })
}

function goToFavorites() {
  uni.navigateTo({ url: '/pages/favorites/index' })
}

function goToFeedback() {
  uni.navigateTo({ url: '/pages/feedback/index' })
}

function showAbout() {
  uni.showModal({
    title: '关于 Moana',
    content: 'Moana 是一款 AI 原生的早教内容生成平台，为 1-6 岁儿童提供个性化绘本、儿歌和视频内容。\n\n版本：1.0.0',
    showCancel: false,
    confirmText: '好的'
  })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.reLaunch({ url: '/pages/index/index' })
      }
    }
  })
}

onShow(() => {
  if (userStore.checkLogin() && !userStore.user) {
    userStore.fetchUser()
  }
  childStore.fetchChildren()
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

// === 梦幻背景层 ===
.dreamy-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(60rpx);
  opacity: 0.5;
  animation: auroraFloat 8s ease-in-out infinite;

  &.aurora-1 {
    width: 400rpx;
    height: 400rpx;
    background: linear-gradient(135deg, rgba(255, 182, 193, 0.6), rgba(255, 218, 185, 0.4));
    top: -100rpx;
    right: -80rpx;
    animation-delay: 0s;
  }

  &.aurora-2 {
    width: 300rpx;
    height: 300rpx;
    background: linear-gradient(135deg, rgba(176, 224, 230, 0.5), rgba(221, 160, 221, 0.3));
    bottom: 300rpx;
    left: -60rpx;
    animation-delay: -3s;
  }

  &.aurora-3 {
    width: 250rpx;
    height: 250rpx;
    background: linear-gradient(135deg, rgba(255, 228, 181, 0.5), rgba(255, 182, 193, 0.3));
    top: 40%;
    right: -40rpx;
    animation-delay: -5s;
  }
}

.floating-orb {
  position: absolute;
  border-radius: 50%;
  animation: orbFloat 6s ease-in-out infinite;

  &.orb-1 {
    width: 16rpx;
    height: 16rpx;
    background: rgba(255, 182, 193, 0.7);
    top: 200rpx;
    left: 60rpx;
    animation-delay: 0s;
  }

  &.orb-2 {
    width: 12rpx;
    height: 12rpx;
    background: rgba(176, 224, 230, 0.7);
    top: 500rpx;
    right: 80rpx;
    animation-delay: -2s;
  }

  &.orb-3 {
    width: 10rpx;
    height: 10rpx;
    background: rgba(221, 160, 221, 0.6);
    bottom: 400rpx;
    left: 120rpx;
    animation-delay: -4s;
  }
}

@keyframes auroraFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20rpx, -20rpx) scale(1.05); }
  66% { transform: translate(-10rpx, 15rpx) scale(0.95); }
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.7; }
  50% { transform: translateY(-20rpx) scale(1.2); opacity: 1; }
}

// === 导航栏 ===
.nav-bar {
  position: relative;
  z-index: 10;
  padding: calc(env(safe-area-inset-top) + 48rpx) 32rpx 24rpx;
}

.nav-title {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.title-icon-wrap {
  position: relative;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 56rpx;
  height: 56rpx;
  background: radial-gradient(circle, rgba(255, 182, 193, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.4; }
  50% { transform: translate(-50%, -50%) scale(1.3); opacity: 0.6; }
}

.title-icon {
  position: relative;
  font-size: 40rpx;
  z-index: 1;
}

.title-text {
  font-size: $font-xl;
  font-weight: $font-bold;
  color: $text-primary;
  letter-spacing: 2rpx;
}

// === 主滚动区 ===
.main-scroll {
  position: relative;
  z-index: 1;
  height: calc(100vh - 120rpx);
  padding: 0 32rpx;
  width: 750rpx;
  box-sizing: border-box;
}

// === 用户卡片 ===
.user-card {
  position: relative;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 36rpx;
  margin-bottom: 32rpx;
  box-shadow: $shadow-card;
  overflow: hidden;
}

.card-glow {
  position: absolute;
  top: -50%;
  right: -30%;
  width: 300rpx;
  height: 300rpx;
  background: radial-gradient(circle, rgba(255, 182, 193, 0.15) 0%, transparent 60%);
  border-radius: 50%;
  pointer-events: none;
}

.user-info {
  position: relative;
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
  width: 140rpx;
  height: 140rpx;
}

.avatar-ring {
  position: absolute;
  top: -8rpx;
  left: -8rpx;
  right: -8rpx;
  bottom: -8rpx;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    #FFB6C1,
    #DDA0DD,
    #B0E0E6,
    #98D8AA,
    #FFE4B5,
    #FFB6C1
  );
  animation: ringRotate 4s linear infinite;
}

.avatar-ring-inner {
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  right: 4rpx;
  bottom: 4rpx;
  border-radius: 50%;
  background: $bg-card;
}

@keyframes ringRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.avatar {
  position: absolute;
  top: 8rpx;
  left: 8rpx;
  width: 124rpx;
  height: 124rpx;
  border-radius: 50%;
  z-index: 1;
}

.avatar-placeholder {
  position: absolute;
  top: 8rpx;
  left: 8rpx;
  width: 124rpx;
  height: 124rpx;
  border-radius: 50%;
  background: $gradient-dreamy;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;

  text {
    font-size: 52rpx;
    color: $text-primary;
    font-weight: $font-bold;
  }
}

.avatar-sparkle {
  position: absolute;
  font-size: 20rpx;
  color: #FFD700;
  z-index: 2;
  animation: sparkle 1.5s ease-in-out infinite;

  &.sparkle-1 {
    top: 0;
    right: 8rpx;
    animation-delay: 0s;
  }

  &.sparkle-2 {
    bottom: 8rpx;
    left: 0;
    animation-delay: -0.7s;
  }
}

@keyframes sparkle {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 1; }
}

.user-detail {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 40rpx;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.user-id-wrap {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.user-id-label {
  font-size: 22rpx;
  color: $text-white;
  background: linear-gradient(135deg, #B0E0E6, #98D8AA);
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  font-weight: $font-medium;
}

.user-id {
  font-size: $font-sm;
  color: $text-tertiary;
  font-family: 'SF Mono', 'Monaco', monospace;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 8rpx 16rpx;
  background: linear-gradient(135deg, #FFE4B5, #FFD700);
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(255, 215, 0, 0.3);
}

.badge-icon {
  font-size: 24rpx;
}

.badge-text {
  font-size: 22rpx;
  font-weight: $font-bold;
  color: #8B4513;
}

// === 区块 ===
.section {
  margin-bottom: 32rpx;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  padding: 0 8rpx;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.section-icon-bg {
  width: 44rpx;
  height: 44rpx;
  border-radius: 12rpx;
  background: $gradient-dreamy;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-sm;

  &.icon-settings {
    background: linear-gradient(135deg, #B0E0E6, #87CEEB);
  }
}

.section-icon {
  font-size: 26rpx;
}

.section-title {
  font-size: $font-md;
  font-weight: $font-bold;
  color: $text-primary;
}

.section-action {
  display: flex;
  align-items: center;
  gap: 4rpx;
  padding: 8rpx 16rpx;
  background: rgba($primary, 0.1);
  border-radius: 20rpx;
}

.action-icon {
  font-size: 24rpx;
}

.action-text {
  font-size: 26rpx;
  color: $primary;
  font-weight: $font-medium;
}

// === 空状态 ===
.empty-child {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: 56rpx 48rpx;
  text-align: center;
  box-shadow: $shadow-card;
}

.empty-illustration {
  position: relative;
  width: 120rpx;
  height: 120rpx;
  margin: 0 auto 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-ring {
  position: absolute;
  border-radius: 50%;
  border: 2rpx solid;
  animation: emptyRingPulse 2s ease-out infinite;

  &.ring-1 {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-color: rgba($primary, 0.3);
    animation-delay: 0s;
  }

  &.ring-2 {
    top: -16rpx;
    left: -16rpx;
    right: -16rpx;
    bottom: -16rpx;
    border-color: rgba($primary, 0.15);
    animation-delay: -1s;
  }
}

@keyframes emptyRingPulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.4); opacity: 0; }
}

.empty-emoji {
  font-size: 56rpx;
  position: relative;
  z-index: 1;
}

.empty-text {
  display: block;
  font-size: $font-base;
  color: $text-tertiary;
  margin-bottom: 28rpx;
}

.empty-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 220rpx;
  height: 88rpx;
  background: $gradient-primary;
  border-radius: $radius-xl;
  box-shadow: $shadow-button;
  overflow: hidden;

  text {
    position: relative;
    z-index: 1;
    font-size: $font-base;
    font-weight: $font-semibold;
    color: $text-white;
  }

  &:active {
    transform: scale(0.96);
  }
}

.btn-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 2.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  50%, 100% { left: 100%; }
}

// === 孩子列表 ===
.child-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.child-card {
  position: relative;
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
  transition: all $duration-base $ease-out;
  overflow: hidden;

  &.active {
    border-color: $primary;
    background: rgba($primary, 0.03);

    .child-avatar {
      background: $gradient-primary;
    }
  }

  &:active {
    transform: scale(0.98);
  }
}

.child-card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(ellipse at top left, rgba($primary, 0.08) 0%, transparent 60%);
  pointer-events: none;
}

.child-avatar {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  border-radius: $radius-md;
  background: $gradient-dreamy;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: $shadow-sm;

  text {
    font-size: 40rpx;
  }
}

.child-info {
  flex: 1;
  margin-left: 20rpx;
}

.child-name {
  display: block;
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
}

.child-age {
  display: block;
  font-size: $font-sm;
  color: $text-tertiary;
  margin-top: 4rpx;
}

.child-check {
  position: relative;
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: $gradient-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-button;

  text {
    font-size: 26rpx;
    color: $text-white;
    font-weight: $font-bold;
    position: relative;
    z-index: 1;
  }
}

.check-ring {
  position: absolute;
  top: -4rpx;
  left: -4rpx;
  right: -4rpx;
  bottom: -4rpx;
  border-radius: 50%;
  border: 2rpx solid rgba($primary, 0.3);
  animation: checkPulse 1.5s ease-out infinite;
}

@keyframes checkPulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.child-select-hint {
  text {
    font-size: 24rpx;
    color: $text-placeholder;
  }
}

// === 菜单 ===
.menu-card {
  background: $bg-card;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: $shadow-card;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid $border-light;
  transition: background $duration-fast $ease-out;

  &:last-child {
    border-bottom: none;
  }

  &:active {
    background: $bg-soft;
  }

  &.logout {
    .menu-label {
      color: $error;
    }
  }
}

.menu-icon-wrap {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  box-shadow: $shadow-sm;

  &.icon-heart {
    background: linear-gradient(135deg, rgba(255, 107, 129, 0.15), rgba(233, 30, 99, 0.15));
  }
  &.icon-chat {
    background: linear-gradient(135deg, rgba(152, 216, 170, 0.15), rgba(76, 175, 80, 0.15));
  }
  &.icon-info {
    background: linear-gradient(135deg, rgba(176, 224, 230, 0.15), rgba(100, 181, 246, 0.15));
  }
  &.icon-logout {
    background: linear-gradient(135deg, rgba(239, 83, 80, 0.15), rgba(244, 67, 54, 0.15));
  }
}

.menu-icon {
  font-size: 32rpx;
}

.menu-content {
  flex: 1;
}

.menu-label {
  display: block;
  font-size: $font-md;
  color: $text-primary;
  font-weight: $font-medium;
}

.menu-desc {
  display: block;
  font-size: 24rpx;
  color: $text-tertiary;
  margin-top: 4rpx;
}

.menu-arrow {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  text {
    font-size: 36rpx;
    color: $text-placeholder;
  }
}

// === 底部装饰 ===
.footer-decor {
  text-align: center;
  padding: 40rpx 0 20rpx;
}

.footer-wave {
  display: block;
  font-size: 32rpx;
  opacity: 0.3;
  margin-bottom: 12rpx;
}

.footer-text {
  font-size: 24rpx;
  color: $text-placeholder;
  letter-spacing: 1rpx;
}

// === 底部安全区 ===
.safe-bottom {
  height: calc(env(safe-area-inset-bottom) + 120rpx);
}
</style>
