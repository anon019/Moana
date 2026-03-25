<template>
  <view class="page-container">
    <scroll-view class="main-scroll" scroll-y>
      <!-- 表单卡片 -->
      <view class="form-card animate-slideUp">
        <view class="card-header">
          <text class="card-icon">👶</text>
          <text class="card-title">宝贝信息</text>
        </view>

        <!-- 宝贝名称 -->
        <view class="form-item">
          <text class="form-label">宝贝昵称</text>
          <input
            v-model="form.name"
            class="form-input"
            placeholder="请输入宝贝的昵称"
            maxlength="20"
          />
        </view>

        <!-- 性别选择 -->
        <view class="form-item">
          <text class="form-label">性别</text>
          <view class="gender-selector">
            <view
              class="gender-option"
              :class="{ active: form.gender === 'male' }"
              @tap="form.gender = 'male'"
            >
              <text class="gender-icon">👦</text>
              <text class="gender-text">男孩</text>
            </view>
            <view
              class="gender-option"
              :class="{ active: form.gender === 'female' }"
              @tap="form.gender = 'female'"
            >
              <text class="gender-icon">👧</text>
              <text class="gender-text">女孩</text>
            </view>
          </view>
        </view>

        <!-- 出生日期 -->
        <view class="form-item">
          <text class="form-label">出生日期</text>
          <picker
            mode="date"
            :value="form.birthDate"
            :start="minDate"
            :end="maxDate"
            @change="onDateChange"
          >
            <view class="date-picker">
              <text v-if="form.birthDate" class="date-value">{{ form.birthDate }}</text>
              <text v-else class="date-placeholder">请选择出生日期</text>
              <text class="date-arrow">›</text>
            </view>
          </picker>
        </view>

        <!-- 年龄显示 -->
        <view v-if="ageText" class="age-display">
          <text class="age-label">宝贝年龄</text>
          <text class="age-value">{{ ageText }}</text>
        </view>
      </view>

      <!-- 兴趣标签 -->
      <view class="form-card animate-slideUp delay-1">
        <view class="card-header">
          <text class="card-icon">💝</text>
          <text class="card-title">兴趣爱好（可选）</text>
        </view>

        <view class="interest-tags">
          <view
            v-for="interest in interestOptions"
            :key="interest.value"
            class="interest-tag"
            :class="{ active: form.interests.includes(interest.value) }"
            @tap="toggleInterest(interest.value)"
          >
            <text class="tag-icon">{{ interest.icon }}</text>
            <text class="tag-text">{{ interest.label }}</text>
          </view>
        </view>
      </view>

      <!-- 提示说明 -->
      <view class="tips animate-slideUp delay-2">
        <text class="tips-icon">💡</text>
        <text class="tips-text">
          填写宝贝信息后，我们将为 TA 推荐更适合的内容
        </text>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </scroll-view>

    <!-- 底部按钮 -->
    <view class="bottom-bar">
      <view class="submit-btn" :class="{ disabled: !canSubmit }" @tap="handleSubmit">
        <text>{{ submitting ? '添加中...' : '添加宝贝' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useChildStore } from '@/stores/child'

const childStore = useChildStore()

const form = reactive({
  name: '',
  gender: '' as 'male' | 'female' | '',
  birthDate: '',
  interests: [] as string[]
})

const submitting = ref(false)

const interestOptions = [
  { value: 'animals', label: '动物', icon: '🐻' },
  { value: 'vehicles', label: '交通工具', icon: '🚗' },
  { value: 'space', label: '太空', icon: '🚀' },
  { value: 'princess', label: '公主', icon: '👸' },
  { value: 'dinosaur', label: '恐龙', icon: '🦕' },
  { value: 'ocean', label: '海洋', icon: '🐳' },
  { value: 'music', label: '音乐', icon: '🎵' },
  { value: 'sports', label: '运动', icon: '⚽' }
]

// 日期范围：6年前到今天
const today = new Date()
const maxDate = today.toISOString().split('T')[0]
const minYear = today.getFullYear() - 6
const minDate = `${minYear}-01-01`

const ageText = computed(() => {
  if (!form.birthDate) return ''
  const birth = new Date(form.birthDate)
  const now = new Date()
  const months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
  if (months < 0) return ''
  const years = Math.floor(months / 12)
  const remainMonths = months % 12
  if (years === 0) return `${remainMonths}个月`
  if (remainMonths === 0) return `${years}岁`
  return `${years}岁${remainMonths}个月`
})

const canSubmit = computed(() => {
  // 后端只需要 name 和 birth_date，gender 是可选的 UI 元素
  return form.name.trim() && form.birthDate && !submitting.value
})

function onDateChange(e: any) {
  form.birthDate = e.detail.value
}

function toggleInterest(value: string) {
  const index = form.interests.indexOf(value)
  if (index > -1) {
    form.interests.splice(index, 1)
  } else if (form.interests.length < 5) {
    form.interests.push(value)
  } else {
    uni.showToast({ title: '最多选择5个兴趣', icon: 'none' })
  }
}

async function handleSubmit() {
  if (!canSubmit.value) return

  submitting.value = true
  try {
    // 只发送后端需要的字段 (CreateChildRequest)
    await childStore.addChild({
      name: form.name.trim(),
      birth_date: form.birthDate,  // YYYY-MM-DD 格式
      interests: form.interests.length > 0 ? form.interests : undefined
    })

    uni.showToast({ title: '添加成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e: any) {
    const errMsg = typeof e === 'string' ? e : (e?.message || e?.detail || '添加失败')
    console.error('添加宝贝失败:', e)
    uni.showToast({ title: errMsg, icon: 'none' })
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
  display: flex;
  flex-direction: column;
  width: 750rpx;
  box-sizing: border-box;
  overflow-x: hidden;
}

.main-scroll {
  flex: 1;
  padding: $spacing-md;
  width: 750rpx;
  box-sizing: border-box;
}

.form-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
  box-shadow: $shadow-sm;
}

.card-header {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-sm;
  border-bottom: 1rpx solid $uni-border-color;
}

.card-icon {
  font-size: 36rpx;
}

.card-title {
  font-size: $font-md;
  font-weight: $font-bold;
  color: $text-primary;
}

.form-item {
  margin-bottom: $spacing-md;

  &:last-child {
    margin-bottom: 0;
  }
}

.form-label {
  display: block;
  font-size: $font-sm;
  color: $text-secondary;
  margin-bottom: $spacing-xs;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 $spacing-md;
  background: $bg-warm;
  border-radius: $radius-md;
  font-size: $font-base;
  color: $text-primary;
}

.gender-selector {
  display: flex;
  gap: $spacing-sm;
}

.gender-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-md;
  background: $bg-warm;
  border-radius: $radius-md;
  border: 2rpx solid transparent;
  transition: all $duration-fast;

  &.active {
    border-color: $primary;
    background: rgba($primary, 0.1);
  }
}

.gender-icon {
  font-size: 48rpx;
  margin-bottom: $spacing-xs;
}

.gender-text {
  font-size: $font-sm;
  color: $text-primary;
}

.date-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 $spacing-md;
  background: $bg-warm;
  border-radius: $radius-md;
}

.date-value {
  font-size: $font-base;
  color: $text-primary;
}

.date-placeholder {
  font-size: $font-base;
  color: $text-light;
}

.date-arrow {
  font-size: $font-lg;
  color: $text-light;
}

.age-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-sm $spacing-md;
  background: rgba($secondary, 0.1);
  border-radius: $radius-md;
  margin-top: $spacing-sm;
}

