<template>
  <view
    class="favorite-button"
    :class="{ active: isFavorite, loading: isLoading }"
    @tap.stop="handleTap"
  >
    <text class="favorite-icon">{{ isFavorite ? '❤️' : '🤍' }}</text>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFavoriteStore } from '@/stores/favorite'

const props = defineProps<{
  contentId: string
}>()

const emit = defineEmits<{
  change: [isFavorite: boolean]
}>()

const favoriteStore = useFavoriteStore()
const isLoading = ref(false)

const isFavorite = computed(() => favoriteStore.isFavorite(props.contentId))

async function handleTap() {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const newState = await favoriteStore.toggleFavorite(props.contentId)
    emit('change', newState)
    uni.showToast({
      title: newState ? '已收藏' : '已取消收藏',
      icon: 'none'
    })
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  favoriteStore.checkContentFavorite(props.contentId)
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.favorite-button {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: $shadow-sm;
  transition: transform $duration-fast;

  &:active {
    transform: scale(0.9);
  }

  &.loading {
    opacity: 0.5;
    pointer-events: none;
  }

  &.active {
    .favorite-icon {
      animation: heartBeat 0.3s ease-out;
    }
  }
}

.favorite-icon {
  font-size: 32rpx;
}

@keyframes heartBeat {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}
</style>
