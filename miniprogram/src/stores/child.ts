/**
 * 孩子信息状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/api/request'
import { STORAGE_KEYS, getStorageWithExpiry, setStorageWithExpiry } from '@/utils/storage'

// 孩子信息接口 (与后端 ChildResponse 对齐)
export interface Child {
  id: string
  name: string
  birth_date: string  // YYYY-MM-DD 格式
  avatar_url?: string | null
  interests: string[]
  favorite_characters: string[]
  current_stage?: string | null
}

export const useChildStore = defineStore('child', () => {
  const CHILDREN_CACHE_TTL_MINUTES = 12 * 60
  // 状态
  const children = ref<Child[]>([])
  const currentChild = ref<Child | null>(null)

  function restoreChildrenFromCache() {
    const cachedChildren = getStorageWithExpiry<Child[]>(STORAGE_KEYS.CHILDREN_CACHE) || []
    if (!cachedChildren.length) {
      return
    }

    children.value = cachedChildren

    const savedChildId = uni.getStorageSync(STORAGE_KEYS.CURRENT_CHILD_ID)
    if (savedChildId) {
      const saved = cachedChildren.find(child => child.id === savedChildId)
      if (saved) {
        currentChild.value = saved
        return
      }
    }

    currentChild.value = cachedChildren[0]
  }

  function persistChildrenCache() {
    void setStorageWithExpiry(STORAGE_KEYS.CHILDREN_CACHE, children.value, CHILDREN_CACHE_TTL_MINUTES)
  }

  restoreChildrenFromCache()

  // 计算属性
  const hasChild = computed(() => children.value.length > 0)

  // 根据出生日期计算月龄
  const currentChildAgeMonths = computed(() => {
    if (!currentChild.value?.birth_date) return 0
    const birth = new Date(currentChild.value.birth_date)
    const now = new Date()
    return (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
  })

  const currentChildAge = computed(() => {
    const months = currentChildAgeMonths.value
    if (months <= 0) return ''
    const years = Math.floor(months / 12)
    const remainMonths = months % 12
    if (years === 0) return `${remainMonths}个月`
    if (remainMonths === 0) return `${years}岁`
    return `${years}岁${remainMonths}个月`
  })

  // 设置当前孩子
  function setCurrentChild(child: Child) {
    currentChild.value = child
    uni.setStorageSync(STORAGE_KEYS.CURRENT_CHILD_ID, child.id)
  }

  // 添加孩子 (与后端 CreateChildRequest 对齐)
  async function addChild(data: {
    name: string
    birth_date: string  // 必填，YYYY-MM-DD 格式
    avatar_url?: string
    favorite_characters?: string[]
    interests?: string[]
  }): Promise<Child> {
    const child = await request.post<Child>('/child', data)
    children.value.push(child)

    // 如果是第一个孩子，自动设为当前
    if (children.value.length === 1) {
      setCurrentChild(child)
    }

    persistChildrenCache()

    return child
  }

  // 获取孩子列表
  async function fetchChildren() {
    try {
      const res = await request.get<Child[]>('/child/list')
      children.value = res
      persistChildrenCache()

      // 恢复之前选中的孩子
      const savedChildId = uni.getStorageSync(STORAGE_KEYS.CURRENT_CHILD_ID)
      if (savedChildId) {
        const saved = children.value.find(c => c.id === savedChildId)
        if (saved) {
          currentChild.value = saved
          return
        }
      }

      // 默认选中第一个
      if (children.value.length > 0) {
        setCurrentChild(children.value[0])
      } else {
        currentChild.value = null
      }
    } catch (e) {
      console.error('获取孩子列表失败:', e)
    }
  }

  return {
    children,
    currentChild,
    hasChild,
    currentChildAge,
    currentChildAgeMonths,
    setCurrentChild,
    addChild,
    fetchChildren
  }
})
