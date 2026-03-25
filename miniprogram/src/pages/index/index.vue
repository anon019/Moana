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

    <!-- 主内容区 -->
    <scroll-view class="main-scroll" scroll-y enhanced :show-scrollbar="false">
      <!-- 英雄区域 - 全新设计 -->
      <view class="hero-section">
        <!-- 顶部装饰条 -->
        <view class="hero-top-decor">
          <view class="sparkle s1">✦</view>
          <view class="sparkle s2">✧</view>
          <view class="sparkle s3">✦</view>
        </view>

        <!-- 用户信息卡片 -->
        <view class="user-card" @tap="goToProfile">
          <view class="user-card-glow"></view>
          <view class="avatar-container">
            <view class="avatar-ring">
              <view class="ring-segment seg-1"></view>
              <view class="ring-segment seg-2"></view>
              <view class="ring-segment seg-3"></view>
            </view>
            <view class="avatar-inner">
              <image
                v-if="childStore.currentChild?.avatar_url"
                :src="childStore.currentChild.avatar_url"
                class="avatar-img"
                mode="aspectFill"
              />
              <view v-else class="avatar-placeholder">
                <text>{{ childName.slice(0, 1) }}</text>
              </view>
            </view>
            <view class="avatar-status">
              <text>👋</text>
            </view>
          </view>
          <view class="user-info">
            <view class="greeting-row">
              <text class="greeting-emoji">{{ greetingEmoji }}</text>
              <text class="greeting-text">{{ greetingText }}</text>
            </view>
            <text class="child-name">{{ childName }}</text>
          </view>
          <view class="user-arrow">
            <text>›</text>
          </view>
        </view>

      </view>

      <!-- 创作魔法入口 - 全新沉浸式设计 -->
      <view class="magic-section">
        <view class="section-header">
          <view class="section-icon-wrap">
            <text class="section-icon">✨</text>
          </view>
          <view class="section-title-wrap">
            <text class="section-title">开启创作魔法</text>
            <text class="section-subtitle">为 {{ childName }} 量身定制</text>
          </view>
        </view>

        <!-- 大型沉浸式创作卡片 -->
        <view class="creation-showcase">
          <!-- 绘本卡片 - 主推 -->
          <view class="showcase-card card-book" @tap="goToCreateBook">
            <view class="showcase-bg">
              <view class="bg-pattern"></view>
              <view class="bg-gradient"></view>
            </view>
            <view class="showcase-content">
              <view class="showcase-badge">
                <text class="badge-star">★</text>
                <text class="badge-text">推荐</text>
              </view>
              <view class="showcase-icon-area">
                <view class="icon-float-ring r1"></view>
                <view class="icon-float-ring r2"></view>
                <view class="icon-float-ring r3"></view>
                <view class="showcase-icon">
                  <text>📚</text>
                </view>
              </view>
              <view class="showcase-info">
                <text class="showcase-title">AI 绘本</text>
                <text class="showcase-desc">个性化故事 · 独特插画</text>
                <view class="showcase-features">
                  <view class="feature-tag">
                    <text>🎨 多种画风</text>
                  </view>
                  <view class="feature-tag">
                    <text>👶 宝贝主角</text>
                  </view>
                </view>
              </view>
              <view class="showcase-action">
                <view class="action-btn">
                  <text class="action-text">开始创作</text>
                  <text class="action-arrow">→</text>
                </view>
              </view>
            </view>
            <view class="showcase-decor">
              <view class="decor-star ds1">✦</view>
              <view class="decor-star ds2">✧</view>
              <view class="decor-star ds3">⋆</view>
            </view>
          </view>

          <!-- 次要卡片区 -->
          <view class="secondary-cards">
            <!-- 儿歌卡片 -->
            <view class="secondary-card card-song" @tap="goToCreateSong">
              <view class="sec-bg"></view>
              <view class="sec-content">
                <view class="sec-icon-wrap">
                  <text class="sec-icon">🎵</text>
                  <view class="music-wave">
                    <view class="wave-bar b1"></view>
                    <view class="wave-bar b2"></view>
                    <view class="wave-bar b3"></view>
                  </view>
                </view>
                <view class="sec-info">
                  <text class="sec-title">AI 儿歌</text>
                  <text class="sec-desc">原创旋律</text>
                </view>
                <view class="sec-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>

            <!-- 视频卡片 -->
            <view class="secondary-card card-video" @tap="goToCreateVideo">
              <view class="sec-bg"></view>
              <view class="sec-content">
                <view class="sec-icon-wrap">
                  <text class="sec-icon">🎬</text>
                  <view class="play-btn-mini">
                    <text>▶</text>
                  </view>
                </view>
                <view class="sec-info">
                  <text class="sec-title">AI 视频</text>
                  <text class="sec-desc">绘本动画</text>
                </view>
                <view class="sec-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 继续探索区 -->
      <view v-if="recentPlays.length > 0" class="continue-section">
        <view class="section-header-simple">
          <text class="section-title-simple">继续探索</text>
          <text class="section-more" @tap="goToLibrary">查看全部 →</text>
        </view>

        <scroll-view class="continue-scroll" scroll-x enable-flex :show-scrollbar="false">
          <view class="continue-list">
            <view
              v-for="item in recentPlays"
              :key="item.id"
              class="continue-card"
              :class="'continue-' + item.content_type"
              @tap="goToPlay(item)"
            >
              <view class="continue-cover">
                <image v-if="item.cover_url" :src="item.cover_url" mode="aspectFill" class="cover-img" />
                <view v-else class="cover-placeholder">
                  <text>{{ getTypeIcon(item.content_type) }}</text>
                </view>
                <!-- 进度环 -->
                <view class="progress-ring">
                  <view class="ring-bg"></view>
                  <view class="ring-progress" :style="{ '--progress': getPlayProgress(item) }"></view>
                  <view class="ring-center">
                    <text>{{ Math.round(getPlayProgress(item) * 100) }}%</text>
                  </view>
                </view>
              </view>
              <view class="continue-info">
                <text class="continue-title">{{ getPlayTitle(item) }}</text>
                <view class="continue-type" :class="'type-' + item.content_type">
                  <text>{{ getTypeLabel(item.content_type) }}</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 今日灵感区 - 按类型分组推荐 -->
      <view class="inspiration-section">
        <view class="section-header-simple">
          <text class="section-title-simple">今日灵感</text>
          <view class="refresh-hint">
            <text class="refresh-icon">🌟</text>
            <text class="refresh-text">每日更新</text>
          </view>
        </view>

        <!-- 按类型分组显示 -->
        <view class="inspiration-groups">
          <!-- 绘本推荐 -->
          <view class="inspiration-group group-book">
            <view class="group-header">
              <view class="group-icon-wrap">
                <text class="group-icon">📚</text>
              </view>
              <text class="group-title">绘本推荐</text>
            </view>
            <view class="group-cards">
              <view
                v-for="item in bookRecommendations"
                :key="item.id"
                class="inspire-card card-book"
                @tap="handleRecommend(item)"
              >
                <view class="card-icon-wrap">
                  <text class="card-icon">{{ item.icon }}</text>
                </view>
                <view class="card-info">
                  <text class="card-title">{{ item.title }}</text>
                  <text class="card-desc">{{ item.desc }}</text>
                </view>
                <view class="card-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>
          </view>

          <!-- 儿歌推荐 -->
          <view class="inspiration-group group-song">
            <view class="group-header">
              <view class="group-icon-wrap">
                <text class="group-icon">🎵</text>
              </view>
              <text class="group-title">儿歌推荐</text>
            </view>
            <view class="group-cards">
              <view
                v-for="item in songRecommendations"
                :key="item.id"
                class="inspire-card card-song"
                @tap="handleRecommend(item)"
              >
                <view class="card-icon-wrap">
                  <text class="card-icon">{{ item.icon }}</text>
                </view>
                <view class="card-info">
                  <text class="card-title">{{ item.title }}</text>
                  <text class="card-desc">{{ item.desc }}</text>
                </view>
                <view class="card-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>
          </view>

          <!-- 视频推荐 -->
          <view class="inspiration-group group-video">
            <view class="group-header">
              <view class="group-icon-wrap">
                <text class="group-icon">🎬</text>
              </view>
              <text class="group-title">视频推荐</text>
            </view>
            <view class="group-cards">
              <view
                v-for="item in videoRecommendations"
                :key="item.id"
                class="inspire-card card-video"
                @tap="handleRecommend(item)"
              >
                <view class="card-icon-wrap">
                  <text class="card-icon">{{ item.icon }}</text>
                </view>
                <view class="card-info">
                  <text class="card-title">{{ item.title }}</text>
                  <text class="card-desc">{{ item.desc }}</text>
                </view>
                <view class="card-arrow">
                  <text>→</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 快捷工具区 -->
      <view class="tools-section">
        <view class="tools-container">
          <view class="tool-item" @tap="goToChildMode">
            <view class="tool-icon-wrap tool-child">
              <view class="tool-icon-bg"></view>
              <text class="tool-icon">👶</text>
            </view>
            <text class="tool-label">儿童模式</text>
          </view>
          <view class="tool-item" @tap="goToFavorites">
            <view class="tool-icon-wrap tool-favorites">
              <view class="tool-icon-bg"></view>
              <text class="tool-icon">❤️</text>
            </view>
            <text class="tool-label">我的收藏</text>
          </view>
        </view>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </scroll-view>

    <!-- 新用户引导 -->
    <view v-if="showAddChildGuide" class="guide-overlay" @tap.self="() => {}">
      <view class="guide-modal">
        <view class="guide-bg">
          <view class="guide-orb o1"></view>
          <view class="guide-orb o2"></view>
          <view class="guide-orb o3"></view>
        </view>
        <view class="guide-content">
          <view class="guide-avatar-wrap">
            <view class="guide-avatar-ring"></view>
            <view class="guide-avatar">
              <text>👶</text>
            </view>
          </view>
          <text class="guide-title">欢迎来到 Moana</text>
          <text class="guide-subtitle">开启童话创作之旅</text>
          <text class="guide-desc">添加宝贝信息，为 Ta 量身定制早教内容</text>
          <view class="guide-btn" @tap="goToAddChild">
            <view class="guide-btn-shine"></view>
            <view class="guide-btn-content">
              <text class="btn-sparkle">✨</text>
              <text class="btn-text">添加宝贝</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { useChildStore } from '@/stores/child'
