/**
 * 内容状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getThemes,
  generatePictureBook,
  getGeneratedList,
  getContentDetail,
  deleteContent,
  type ThemeList,
  type PictureBook,
  type GeneratePictureBookParams
} from '@/api/content'

export const useContentStore = defineStore('content', () => {
  // 状态
  const themes = ref<ThemeList | null>(null)
  const generatedList = ref<PictureBook[]>([])
  const currentContent = ref<PictureBook | null>(null)
  const isGenerating = ref(false)
  const generatingProgress = ref(0) // 0-100

  // 内存缓存层（id → 详情，会话内有效）
  const contentCache = new Map<string, PictureBook>()
  // in-flight 去重（防止同一 ID 并发请求）
  const inflight = new Map<string, Promise<PictureBook>>()

  function hasPlayableDetail(content: PictureBook | null | undefined): content is PictureBook {
    if (!content?.id) return false

    const playable = content as any
    return Boolean(
      (Array.isArray(playable.pages) && playable.pages.length > 0) ||
      playable.audio_url ||
      playable.video_url
    )
  }

  function mergeContentIntoList(content: PictureBook) {
    const index = generatedList.value.findIndex(item => item.id === content.id)
    if (index === -1) return

    generatedList.value[index] = {
      ...generatedList.value[index],
      ...content
    }
  }

  // 将列表中的可播放内容回填到内存缓存
  function backfillContentCache(items: PictureBook[]) {
    items.forEach(item => {
      if (!hasPlayableDetail(item)) {
        return
      }

      const cached = contentCache.get(item.id)
      if (!cached || Object.keys(item as any).length >= Object.keys(cached as any).length) {
        contentCache.set(item.id, item)
      }
    })
  }

  function primeContentCache(content: PictureBook | null | undefined) {
    if (!hasPlayableDetail(content)) {
      return
    }

    contentCache.set(content.id, content)
    mergeContentIntoList(content)
  }

  function getCachedContent(contentId: string): PictureBook | null {
    if (!contentId) return null

    const cached = contentCache.get(contentId)
    if (cached) {
      return cached
    }

    const listItem = generatedList.value.find(item => item.id === contentId)
    if (hasPlayableDetail(listItem)) {
      contentCache.set(contentId, listItem)
      return listItem
    }

    return null
  }

  // 分页状态
  const hasMoreContent = ref(true)
  const isLoadingMore = ref(false)
  const PAGE_SIZE = 20

  // 获取主题列表
  async function fetchThemes() {
    if (themes.value) return themes.value

    try {
      themes.value = await getThemes()
      return themes.value
    } catch (e) {
      console.error('获取主题失败:', e)
      throw e
    }
  }

  // 生成绘本
  async function createPictureBook(params: GeneratePictureBookParams): Promise<PictureBook> {
    isGenerating.value = true
    generatingProgress.value = 0

    let progressInterval: ReturnType<typeof setInterval> | null = null
    try {
      // 模拟进度更新（限制最大值为 95%，避免超过 100%）
      progressInterval = setInterval(() => {
        if (generatingProgress.value < 90) {
          const increment = Math.random() * 10 + 2 // 2-12% 增量
          generatingProgress.value = Math.min(95, generatingProgress.value + increment)
        }
      }, 1500)

      const result = await generatePictureBook(params)

      clearInterval(progressInterval)
      progressInterval = null
      generatingProgress.value = 100

      // 添加到列表
      generatedList.value.unshift(result)
      currentContent.value = result

      return result
    } catch (e) {
      console.error('生成绘本失败:', e)
      throw e
    } finally {
      if (progressInterval) clearInterval(progressInterval)
      isGenerating.value = false
    }
  }

  // 获取已生成内容列表（首次加载或刷新）
  async function fetchGeneratedList(refresh = false) {
    if (!refresh && generatedList.value.length > 0) {
      return generatedList.value
    }

    try {
      const res = await getGeneratedList({ limit: PAGE_SIZE, offset: 0 })
      generatedList.value = res.items
      // 回填到 contentCache：从库点击时直接内存命中，省去 HTTP 请求
      backfillContentCache(res.items)
      // 只根据返回条目数判断：返回数量 < 请求数量 说明没有更多了
      hasMoreContent.value = res.items.length >= PAGE_SIZE
      return res.items
    } catch (e) {
      console.error('获取内容列表失败:', e)
      throw e
    }
  }

  // 加载更多内容（分页）
  async function fetchMoreContent() {
    if (isLoadingMore.value || !hasMoreContent.value) {
      return []
    }

    isLoadingMore.value = true
    try {
      const offset = generatedList.value.length
      const res = await getGeneratedList({ limit: PAGE_SIZE, offset })

      if (res.items.length > 0) {
        generatedList.value = [...generatedList.value, ...res.items]
        backfillContentCache(res.items)
      }

      hasMoreContent.value = res.items.length >= PAGE_SIZE
      return res.items
    } catch (e) {
      console.error('加载更多内容失败:', e)
      throw e
    } finally {
      isLoadingMore.value = false
    }
  }

  // 获取内容详情（内存缓存 → localStorage → HTTP，带 in-flight 去重）
  async function fetchContentDetail(contentId: string) {
    // L1: 内存命中
    const cached = getCachedContent(contentId)
    if (cached) {
      console.log('[fetchContentDetail] 内存缓存命中:', contentId)
      currentContent.value = cached
      return cached
    }

    // L2: in-flight 去重（同一 ID 的并发请求复用同一个 Promise）
    const pending = inflight.get(contentId)
    if (pending) {
      console.log('[fetchContentDetail] 复用进行中请求:', contentId)
      const result = await pending
      currentContent.value = result
      return result
    }

    // L3: 发起请求（localStorage 缓存 → HTTP）
    const promise = getContentDetail(contentId).then(result => {
      primeContentCache(result)
      inflight.delete(contentId)
      return result
    }).catch(e => {
      inflight.delete(contentId)
      throw e
    })
    inflight.set(contentId, promise)

    try {
      const result = await promise
      currentContent.value = result
      return result
    } catch (e: any) {
      console.error('[fetchContentDetail] 获取内容详情失败:', e?.message || e)
      throw e
    }
  }

  // 设置当前内容
  function setCurrentContent(content: PictureBook | null) {
    currentContent.value = content
    if (content) {
      primeContentCache(content)
    }
  }

  // 清除生成状态
  function clearGenerating() {
    isGenerating.value = false
    generatingProgress.value = 0
  }

  // 删除内容
  async function removeContent(contentId: string) {
    try {
      await deleteContent(contentId)
      // 从本地列表和内存缓存中移除
      generatedList.value = generatedList.value.filter(item => item.id !== contentId)
      contentCache.delete(contentId)
      // 如果删除的是当前内容，清空
      if (currentContent.value?.id === contentId) {
        currentContent.value = null
      }
    } catch (e) {
      console.error('删除内容失败:', e)
      throw e
    }
  }

  return {
    themes,
    generatedList,
    currentContent,
    isGenerating,
    generatingProgress,
    hasMoreContent,
    isLoadingMore,
    fetchThemes,
    createPictureBook,
    fetchGeneratedList,
    fetchMoreContent,
    fetchContentDetail,
    getCachedContent,
    primeContentCache,
    setCurrentContent,
    clearGenerating,
    removeContent
  }
})
