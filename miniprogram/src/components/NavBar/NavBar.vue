<template>
  <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
    <!-- 背景装饰 -->
    <view class="nav-bg">
      <view class="blob blob-1"></view>
      <view class="blob blob-2"></view>
    </view>

    <!-- 导航内容 -->
    <view class="nav-content">
      <view class="nav-left">
        <view v-if="showBack" class="back-btn" @tap="handleBack">
          <text class="back-icon">‹</text>
        </view>
        <view v-else class="brand">
          <view class="brand-icon">
            <text class="wave-emoji">🌊</text>
          </view>
          <text class="brand-name">Moana</text>
        </view>
      </view>

      <view class="nav-center">
        <text v-if="title" class="nav-title">{{ title }}</text>
      </view>

      <view class="nav-right">
        <slot name="right">
          <view v-if="showAvatar" class="avatar-wrapper" @tap="$emit('avatar-tap')">
            <image
              v-if="avatarUrl"
              class="avatar"
              :src="avatarUrl"
              mode="aspectFill"
            />
            <view v-else class="avatar-placeholder">
              <text>👶</text>
            </view>
          </view>
        </slot>
      </view>
    </view>
  </view>

  <!-- 占位 -->
  <view class="nav-placeholder" :style="{ height: navHeight + 'px' }"></view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  title?: string
  showBack?: boolean
  showAvatar?: boolean
  avatarUrl?: string
}>()

const emit = defineEmits(['back', 'avatar-tap'])

const statusBarHeight = ref(20)
const navHeight = ref(88)

onMounted(() => {
  const sysInfo = uni.getSystemInfoSync()
  statusBarHeight.value = sysInfo.statusBarHeight || 20
  navHeight.value = statusBarHeight.value + 44
})

function handleBack() {
  emit('back')
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: $z-sticky;
  background: $bg-base;
  overflow: hidden;
}

.nav-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;

  .blob {
    position: absolute;
    border-radius: 50%;
    opacity: 0.4;
  }

  .blob-1 {
    width: 200rpx;
    height: 200rpx;
    background: $accent-soft;
    top: -100rpx;
    left: -50rpx;
  }

  .blob-2 {
    width: 150rpx;
    height: 150rpx;
    background: rgba($primary, 0.1);
    top: -50rpx;
    right: 50rpx;
  }
}

.nav-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 $spacing-md;
}

.nav-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  border-radius: $radius-md;
  background: $bg-card;
  box-shadow: $shadow-sm;

  .back-icon {
    font-size: 48rpx;
    color: $text-primary;
    line-height: 1;
    margin-top: -4rpx;
  }
}

.brand {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.brand-icon {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $gradient-primary;
  border-radius: $radius-sm;
  box-shadow: $shadow-button;

  .wave-emoji {
    font-size: 28rpx;
  }
}

.brand-name {
  font-size: $font-lg;
  font-weight: $font-bold;
  color: $text-primary;
  letter-spacing: 1rpx;
}

.nav-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.nav-title {
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
}

.nav-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  border: 4rpx solid $bg-card;
  box-shadow: $shadow-md;
}

.avatar-placeholder {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: $gradient-warm;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  border: 4rpx solid $bg-card;
  box-shadow: $shadow-md;
}

.nav-placeholder {
  width: 100%;
}
</style>