import { useContentStore } from '@/stores/content'
import type { PlayHistoryItem } from '@/api/play'
import { getPlayHistory } from '@/api/play'

const userStore = useUserStore()
const childStore = useChildStore()
const contentStore = useContentStore()

// 状态
const recentPlays = ref<PlayHistoryItem[]>([])
const showAddChildGuide = ref(false)
let loadDataTask: Promise<void> | null = null

function getPlayProgress(item: PlayHistoryItem): number {
  const raw = item.progress ?? item.completion_rate ?? 0
  return Math.max(0, Math.min(1, Number(raw) || 0))
}

function getPlayTitle(item: PlayHistoryItem): string {
  return item.content_title || '继续播放'
}

// 计算属性
const childName = computed(() => childStore.currentChild?.name || '宝贝')

const greetingEmoji = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '🌙'
  if (hour < 9) return '🌅'
  if (hour < 12) return '☀️'
  if (hour < 14) return '🌞'
  if (hour < 18) return '🌤️'
  if (hour < 22) return '🌆'
  return '🌙'
})

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

// 灵感推荐池 - 使用 API 返回的主题 ID
const inspirationPool = {
  book: [
    { id: 'brush_teeth', icon: '🦷', title: '刷牙好习惯', desc: '培养口腔护理习惯' },
    { id: 'no_picky_eating', icon: '🥦', title: '不挑食', desc: '健康饮食启蒙' },
    { id: 'bedtime', icon: '🛏️', title: '按时睡觉', desc: '培养作息规律' },
    { id: 'wash_hands', icon: '🧼', title: '洗手讲卫生', desc: '养成卫生习惯' },
    { id: 'tidy_up', icon: '🧹', title: '收拾玩具', desc: '学会自己整理' },
    { id: 'greeting', icon: '👋', title: '打招呼', desc: '礼貌小达人' },
    { id: 'colors', icon: '🎨', title: '认识颜色', desc: '色彩启蒙之旅' },
    { id: 'animals', icon: '🦁', title: '认识动物', desc: '动物王国探险' },
    { id: 'numbers', icon: '🔢', title: '认识数字', desc: '数学启蒙乐园' },
    { id: 'weather', icon: '🌤️', title: '认识天气', desc: '感受自然奥秘' },
    { id: 'sharing', icon: '🤝', title: '学会分享', desc: '分享的快乐' },
    { id: 'family', icon: '👨‍👩‍👧', title: '认识家人', desc: '温暖的家庭' }
  ],
  song: [
    { id: 'brush_teeth', icon: '🦷', title: '刷牙歌', desc: '唱着歌儿刷刷牙' },
    { id: 'no_picky_eating', icon: '🥦', title: '不挑食歌', desc: '吃蔬菜身体棒' },
    { id: 'nap_time', icon: '😴', title: '午睡歌', desc: '温柔旋律助眠' },
    { id: 'wash_hands', icon: '🧼', title: '洗手歌', desc: '七步洗手法' },
    { id: 'colors', icon: '🌈', title: '颜色歌', desc: '唱出七彩世界' },
    { id: 'animals', icon: '🐼', title: '动物歌', desc: '动物叫声大合唱' },
    { id: 'numbers', icon: '🔢', title: '数字歌', desc: '数学启蒙儿歌' },
    { id: 'happy', icon: '😄', title: '开心歌', desc: '快乐每一天' },
    { id: 'vehicles', icon: '🚌', title: '交通工具歌', desc: '车车火车飞机' },
    { id: 'greeting', icon: '👋', title: '打招呼歌', desc: '你好、再见' }
  ],
  video: [
    { id: 'brush_teeth', icon: '🦷', title: '刷牙动画', desc: '绘本变动画' },
    { id: 'animals', icon: '🦁', title: '动物世界', desc: '动态故事体验' },
    { id: 'colors', icon: '🎨', title: '色彩之旅', desc: '绘本动画版' },
    { id: 'bedtime', icon: '🌙', title: '晚安故事', desc: '睡前动画' },
    { id: 'family', icon: '👨‍👩‍👧', title: '家庭时光', desc: '温馨小剧场' },
    { id: 'sharing', icon: '🤝', title: '分享乐趣', desc: '动画绘本' }
  ]
}