.age-label {
  font-size: $font-sm;
  color: $text-secondary;
}

.age-value {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $secondary;
}

.interest-tags {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
}

.interest-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: $spacing-xs $spacing-sm;
  background: $bg-warm;
  border-radius: $radius-full;
  border: 2rpx solid transparent;
  transition: all $duration-fast;

  &.active {
    border-color: $accent;
    background: rgba($accent, 0.2);
  }
}

.tag-icon {
  font-size: 28rpx;
}

.tag-text {
  font-size: $font-sm;
  color: $text-primary;
}

.tips {
  display: flex;
  align-items: flex-start;
  gap: $spacing-xs;
  padding: $spacing-md;
  background: rgba($secondary, 0.08);
  border-radius: $radius-md;
}

.tips-icon {
  font-size: 28rpx;
  flex-shrink: 0;
}

.tips-text {
  font-size: $font-sm;
  color: $text-secondary;
  line-height: 1.6;
}

.safe-bottom {
  height: 180rpx;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 750rpx;
  padding: $spacing-md;
  padding-bottom: calc(#{$spacing-md} + env(safe-area-inset-bottom));
  background: $bg-card;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.submit-btn {
  height: 96rpx;
  background: $gradient-primary;
  border-radius: $radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-button;
  transition: all $duration-fast;

  text {
    font-size: $font-md;
    font-weight: $font-semibold;
    color: $text-white;
  }

  &:active {
    transform: scale(0.98);
  }

  &.disabled {
    opacity: 0.5;
    pointer-events: none;
  }
}
</style>
