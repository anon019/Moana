<template>
  <view class="empty-state">
    <text class="empty-icon">{{ icon }}</text>
    <text class="empty-title">{{ title }}</text>
    <text v-if="description" class="empty-desc">{{ description }}</text>
    <view v-if="actionText" class="empty-action" @tap="$emit('action')">
      <text>{{ actionText }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  title: string
  description?: string
  actionText?: string
}>(), {
  icon: '📭'
})

defineEmits<{
  action: []
}>()
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx $spacing-lg;
  text-align: center;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: $spacing-md;
}

.empty-title {
  font-size: $font-lg;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.empty-desc {
  font-size: $font-base;
  color: $text-secondary;
  margin-bottom: $spacing-lg;
}

.empty-action {
  padding: $spacing-sm $spacing-lg;
  background: $gradient-primary;
  border-radius: $radius-lg;
  box-shadow: $shadow-button;

  text {
    font-size: $font-base;
    font-weight: $font-semibold;
    color: $text-white;
  }

  &:active {
    transform: scale(0.95);
  }
}
</style>