// 基于日期的伪随机数生成器
function getDailySeededRandom(seed: number): () => number {
  return () => {
    seed = (seed * 9301 + 49297) % 233280
    return seed / 233280
  }
}

// 基于日期的洗牌函数
function getDailyShuffledArray<T>(arr: T[], dateSeed: number): T[] {
  const random = getDailySeededRandom(dateSeed)
  const shuffled = [...arr]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

// 获取今日日期种子
function getTodayDateSeed(): number {
  const now = new Date()
  const hkOffset = 8 * 60
  const hkTime = new Date(now.getTime() + hkOffset * 60 * 1000)
  return hkTime.getFullYear() * 10000 + (hkTime.getMonth() + 1) * 100 + hkTime.getDate()
}

// 绘本推荐 - 每日随机2个
const bookRecommendations = computed(() => {
  const dateSeed = getTodayDateSeed()
  return getDailyShuffledArray(inspirationPool.book, dateSeed)
    .slice(0, 2)
    .map(item => ({
      id: `book_${item.id}`,
      type: 'book' as const,
      icon: item.icon,
      title: item.title,
      desc: item.desc,
      theme: item.id
    }))
})

// 儿歌推荐 - 每日随机2个
const songRecommendations = computed(() => {
  const dateSeed = getTodayDateSeed() + 1000 // 不同偏移量保证与绘本不同
  return getDailyShuffledArray(inspirationPool.song, dateSeed)
    .slice(0, 2)
    .map(item => ({
      id: `song_${item.id}`,
      type: 'song' as const,
      icon: item.icon,
      title: item.title,
      desc: item.desc,
      theme: item.id
    }))
})

// 视频推荐 - 每日随机2个
const videoRecommendations = computed(() => {
  const dateSeed = getTodayDateSeed() + 2000 // 不同偏移量保证与其他类型不同
  return getDailyShuffledArray(inspirationPool.video, dateSeed)
    .slice(0, 2)
    .map(item => ({
      id: `video_${item.id}`,
      type: 'video' as const,
      icon: item.icon,
      title: item.title,
      desc: item.desc,
      theme: item.id
    }))
})

// 辅助方法
function getTypeIcon(type: string) {
  const icons: Record<string, string> = {
    picture_book: '📚',
    nursery_rhyme: '🎵',
    video: '🎬'
  }
  return icons[type] || '📚'
}

function getTypeLabel(type: string) {
  const labels: Record<string, string> = {
    picture_book: '绘本',
    nursery_rhyme: '儿歌',
    video: '视频'
  }
  return labels[type] || '绘本'
}

// 导航方法
function goToProfile() {
  uni.switchTab({ url: '/pages/profile/index' })
}

function goToCreateBook() {
  uni.navigateTo({ url: '/pages/create/picture-book' })
}

function goToCreateSong() {
  uni.navigateTo({ url: '/pages/create/nursery-rhyme' })
}

function goToCreateVideo() {
  uni.navigateTo({ url: '/pages/create/video' })
}

function goToLibrary() {
  uni.switchTab({ url: '/pages/library/index' })
}

function goToAddChild() {
  showAddChildGuide.value = false
  uni.navigateTo({ url: '/pages/profile/add-child' })
}

function warmContentDetail(contentId?: string) {
  if (!contentId) return

  void contentStore.fetchContentDetail(contentId).catch(() => {
    /* silent */
  })
}

function goToPlay(item: PlayHistoryItem) {
  warmContentDetail(item.content_id)
  const contentType = item.content_type
  if (contentType === 'nursery_rhyme') {
    uni.navigateTo({ url: `/pages/play/nursery-rhyme?id=${item.content_id}` })
  } else if (contentType === 'video') {
    uni.navigateTo({ url: `/pages/play/video?id=${item.content_id}` })
  } else {
    uni.navigateTo({ url: `/pages/play/picture-book?id=${item.content_id}` })
  }
}

function handleRecommend(item: any) {
  console.log('[首页灵感] 点击推荐:', item.type, item.title, '主题ID:', item.theme)
  if (item.type === 'book') {
    uni.navigateTo({ url: `/pages/create/picture-book?theme=${item.theme}` })
  } else if (item.type === 'song') {
    uni.navigateTo({ url: `/pages/create/nursery-rhyme?theme=${item.theme}` })
  } else if (item.type === 'video') {
    uni.navigateTo({ url: '/pages/create/video' })
  }
}

function goToChildMode() {
  uni.navigateTo({ url: '/pages/child/index' })
}

function goToFavorites() {
  uni.navigateTo({ url: '/pages/favorites/index' })
}

// 加载数据
async function loadData() {
  if (loadDataTask) {
    return loadDataTask
  }

  loadDataTask = (async () => {
    try {
      if (!userStore.checkLogin()) {
        await userStore.login()
      }

      await childStore.fetchChildren()

      if (!childStore.hasChild) {
        showAddChildGuide.value = true
        recentPlays.value = []
        return
      }

      showAddChildGuide.value = false

      if (childStore.currentChild) {
        try {
          const historyRes = await getPlayHistory(childStore.currentChild.id, { limit: 5 })
          recentPlays.value = historyRes.items.filter(item => getPlayProgress(item) < 1)
        } catch (e) {
          console.log('加载数据失败:', e)
        }
      } else {
        recentPlays.value = []
      }
    } catch (e) {
      console.log('首页加载失败:', e)
      recentPlays.value = []
    }
  })().finally(() => {
    loadDataTask = null
  })

  return loadDataTask
}

onShow(() => {
  void loadData()
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
// 梦幻背景层
// ============================================
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
  opacity: 0.4;

  &.aurora-1 {
    width: 500rpx;
    height: 500rpx;
    background: linear-gradient(135deg, $book-light 0%, rgba($book-primary, 0.3) 100%);
    top: -150rpx;
    right: -100rpx;
    animation: auroraFloat 8s ease-in-out infinite;
  }

  &.aurora-2 {
    width: 400rpx;
    height: 400rpx;
    background: linear-gradient(135deg, $song-light 0%, rgba($song-primary, 0.3) 100%);
    top: 40%;
    left: -120rpx;
    animation: auroraFloat 10s ease-in-out infinite 2s;
  }

  &.aurora-3 {
    width: 350rpx;
    height: 350rpx;
    background: linear-gradient(135deg, $video-light 0%, rgba($video-primary, 0.3) 100%);
    bottom: 5%;
    right: -80rpx;
    animation: auroraFloat 12s ease-in-out infinite 4s;
  }
}

@keyframes auroraFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20rpx, -30rpx) scale(1.05); }
  66% { transform: translate(-15rpx, 20rpx) scale(0.95); }
}

