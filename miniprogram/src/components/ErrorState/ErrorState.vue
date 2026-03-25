<template>
  <view class="error-state">
    <text class="error-icon">{{ icon }}</text>
    <text class="error-title">{{ title }}</text>
    <text v-if="message" class="error-message">{{ message }}</text>
    <view class="error-action" @tap="$emit('retry')">
      <text>{{ retryText }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  title?: string
  message?: string
  retryText?: string
}>(), {
  icon: '😢',
  title: '出错了',
  retryText: '重试'
})

defineEmits<{
  retry: []
}>()
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx $spacing-lg;
  text-align: center;
}

.error-icon {
  font-size: 100rpx;
  margin-bottom: $spacing-md;
}

.error-title {
  font-size: $font-lg;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.error-message {
  font-size: $font-sm;
  color: $text-secondary;
  margin-bottom: $spacing-lg;
  max-width: 500rpx;
}

.error-action {
  padding: $spacing-sm $spacing-lg;
  background: $bg-card;
  border-radius: $radius-lg;
  border: 2rpx solid $primary;

  text {
    font-size: $font-base;
    font-weight: $font-medium;
    color: $primary;
  }

  &:active {
    background: rgba($primary, 0.1);
  }
}
</style>
