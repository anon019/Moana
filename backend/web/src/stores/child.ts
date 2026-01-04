import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getChildren, getChildSettings, updateChildSettings as apiUpdateSettings, addChild as apiAddChild, updateChild as apiUpdateChild } from '@/api/child'
import { getTodayStats } from '@/api/play'
import type { Child, ChildSettings } from '@/api/types'

export const useChildStore = defineStore('child', () => {
  const children = ref<Child[]>([])
  const currentChild = ref<Child | null>(null)
  const settings = ref<ChildSettings>({
    child_id: '',
    daily_limit_minutes: 60,
    session_limit_minutes: 30,
    rest_reminder_enabled: true
  })
  const todayDuration = ref(0)

  const hasChild = computed(() => children.value.length > 0)

  const currentChildAge = computed(() => {
    if (!currentChild.value?.birth_date) return ''
    const birth = new Date(currentChild.value.birth_date)
    const now = new Date()
    const months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
    if (months <= 0) return ''
    const years = Math.floor(months / 12)
    const remainMonths = months % 12
    if (years === 0) return `${remainMonths}个月`
    if (remainMonths === 0) return `${years}岁`
    return `${years}岁${remainMonths}个月`
  })

  const currentChildAgeMonths = computed(() => {
    if (!currentChild.value?.birth_date) return 0
    const birth = new Date(currentChild.value.birth_date)
    const now = new Date()
    return (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
  })

  async function fetchChildren() {
    try {
      children.value = await getChildren()
      const savedChildId = localStorage.getItem('current_child_id')
      if (savedChildId) {
        const saved = children.value.find(c => c.id === savedChildId)
        if (saved) {
          currentChild.value = saved
          await fetchSettings()
          return
        }
      }
      if (children.value.length > 0) {
        setCurrentChild(children.value[0])
      }
    } catch (e) {
      console.error('获取孩子列表失败:', e)
    }
  }

  function setCurrentChild(child: Child) {
    currentChild.value = child
    localStorage.setItem('current_child_id', child.id)
    fetchSettings()
    fetchTodayDuration()
  }

  async function fetchSettings() {
    if (!currentChild.value) return
    try {
      settings.value = await getChildSettings(currentChild.value.id)
    } catch {
      settings.value = {
        child_id: currentChild.value.id,
        daily_limit_minutes: 60,
        session_limit_minutes: 30,
        rest_reminder_enabled: true
      }
    }
  }

  async function updateSettings(newSettings: Partial<ChildSettings>) {
    if (!currentChild.value) return
    settings.value = await apiUpdateSettings(currentChild.value.id, { ...settings.value, ...newSettings })
  }

  async function fetchTodayDuration() {
    if (!currentChild.value) return
    try {
      const stats = await getTodayStats(currentChild.value.id)
      todayDuration.value = stats.today_duration
    } catch {
      todayDuration.value = 0
    }
  }

  async function addChild(data: { name: string; birth_date: string; interests?: string[]; favorite_characters?: string[] }) {
    const child = await apiAddChild(data)
    children.value.push(child)
    if (children.value.length === 1) {
      setCurrentChild(child)
    }
    return child
  }

  async function updateChild(childId: string, data: { name?: string; birth_date?: string; interests?: string[]; favorite_characters?: string[] }) {
    const updatedChild = await apiUpdateChild(childId, data)
    const index = children.value.findIndex(c => c.id === childId)
    if (index !== -1) {
      children.value[index] = updatedChild
    }
    if (currentChild.value?.id === childId) {
      currentChild.value = updatedChild
    }
    return updatedChild
  }

  return {
    children,
    currentChild,
    settings,
    todayDuration,
    hasChild,
    currentChildAge,
    currentChildAgeMonths,
    fetchChildren,
    setCurrentChild,
    fetchSettings,
    updateSettings,
    fetchTodayDuration,
    addChild,
    updateChild
  }
})