.floating-orb {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8), rgba(255,255,255,0));
  opacity: 0.6;

  &.orb-1 {
    width: 80rpx;
    height: 80rpx;
    top: 20%;
    right: 15%;
    animation: orbFloat 6s ease-in-out infinite;
  }

  &.orb-2 {
    width: 50rpx;
    height: 50rpx;
    top: 50%;
    left: 10%;
    animation: orbFloat 8s ease-in-out infinite 1s;
  }

  &.orb-3 {
    width: 60rpx;
    height: 60rpx;
    bottom: 25%;
    right: 20%;
    animation: orbFloat 7s ease-in-out infinite 2s;
  }
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-30rpx); }
}

// ============================================
// 主滚动区
// ============================================
.main-scroll {
  position: relative;
  z-index: 1;
  height: 100vh;
  padding: 0 $spacing-lg;
  box-sizing: border-box;
  width: 750rpx;
}

// ============================================
// 英雄区域
// ============================================
.hero-section {
  padding-top: calc(env(safe-area-inset-top) + 60rpx);
  padding-bottom: $spacing-lg;
}

.hero-top-decor {
  position: relative;
  height: 40rpx;
  margin-bottom: $spacing-md;
}

.sparkle {
  position: absolute;
  font-size: 20rpx;
  color: $accent;
  animation: sparkleAnim 2s ease-in-out infinite;

  &.s1 { left: 20%; animation-delay: 0s; }
  &.s2 { left: 50%; animation-delay: 0.5s; }
  &.s3 { left: 80%; animation-delay: 1s; }
}

