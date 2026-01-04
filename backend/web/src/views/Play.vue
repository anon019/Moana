<template>
  <div class="play-page h-screen">
    <!-- 加载状态 -->
    <div v-if="loading" class="h-full flex items-center justify-center bg-gray-900">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p class="mt-4 text-white/60">加载中...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="h-full flex items-center justify-center bg-gray-900">
      <div class="text-center">
        <div class="text-6xl mb-4">😵</div>
        <p class="text-white/80 mb-4">{{ error }}</p>
        <button @click="goBack" class="btn btn-primary">返回</button>
      </div>
    </div>

    <!-- 绘本播放器 -->
    <PlayerPictureBook
      v-else-if="pictureBook"
      :title="pictureBook.title"
      :pages="pictureBook.pages"
      @back="goBack"
    />

    <!-- 儿歌播放器 -->
    <PlayerNurseryRhyme
      v-else-if="nurseryRhyme"
      :title="nurseryRhyme.title"
      :audio-url="nurseryRhyme.audio_url"
      :cover-url="nurseryRhyme.cover_url || nurseryRhyme.suno_cover_url"
      :lyrics="nurseryRhyme.lyrics"
      @back="goBack"
    />

    <!-- 视频播放器 -->
    <PlayerVideo
      v-else-if="video"
      :title="video.title"
      :video-url="video.video_url"
      :cover-url="video.cover_url"
      @back="goBack"
    />

    <!-- 未知类型 -->
    <div v-else class="h-full flex items-center justify-center bg-gray-900">
      <div class="text-center">
        <div class="text-6xl mb-4">🤔</div>
        <p class="text-white/80 mb-4">未知的内容类型</p>
        <button @click="goBack" class="btn btn-primary">返回</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContentDetail } from '@/api/content'
import type { PictureBook, NurseryRhyme, Video } from '@/api/types'
import PlayerPictureBook from '@/components/PlayerPictureBook.vue'
import PlayerNurseryRhyme from '@/components/PlayerNurseryRhyme.vue'
import PlayerVideo from '@/components/PlayerVideo.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const content = ref<PictureBook | NurseryRhyme | Video | null>(null)

// 从路由参数获取类型
const contentType = computed(() => route.params.type as string)
const contentId = computed(() => route.params.id as string)

// 使用 content_type 字段判断类型（更可靠）
const actualType = computed(() => {
  const c = content.value as any
  return c?.content_type || null
})

// 类型断言
const pictureBook = computed(() => {
  if (actualType.value === 'picture_book') {
    return content.value as PictureBook
  }
  return null
})

const nurseryRhyme = computed(() => {
  if (actualType.value === 'nursery_rhyme') {
    return content.value as NurseryRhyme
  }
  return null
})

const video = computed(() => {
  if (actualType.value === 'video') {
    return content.value as Video
  }
  return null
})

// 返回上一页
function goBack() {
  // 如果有历史记录，返回上一页；否则去内容库
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/library')
  }
}

// 获取内容详情
async function fetchContent() {
  if (!contentId.value) {
    error.value = '缺少内容ID'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = ''
    content.value = await getContentDetail(contentId.value)

    // 验证内容类型是否匹配
    const actualType = pictureBook.value
      ? 'picture-book'
      : nurseryRhyme.value
        ? 'nursery-rhyme'
        : 'video'

    if (actualType !== contentType.value) {
      console.warn(`内容类型不匹配: 路由=${contentType.value}, 实际=${actualType}`)
      // 不报错，使用实际类型
    }
  } catch (e: any) {
    console.error('获取内容详情失败:', e)
    error.value = e?.response?.data?.detail || '获取内容失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchContent()
})
</script>

<style scoped>
.play-page {
  /* 全屏沉浸式 */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 50;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #0ea5e9;
  color: white;
}

.btn-primary:hover {
  background-color: #0284c7;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
