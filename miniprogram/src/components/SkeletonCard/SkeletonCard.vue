<template>
  <view class="skeleton-card" :class="type">
    <view class="skeleton-cover skeleton-animate"></view>
    <view class="skeleton-content">
      <view class="skeleton-title skeleton-animate"></view>
      <view class="skeleton-desc skeleton-animate"></view>
    </view>
  </view>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  type?: 'horizontal' | 'vertical'
}>(), {
  type: 'vertical'
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.skeleton-card {
  display: flex;
  background: $bg-card;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: $shadow-card;

  &.horizontal {
    flex-direction: row;
    padding: $spacing-md;
    margin-bottom: $spacing-md;

    .skeleton-cover {
      width: 160rpx;
      height: 120rpx;
      border-radius: $radius-md;
      margin-right: $spacing-md;
      flex-shrink: 0;
    }
  }

  &.vertical {
    flex-direction: column;

    .skeleton-cover {
      width: 100%;
      height: 200rpx;
    }

    .skeleton-content {
      padding: $spacing-sm;
    }
  }
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: $spacing-sm;
}

.skeleton-title {
  height: 32rpx;
  width: 70%;
  border-radius: $radius-sm;
}

.skeleton-desc {
  height: 24rpx;
  width: 45%;
  border-radius: $radius-sm;
}

.skeleton-animate {
  background: linear-gradient(
    90deg,
    $border-light 25%,
    $bg-soft 50%,
    $border-light 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