@keyframes sparkleAnim {
  0%, 100% { opacity: 0.3; transform: scale(1) rotate(0deg); }
  50% { opacity: 1; transform: scale(1.2) rotate(180deg); }
}

// 用户卡片
.user-card {
  position: relative;
  display: flex;
  align-items: center;
  padding: $spacing-md $spacing-lg;
  background: rgba(255, 255, 255, 0.9);
  border-radius: $radius-2xl;
  box-shadow: $shadow-lg;
  margin-bottom: $spacing-lg;
  overflow: hidden;
  border: 1rpx solid rgba(255, 255, 255, 0.8);

  &:active {
    transform: scale(0.98);
  }
}

.user-card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba($primary, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.avatar-container {
  position: relative;
  width: 120rpx;
  height: 120rpx;
  flex-shrink: 0;
}

.avatar-ring {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  overflow: hidden;
}

.ring-segment {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  border: 4rpx solid transparent;

  &.seg-1 {
    border-top-color: $book-primary;
    border-right-color: $book-primary;
    animation: ringRotate 3s linear infinite;
  }

  &.seg-2 {
    border-bottom-color: $song-primary;
    animation: ringRotate 3s linear infinite reverse;
    animation-delay: 0.5s;
  }

  &.seg-3 {
    border-left-color: $video-primary;
    animation: ringRotate 4s linear infinite;
    animation-delay: 1s;
  }
}

@keyframes ringRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.avatar-inner {
  position: absolute;
  top: 8rpx;
  left: 8rpx;
  right: 8rpx;
  bottom: 8rpx;
  border-radius: 50%;
  overflow: hidden;
  background: $gradient-dreamy;
  box-shadow: $shadow-md;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $gradient-primary;

  text {
    font-size: 48rpx;
    color: #fff;
    font-weight: 700;
  }
}

.avatar-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 40rpx;
  height: 40rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-sm;
  border: 3rpx solid #fff;

  text {
    font-size: 22rpx;
  }
}

.user-info {
  flex: 1;
  margin-left: $spacing-md;
}

.greeting-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 4rpx;
}

.greeting-emoji {
  font-size: 24rpx;
}

.greeting-text {
  font-size: $font-sm;
  color: $text-tertiary;
}

.child-name {
  display: block;
  font-size: $font-hero;
  font-weight: 800;
  color: $text-primary;
  line-height: 1.2;
}

.user-arrow {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  text {
    font-size: 40rpx;
    color: $text-tertiary;
    font-weight: 300;
  }
}

// ============================================
// 创作魔法区
// ============================================
.magic-section {
  margin-bottom: $spacing-xl;
}

