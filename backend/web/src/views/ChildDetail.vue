<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <!-- 页面头部 -->
    <div class="flex items-center">
      <router-link to="/children" class="mr-4 text-gray-500 hover:text-gray-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </router-link>
      <h1 class="text-2xl font-bold text-gray-900">孩子详情</h1>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="card text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-2">加载中...</p>
    </div>

    <!-- 未找到 -->
    <div v-else-if="!child" class="card text-center py-12">
      <div class="text-6xl mb-4">:(</div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">未找到孩子信息</h3>
      <router-link to="/children" class="text-primary-600 hover:underline">
        返回孩子列表
      </router-link>
    </div>

    <!-- 详情内容 -->
    <template v-else>
      <!-- 头像和基本信息 -->
      <div class="card">
        <div class="flex items-center">
          <div
            class="w-20 h-20 rounded-full flex items-center justify-center text-3xl font-bold"
            :class="isCurrentChild ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600'"
          >
            {{ child.name.charAt(0) }}
          </div>
          <div class="ml-6 flex-1">
            <div class="flex items-center gap-3">
              <h2 class="text-xl font-bold text-gray-900">{{ child.name }}</h2>
              <span
                v-if="isCurrentChild"
                class="px-2 py-1 bg-primary-100 text-primary-600 text-xs font-medium rounded-full"
              >
                当前
              </span>
            </div>
            <p class="text-gray-500 mt-1">{{ calculateAge(child.birth_date) }}</p>
          </div>
          <button
            v-if="!isCurrentChild"
            @click="handleSetCurrent"
            class="btn btn-primary"
          >
            设为当前
          </button>
        </div>
      </div>

      <!-- 编辑表单 -->
      <form @submit.prevent="handleSubmit" class="card space-y-6">
        <h3 class="text-lg font-medium text-gray-900">编辑信息</h3>

        <!-- 姓名 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            姓名 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.name"
            type="text"
            class="input"
            placeholder="请输入孩子的姓名"
            required
          />
        </div>

        <!-- 出生日期 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            出生日期 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.birth_date"
            type="date"
            class="input"
            :max="maxDate"
            required
          />
          <p v-if="form.birth_date" class="text-sm text-gray-500 mt-1">
            年龄: {{ calculateAge(form.birth_date) }}
          </p>
        </div>

        <!-- 兴趣标签 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            兴趣标签 <span class="text-gray-400">(可选)</span>
          </label>
          <div class="flex flex-wrap gap-2 mb-3">
            <button
              v-for="interest in predefinedInterests"
              :key="interest"
              type="button"
              @click="toggleInterest(interest)"
              class="px-3 py-1.5 rounded-full text-sm transition-colors"
              :class="form.interests.includes(interest)
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            >
              {{ interest }}
            </button>
          </div>
          <!-- 自定义兴趣输入 -->
          <div class="flex gap-2">
            <input
              v-model="customInterest"
              type="text"
              class="input flex-1"
              placeholder="输入自定义兴趣"
              @keyup.enter.prevent="addCustomInterest"
            />
            <button
              type="button"
              @click="addCustomInterest"
              class="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
              :disabled="!customInterest.trim()"
            >
              添加
            </button>
          </div>
          <!-- 已选兴趣展示 -->
          <div v-if="form.interests.length > 0" class="mt-3">
            <p class="text-sm text-gray-500 mb-2">已选择:</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="interest in form.interests"
                :key="interest"
                class="inline-flex items-center px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
              >
                {{ interest }}
                <button
                  type="button"
                  @click="removeInterest(interest)"
                  class="ml-1.5 text-primary-500 hover:text-primary-700"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </span>
            </div>
          </div>
        </div>

        <!-- 成功/错误提示 -->
        <div v-if="message" class="p-3 rounded-lg text-sm" :class="messageType === 'success' ? 'bg-green-50 border border-green-200 text-green-600' : 'bg-red-50 border border-red-200 text-red-600'">
          {{ message }}
        </div>

        <!-- 提交按钮 -->
        <div class="flex justify-end gap-3">
          <router-link to="/children" class="btn bg-gray-100 text-gray-700 hover:bg-gray-200">
            取消
          </router-link>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="submitting || !form.name || !form.birth_date || !hasChanges"
          >
            {{ submitting ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </form>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useChildStore } from '@/stores/child'
import type { Child } from '@/api/types'

const route = useRoute()
const childStore = useChildStore()

// 预定义兴趣
const predefinedInterests = [
  '动物', '恐龙', '汽车', '音乐', '画画', '运动',
  '科学', '太空', '海洋', '童话', '超级英雄', '公主'
]

// 状态
const loading = ref(true)
const child = ref<Child | null>(null)
const submitting = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')
const customInterest = ref('')

// 表单数据
const form = reactive({
  name: '',
  birth_date: '',
  interests: [] as string[]
})

// 原始数据用于对比
const originalForm = reactive({
  name: '',
  birth_date: '',
  interests: [] as string[]
})

// 是否当前孩子
const isCurrentChild = computed(() => childStore.currentChild?.id === child.value?.id)

// 最大日期（今天）
const maxDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

// 是否有修改
const hasChanges = computed(() => {
  return form.name !== originalForm.name ||
    form.birth_date !== originalForm.birth_date ||
    JSON.stringify(form.interests.slice().sort()) !== JSON.stringify(originalForm.interests.slice().sort())
})

// 计算年龄
function calculateAge(birthDate: string): string {
  if (!birthDate) return ''
  const birth = new Date(birthDate)
  const now = new Date()
  const months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
  if (months <= 0) return '不足1个月'
  const years = Math.floor(months / 12)
  const remainMonths = months % 12
  if (years === 0) return `${remainMonths}个月`
  if (remainMonths === 0) return `${years}岁`
  return `${years}岁${remainMonths}个月`
}

// 切换兴趣选择
function toggleInterest(interest: string) {
  const index = form.interests.indexOf(interest)
  if (index === -1) {
    form.interests.push(interest)
  } else {
    form.interests.splice(index, 1)
  }
}

// 添加自定义兴趣
function addCustomInterest() {
  const interest = customInterest.value.trim()
  if (interest && !form.interests.includes(interest)) {
    form.interests.push(interest)
    customInterest.value = ''
  }
}

// 移除兴趣
function removeInterest(interest: string) {
  const index = form.interests.indexOf(interest)
  if (index !== -1) {
    form.interests.splice(index, 1)
  }
}

// 设为当前孩子
function handleSetCurrent() {
  if (child.value) {
    childStore.setCurrentChild(child.value)
    message.value = '已设为当前孩子'
    messageType.value = 'success'
    setTimeout(() => {
      message.value = ''
    }, 2000)
  }
}

// 初始化表单数据
function initForm(c: Child) {
  form.name = c.name
  form.birth_date = c.birth_date
  form.interests = [...(c.interests || [])]

  originalForm.name = c.name
  originalForm.birth_date = c.birth_date
  originalForm.interests = [...(c.interests || [])]
}

// 提交表单
async function handleSubmit() {
  if (!child.value || !form.name.trim() || !form.birth_date) {
    message.value = '请填写必填字段'
    messageType.value = 'error'
    return
  }

  if (!hasChanges.value) {
    return
  }

  submitting.value = true
  message.value = ''

  try {
    const updatedChild = await childStore.updateChild(child.value.id, {
      name: form.name.trim(),
      birth_date: form.birth_date,
      interests: form.interests
    })
    child.value = updatedChild
    initForm(updatedChild)
    message.value = '保存成功'
    messageType.value = 'success'
    setTimeout(() => {
      message.value = ''
    }, 2000)
  } catch (e: unknown) {
    const err = e as Error
    message.value = err.message || '保存失败，请重试'
    messageType.value = 'error'
  } finally {
    submitting.value = false
  }
}

// 加载数据
onMounted(async () => {
  try {
    await childStore.fetchChildren()
    const childId = route.params.id as string
    const found = childStore.children.find(c => c.id === childId)
    if (found) {
      child.value = found
      initForm(found)
    }
  } finally {
    loading.value = false
  }
})

// 监听路由变化
watch(() => route.params.id, async (newId) => {
  if (newId && typeof newId === 'string') {
    loading.value = true
    try {
      const found = childStore.children.find(c => c.id === newId)
      if (found) {
        child.value = found
        initForm(found)
      } else {
        child.value = null
      }
    } finally {
      loading.value = false
    }
  }
})
</script>
