<template>
  <view class="loading-state">
    <view class="loading-icon animate-spin">
      <text>{{ icon }}</text>
    </view>
    <text class="loading-text">{{ text }}</text>
  </view>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  text?: string
  icon?: string
}>(), {
  text: '加载中...',
  icon: '🌊'
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx $spacing-lg;
}

.loading-icon {
  font-size: 80rpx;
  margin-bottom: $spacing-md;
}

.loading-text {
  font-size: $font-base;
  color: $text-secondary;
}

.animate-spin {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