.section-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.section-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $gradient-dreamy;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;

  .section-icon {
    font-size: 28rpx;
  }
}

.section-title-wrap {
  flex: 1;
}

.section-title {
  display: block;
  font-size: $font-lg;
  font-weight: 700;
  color: $text-primary;
}

.section-subtitle {
  display: block;
  font-size: $font-sm;
  color: $text-tertiary;
  margin-top: 2rpx;
}

// 创作展示区
.creation-showcase {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

// 主推卡片
.showcase-card {
  position: relative;
  border-radius: $radius-2xl;
  overflow: hidden;
  box-shadow: $shadow-lg;

  &:active {
    transform: scale(0.98);
  }

  &.card-book {
    background: linear-gradient(145deg, #FFF8F5 0%, $book-light 100%);
    border: 1rpx solid rgba($book-primary, 0.1);

    .showcase-badge { background: $book-primary; }
    .icon-float-ring { border-color: rgba($book-primary, 0.2); }
    .action-btn { background: $book-gradient; box-shadow: $shadow-colored-book; }
    .decor-star { color: $book-primary; }
  }
}

.showcase-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.bg-pattern {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background: radial-gradient(circle at 80% 20%, rgba($book-primary, 0.08) 0%, transparent 50%);
}

.bg-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(to top, rgba(255,255,255,0.5), transparent);
}

.showcase-content {
  position: relative;
  z-index: 1;
  padding: $spacing-lg;
}

.showcase-badge {
  position: absolute;
  top: $spacing-md;
  right: $spacing-md;
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 8rpx 16rpx;
  border-radius: $radius-full;

  .badge-star {
    font-size: 18rpx;
    color: #fff;
  }

  .badge-text {
    font-size: 22rpx;
    color: #fff;
    font-weight: 600;
  }
}

.showcase-icon-area {
  position: relative;
  width: 120rpx;
  height: 120rpx;
  margin-bottom: $spacing-md;
}

.icon-float-ring {
  position: absolute;
  border-radius: 50%;
  border: 2rpx solid;

  &.r1 {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    animation: floatRing 3s ease-in-out infinite;
  }

  &.r2 {
    top: -10rpx;
    left: -10rpx;
    right: -10rpx;
    bottom: -10rpx;
    opacity: 0.5;
    animation: floatRing 3s ease-in-out infinite 0.5s;
  }

  &.r3 {
    top: -20rpx;
    left: -20rpx;
    right: -20rpx;
    bottom: -20rpx;
    opacity: 0.3;
    animation: floatRing 3s ease-in-out infinite 1s;
  }
}

@keyframes floatRing {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 0.3; }
}

.showcase-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  text {
    font-size: 64rpx;
  }
}

.showcase-info {
  margin-bottom: $spacing-lg;
}

.showcase-title {
  display: block;
  font-size: $font-xxl;
  font-weight: 800;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.showcase-desc {
  display: block;
  font-size: $font-base;
  color: $text-secondary;
  margin-bottom: $spacing-md;
}

.showcase-features {
  display: flex;
  gap: $spacing-sm;
}

.feature-tag {
  padding: 8rpx 16rpx;
  background: rgba(255, 255, 255, 0.8);
  border-radius: $radius-full;
  border: 1rpx solid rgba($book-primary, 0.15);

  text {
    font-size: $font-xs;
    color: $text-secondary;
  }
}

.showcase-action {
  display: flex;
  justify-content: flex-start;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 36rpx;
  border-radius: $radius-xl;

  .action-text {
    font-size: $font-md;
    font-weight: 600;
    color: #fff;
  }

  .action-arrow {
    font-size: $font-lg;
    color: #fff;
  }
}

.showcase-decor {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 120rpx;
  pointer-events: none;
}

.decor-star {
  position: absolute;
  font-size: 24rpx;
  opacity: 0.6;
  animation: starTwinkle 2s ease-in-out infinite;

  &.ds1 { top: 30%; right: 40rpx; animation-delay: 0s; }
  &.ds2 { top: 50%; right: 20rpx; animation-delay: 0.5s; }
  &.ds3 { top: 70%; right: 50rpx; animation-delay: 1s; }
}

@keyframes starTwinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.2); }
}

// 次要卡片
.secondary-cards {
  display: flex;
  gap: $spacing-md;
}

