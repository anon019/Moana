<template>
  <view class="page-container">
    <NavBar title="我的收藏" :show-back="true" />

    <scroll-view
      class="content-scroll"
      scroll-y
      @scrolltolower="loadMore"
    >
      <!-- 加载状态 -->
      <LoadingState
        v-if="favoriteStore.loading && favoriteStore.favorites.length === 0"
        text="加载中..."
        icon="🌊"
      />

      <!-- 空状态 -->
      <EmptyState
        v-else-if="favoriteStore.favorites.length === 0"
        icon="❤️"
        title="还没有收藏"
        description="浏览内容时点击爱心收藏喜欢的内容"
        action-text="去发现"
        @action="goToLibrary"
      />

      <!-- 收藏列表 -->
      <view v-else class="favorite-list">
        <ContentCard
          v-for="item in favoriteStore.favorites"
          :key="item.id"
          :title="item.content_title"
          :type="item.content_type"
          :cover-url="item.cover_url"
          :created-at="item.created_at"
          :show-play="true"
          @tap="goToDetail(item)"
          @play="goToPlay(item)"
        />
      </view>

      <!-- 加载更多 -->
      <view v-if="favoriteStore.loading && favoriteStore.favorites.length > 0" class="loading-more">
        <text>加载更多...</text>
      </view>

      <view v-if="!favoriteStore.hasMore && favoriteStore.favorites.length > 0" class="no-more">
        <text>没有更多了</text>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { useFavoriteStore } from '@/stores/favorite'
import { useContentStore } from '@/stores/content'
import NavBar from '@/components/NavBar/NavBar.vue'
import ContentCard from '@/components/ContentCard/ContentCard.vue'
import LoadingState from '@/components/LoadingState/LoadingState.vue'
import EmptyState from '@/components/EmptyState/EmptyState.vue'
import type { FavoriteItem } from '@/api/favorite'

const favoriteStore = useFavoriteStore()
const contentStore = useContentStore()

function goToLibrary() {
  uni.switchTab({ url: '/pages/library/index' })
}

function warmContentDetail(contentId?: string) {
  if (!contentId) return

  void contentStore.fetchContentDetail(contentId).catch(() => {
    /* silent */
  })
}

function goToDetail(item: FavoriteItem) {
  warmContentDetail(item.content_id)
  if (item.content_type === 'nursery_rhyme') {
    uni.navigateTo({ url: `/pages/play/nursery-rhyme?id=${item.content_id}` })
  } else if (item.content_type === 'video') {
    uni.navigateTo({ url: `/pages/play/video?id=${item.content_id}` })
  } else {
    uni.navigateTo({ url: `/pages/play/picture-book?id=${item.content_id}` })
  }
}

function goToPlay(item: FavoriteItem) {
  warmContentDetail(item.content_id)
  if (item.content_type === 'nursery_rhyme') {
    uni.navigateTo({ url: `/pages/play/nursery-rhyme?id=${item.content_id}&autoplay=1` })
  } else if (item.content_type === 'video') {
    uni.navigateTo({ url: `/pages/play/video?id=${item.content_id}` })
  } else {
    uni.navigateTo({ url: `/pages/play/picture-book?id=${item.content_id}&autoplay=1` })
  }
}

function loadMore() {
  favoriteStore.fetchFavorites()
}

onShow(() => {
  void favoriteStore.ensureFavoritesLoaded()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.page-container {
  min-height: 100vh;
  background: $gradient-warm;
  width: 750rpx;
  box-sizing: border-box;
  overflow-x: hidden;
}

.content-scroll {
  padding: $spacing-md;
  width: 750rpx;
  box-sizing: border-box;
}

.favorite-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.loading-more,
.no-more {
  text-align: center;
  padding: $spacing-md;

  text {
    font-size: $font-sm;
    color: $text-light;
  }
}

.safe-bottom {
  height: 100rpx;
}
</style>
