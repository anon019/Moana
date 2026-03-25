<template>
  <view class="page-container">
    <NavBar title="意见反馈" :show-back="true" />

    <scroll-view class="main-scroll" scroll-y>
      <!-- 反馈类型 -->
      <view class="section">
        <text class="section-title">反馈类型</text>
        <view class="type-options">
          <view
            v-for="type in feedbackTypes"
            :key="type.value"
            class="type-item"
            :class="{ active: selectedType === type.value }"
            @tap="selectedType = type.value"
          >
            <text class="type-icon">{{ type.icon }}</text>
            <text class="type-name">{{ type.name }}</text>
          </view>
        </view>
      </view>

      <!-- 反馈内容 -->
      <view class="section">
        <text class="section-title">问题描述</text>
        <view class="input-card">
          <textarea
            v-model="content"
            class="feedback-textarea"
            placeholder="请详细描述您遇到的问题或建议..."
            :maxlength="500"
            auto-height
          />
          <text class="char-count">{{ content.length }}/500</text>
        </view>
      </view>

      <!-- 联系方式 -->
      <view class="section">
        <text class="section-title">联系方式（选填）</text>
        <view class="input-card">
          <input
            v-model="contact"
            class="contact-input"
            placeholder="手机号或微信号，方便我们联系您"
            :maxlength="50"
          />
        </view>
      </view>

      <!-- 提交按钮 -->
      <view
        class="submit-btn"
        :class="{ disabled: !canSubmit }"
        @tap="handleSubmit"
      >
        <text>{{ submitting ? '提交中...' : '提交反馈' }}</text>
      </view>

      <!-- 常见问题 -->
      <view class="faq-section">
        <text class="faq-title">常见问题</text>
        <view
          v-for="faq in faqs"
          :key="faq.q"
          class="faq-item"
          @tap="toggleFaq(faq)"
        >
          <view class="faq-question">
            <text>{{ faq.q }}</text>
            <text class="faq-arrow">{{ faq.expanded ? '▲' : '▼' }}</text>
          </view>
          <view v-if="faq.expanded" class="faq-answer">
            <text>{{ faq.a }}</text>
          </view>
        </view>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import NavBar from '@/components/NavBar/NavBar.vue'
import { submitFeedback } from '@/api/feedback'

const feedbackTypes = [
  { value: 'bug', name: '程序问题', icon: '🐛' },
  { value: 'content', name: '内容问题', icon: '📚' },
  { value: 'suggest', name: '功能建议', icon: '💡' },
  { value: 'other', name: '其他', icon: '💬' }
]

const faqs = ref([
  {
    q: '绘本生成需要多长时间？',
    a: '通常需要1-2分钟，具体时间取决于故事长度和网络状况。',
    expanded: false
  },
  {
    q: '如何删除已生成的绘本？',
    a: '在内容库页面，长按想要删除的绘本卡片，即可选择删除。',
    expanded: false
  },
  {
    q: '为什么音频无法播放？',
    a: '请检查手机是否静音，并确保网络连接正常。如仍有问题，请重启小程序。',
    expanded: false
  }
])

const selectedType = ref('suggest')
const content = ref('')
const contact = ref('')
const submitting = ref(false)

const canSubmit = computed(() => {
  return content.value.trim().length >= 10 && !submitting.value
})

function toggleFaq(faq: any) {
  faq.expanded = !faq.expanded
}

async function handleSubmit() {
  if (!canSubmit.value) {
    if (content.value.trim().length < 10) {
      uni.showToast({ title: '请至少输入10个字', icon: 'none' })
    }
    return
  }

  submitting.value = true

  try {
    await submitFeedback({
      type: selectedType.value as 'bug' | 'content' | 'suggest' | 'other',
      content: content.value.trim(),
      contact: contact.value.trim() || undefined
    })

    uni.showToast({ title: '感谢您的反馈！', icon: 'success' })

    // 清空表单
    content.value = ''
    contact.value = ''

    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e: any) {
    uni.showToast({
      title: e.message || '提交失败，请重试',
      icon: 'none'
    })
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.page-container {
  min-height: 100vh;
  background: $bg-base;
  width: 750rpx;
  box-sizing: border-box;
  overflow-x: hidden;
}

.main-scroll {
  padding: $spacing-md;
  width: 750rpx;
  box-sizing: border-box;
}

.section {
  margin-bottom: $spacing-lg;
}

.section-title {
  display: block;
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
  margin-bottom: $spacing-sm;
}

.type-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-sm;
}

.type-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-md $spacing-sm;
  background: $bg-card;
  border-radius: $radius-md;
  border: 2rpx solid transparent;
  transition: all $duration-fast;

  &.active {
    border-color: $primary;
    background: rgba($primary, 0.05);
  }
}

.type-icon {
  font-size: 40rpx;
  margin-bottom: $spacing-xs;
}

.type-name {
  font-size: $font-sm;
  color: $text-primary;
}

.input-card {
  background: $bg-card;
  border-radius: $radius-md;
  padding: $spacing-md;
  position: relative;
}

.feedback-textarea {
  width: 100%;
  min-height: 200rpx;
  font-size: $font-base;
  color: $text-primary;
  line-height: 1.6;
}

.char-count {
  position: absolute;
  right: $spacing-md;
  bottom: $spacing-sm;
  font-size: $font-xs;
  color: $text-light;
}

.contact-input {
  width: 100%;
  font-size: $font-base;
  color: $text-primary;
}

.submit-btn {
  height: 96rpx;
  background: $gradient-primary;
  border-radius: $radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-button;
  margin-bottom: $spacing-xl;

  text {
    font-size: $font-md;
    font-weight: $font-semibold;
    color: $text-white;
  }

  &:active {
    transform: scale(0.98);
  }

  &.disabled {
    background: $text-light;
    box-shadow: none;
  }
}

.faq-section {
  margin-top: $spacing-lg;
}

.faq-title {
  display: block;
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
  margin-bottom: $spacing-sm;
}

.faq-item {
  background: $bg-card;
  border-radius: $radius-md;
  margin-bottom: $spacing-sm;
  overflow: hidden;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;

  text {
    font-size: $font-base;
    color: $text-primary;
  }
}

.faq-arrow {
  font-size: $font-xs;
  color: $text-light;
}

.faq-answer {
  padding: 0 $spacing-md $spacing-md;
  border-top: 1rpx solid $uni-border-color;

  text {
    font-size: $font-sm;
    color: $text-secondary;
    line-height: 1.6;
  }
}

.safe-bottom {
  height: 100rpx;
}
</style>