.secondary-card {
  flex: 1;
  position: relative;
  border-radius: $radius-xl;
  overflow: hidden;
  box-shadow: $shadow-card;

  &:active {
    transform: scale(0.96);
  }

  &.card-song {
    background: linear-gradient(145deg, #F8FFF8 0%, $song-light 100%);
    border: 1rpx solid rgba($song-primary, 0.1);

    .sec-arrow text { color: $song-primary; }
    .wave-bar { background: $song-primary; }
  }

  &.card-video {
    background: linear-gradient(145deg, #FFFDF5 0%, $video-light 100%);
    border: 1rpx solid rgba($video-primary, 0.1);

    .sec-arrow text { color: $video-primary; }
    .play-btn-mini { background: rgba($video-primary, 0.15); color: $video-primary; }
  }
}

.sec-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  opacity: 0.3;
}

.sec-content {
  position: relative;
  z-index: 1;
  padding: $spacing-md;
}

.sec-icon-wrap {
  position: relative;
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: $spacing-sm;
}

.sec-icon {
  font-size: 40rpx;
}

.music-wave {
  position: absolute;
  top: 8rpx;
  right: -16rpx;
  display: flex;
  gap: 4rpx;
  align-items: flex-end;
  height: 24rpx;
}

.wave-bar {
  width: 4rpx;
  border-radius: 2rpx;
  animation: waveAnim 0.8s ease-in-out infinite;

  &.b1 { height: 12rpx; animation-delay: 0s; }
  &.b2 { height: 20rpx; animation-delay: 0.2s; }
  &.b3 { height: 16rpx; animation-delay: 0.4s; }
}

@keyframes waveAnim {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.5); }
}

.play-btn-mini {
  position: absolute;
  top: 4rpx;
  right: -12rpx;
  width: 28rpx;
  height: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;

  text {
    font-size: 12rpx;
  }
}

.sec-info {
  margin-bottom: $spacing-sm;
}

.sec-title {
  display: block;
  font-size: $font-md;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 4rpx;
}

.sec-desc {
  display: block;
  font-size: $font-sm;
  color: $text-tertiary;
}

.sec-arrow {
  display: flex;
  justify-content: flex-end;

  text {
    font-size: 28rpx;
    font-weight: 600;
  }
}

// ============================================
// 继续探索区
// ============================================
.continue-section {
  margin-bottom: $spacing-xl;
}

.section-header-simple {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $spacing-md;
}

.section-title-simple {
  font-size: $font-lg;
  font-weight: 700;
  color: $text-primary;
}

.section-more {
  font-size: $font-sm;
  color: $primary;
  font-weight: 500;
}

.continue-scroll {
  margin: 0 -#{$spacing-lg};
  padding: 0 $spacing-lg;
}

.continue-list {
  display: flex;
  gap: $spacing-md;
  padding-right: $spacing-lg;
}

.continue-card {
  flex-shrink: 0;
  width: 200rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: $radius-xl;
  padding: $spacing-sm;
  box-shadow: $shadow-card;
  border: 1rpx solid rgba(255, 255, 255, 0.8);

  &:active {
    transform: scale(0.96);
  }
}

.continue-cover {
  position: relative;
  width: 100%;
  height: 160rpx;
  border-radius: $radius-lg;
  overflow: hidden;
  margin-bottom: $spacing-sm;
}

.cover-img {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-soft;

  text {
    font-size: 48rpx;
  }
}

.progress-ring {
  position: absolute;
  bottom: 8rpx;
  right: 8rpx;
  width: 48rpx;
  height: 48rpx;
}

.ring-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: $shadow-sm;
}

.ring-progress {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: conic-gradient(
    $primary calc(var(--progress, 0) * 360deg),
    transparent calc(var(--progress, 0) * 360deg)
  );
  mask: radial-gradient(circle, transparent 60%, black 60%);
  -webkit-mask: radial-gradient(circle, transparent 60%, black 60%);
}

.ring-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  text {
    font-size: 16rpx;
    font-weight: 600;
    color: $text-primary;
  }
}

.continue-info {
  padding: 0 4rpx;
}

.continue-title {
  display: block;
  font-size: $font-sm;
  font-weight: 600;
  color: $text-primary;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 8rpx;
}

.continue-type {
  display: inline-flex;
  padding: 4rpx 12rpx;
  border-radius: $radius-sm;
  background: $bg-soft;

  text {
    font-size: 20rpx;
    color: $text-tertiary;
  }

  &.type-picture_book {
    background: $book-light;
    text { color: $book-primary; }
  }

  &.type-nursery_rhyme {
    background: $song-light;
    text { color: $song-primary; }
  }

  &.type-video {
    background: $video-light;
    text { color: $video-primary; }
  }
}

// ============================================
// 今日灵感区 - 分组设计
// ============================================
.inspiration-section {
  margin-bottom: $spacing-xl;
}

.refresh-hint {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.refresh-icon {
  font-size: 20rpx;
  animation: starTwinkle 2s ease-in-out infinite;
}

.refresh-text {
  font-size: $font-xs;
  color: $text-tertiary;
}

.inspiration-groups {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.inspiration-group {
  background: rgba(255, 255, 255, 0.95);
  border-radius: $radius-xl;
  padding: $spacing-md;
  box-shadow: $shadow-card;
  border: 1rpx solid rgba(255, 255, 255, 0.8);

  &.group-book {
    border-left: 6rpx solid $book-primary;
    .group-icon-wrap { background: $book-light; }
    .group-title { color: $book-primary; }
  }

  &.group-song {
    border-left: 6rpx solid $song-primary;
    .group-icon-wrap { background: $song-light; }
    .group-title { color: $song-primary; }
  }

  &.group-video {
    border-left: 6rpx solid $video-primary;
    .group-icon-wrap { background: $video-light; }
    .group-title { color: $video-primary; }
  }
}

.group-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-sm;
}

.group-icon-wrap {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-md;
}

.group-icon {
  font-size: 26rpx;
}

.group-title {
  font-size: $font-md;
  font-weight: 600;
}

.group-cards {
  display: flex;
  gap: $spacing-sm;
}

.inspire-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-lg;
  transition: all $duration-base $ease-out;

  &:active {
    transform: scale(0.96);
  }

  &.card-book {
    background: linear-gradient(135deg, rgba($book-light, 0.5) 0%, rgba($book-light, 0.2) 100%);
    .card-arrow text { color: $book-primary; }
  }

  &.card-song {
    background: linear-gradient(135deg, rgba($song-light, 0.5) 0%, rgba($song-light, 0.2) 100%);
    .card-arrow text { color: $song-primary; }
  }

  &.card-video {
    background: linear-gradient(135deg, rgba($video-light, 0.5) 0%, rgba($video-light, 0.2) 100%);
    .card-arrow text { color: $video-primary; }
  }
}

.card-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  border-radius: $radius-md;
  flex-shrink: 0;
}

.card-icon {
  font-size: 28rpx;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-title {
  display: block;
  font-size: $font-base;
  font-weight: 600;
  color: $text-primary;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-desc {
  display: block;
  font-size: $font-xs;
  color: $text-tertiary;
  margin-top: 2rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-arrow {
  flex-shrink: 0;

  text {
    font-size: 24rpx;
    font-weight: 600;
  }
}

// ============================================
// 工具区
// ============================================
.tools-section {
  margin-bottom: $spacing-lg;
}

.tools-container {
  display: flex;
  justify-content: space-between;
  padding: $spacing-lg;
  background: rgba(255, 255, 255, 0.95);
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
  border: 1rpx solid rgba(255, 255, 255, 0.8);
}

.tool-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  flex: 1;

  &:active {
    transform: scale(0.9);
  }
}

.tool-icon-wrap {
  position: relative;
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-lg;
  overflow: hidden;

  &.tool-child .tool-icon-bg { background: $gradient-dreamy; }
  &.tool-favorites .tool-icon-bg { background: linear-gradient(135deg, $book-light 0%, #FFD6CC 100%); }
}

.tool-icon-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.tool-icon {
  position: relative;
  z-index: 1;
  font-size: 32rpx;
}

.tool-label {
  font-size: $font-xs;
  color: $text-secondary;
}

// ============================================
// 底部安全区
// ============================================
.safe-bottom {
  height: calc(env(safe-area-inset-bottom) + 120rpx);
}

// ============================================
// 引导弹窗
// ============================================
.guide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(61, 41, 20, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-xl;
}

.guide-modal {
  position: relative;
  width: 100%;
  max-width: 580rpx;
  background: #fff;
  border-radius: 48rpx;
  overflow: hidden;
  box-shadow: $shadow-xl;
}

.guide-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200rpx;
  overflow: hidden;
}

.guide-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(40rpx);

  &.o1 {
    width: 150rpx;
    height: 150rpx;
    background: $book-light;
    top: -40rpx;
    left: 20%;
  }

  &.o2 {
    width: 120rpx;
    height: 120rpx;
    background: $song-light;
    top: 20rpx;
    right: 15%;
  }

  &.o3 {
    width: 100rpx;
    height: 100rpx;
    background: $video-light;
    top: 80rpx;
    left: 50%;
  }
}

.guide-content {
  position: relative;
  z-index: 1;
  padding: 80rpx $spacing-xl $spacing-xl;
  text-align: center;
}

.guide-avatar-wrap {
  position: relative;
  width: 140rpx;
  height: 140rpx;
  margin: 0 auto $spacing-lg;
}

.guide-avatar-ring {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  border: 3rpx solid transparent;
  background: linear-gradient(135deg, $book-primary, $song-primary, $video-primary) border-box;
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask-composite: xor;
  animation: ringRotate 4s linear infinite;
}

.guide-avatar {
  position: absolute;
  top: 8rpx;
  left: 8rpx;
  right: 8rpx;
  bottom: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $gradient-dreamy;
  border-radius: 50%;
  box-shadow: $shadow-md;

  text {
    font-size: 64rpx;
  }
}

.guide-title {
  display: block;
  font-size: $font-xxl;
  font-weight: 800;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.guide-subtitle {
  display: block;
  font-size: $font-base;
  color: $primary;
  font-weight: 600;
  margin-bottom: $spacing-sm;
}

.guide-desc {
  display: block;
  font-size: $font-sm;
  color: $text-tertiary;
  margin-bottom: $spacing-xl;
  line-height: 1.6;
}

.guide-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 300rpx;
  height: 100rpx;
  background: $gradient-primary;
  border-radius: 50rpx;
  box-shadow: $shadow-button;
  overflow: hidden;

  &:active {
    transform: scale(0.96);
  }
}

.guide-btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: btnShine 3s ease-in-out infinite;
}

@keyframes btnShine {
  0% { left: -100%; }
  50%, 100% { left: 150%; }
}

.guide-btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.btn-sparkle {
  font-size: 28rpx;
}

.btn-text {
  font-size: $font-md;
  font-weight: 600;
  color: #fff;
}
</style>
