/**
 * 播放追踪相关 API
 * 基于后端 OpenAPI 规范调整
 */
import request from './request'

// 开始播放响应 (后端返回 play_history_id 用于断点续播)
export interface StartPlayResponse {
  play_history_id: string
  content_id: string
  content_type: string
  resumed_from?: {
    page: number
    progress: number
  }
  is_new: boolean
}

// 播放历史项接口 (匹配后端 PlayHistoryItem)
export interface PlayHistoryItem {
  id: string
  content_id: string
  content_type: string
  content_title?: string
  cover_url?: string
  current_page: number
  total_pages: number
  completion_rate?: number
  progress?: number
  started_at: string
  last_played_at: string
  completed_at: string | null
  is_completed: boolean
}

// 答题统计接口 (匹配后端 PlayStatsResponse)
export interface QuestionStats {
  total_questions: number
  correct_count: number
  accuracy_rate: number
  by_type: Record<string, { total: number; correct: number }>
}

// 更新进度响应
export interface UpdateProgressResponse {
  current_page: number
  completion_rate: number
  time_spent_seconds: number
}

// 完成播放响应
export interface CompletePlayResponse {
  completed_at: string
  total_time_seconds: number
}

// 互动提交响应
export interface SubmitInteractionResponse {
  is_correct: boolean
  feedback?: string
}

// 互动数据接口 (匹配后端 SubmitInteractionRequest)
export interface InteractionData {
  play_history_id: string
  page_number: number
  interaction_type: 'tap' | 'drag' | 'shake' | 'question'
  response_data: Record<string, any>
  response_time_ms: number
}

/**
 * 开始播放
 * 如果已有未完成的播放记录，返回断点位置（断点续播）
 */
export async function startPlay(childId: string, contentId: string, contentType: string = 'picture_book'): Promise<StartPlayResponse> {
  return request.post<StartPlayResponse>('/play/start', {
    child_id: childId,
    content_id: contentId,
    content_type: contentType
  })
}

/**
 * 更新播放进度
 */
export async function updateProgress(
  playHistoryId: string,
  currentPage: number,
  timeSpentSeconds: number
): Promise<UpdateProgressResponse> {
  return request.post<UpdateProgressResponse>('/play/progress', {
    play_history_id: playHistoryId,
    current_page: currentPage,
    time_spent_seconds: timeSpentSeconds
  })
}

/**
 * 完成播放
 * 注意：禁用错误提示，因为重复调用（如已完成的绘本）会返回错误，不需要显示给用户
 */
export async function completePlay(playHistoryId: string): Promise<CompletePlayResponse> {
  return request.post<CompletePlayResponse>('/play/complete', {
    play_history_id: playHistoryId
  }, { showError: false })
}

/**
 * 提交互动记录（答题）
 */
export async function submitInteraction(data: InteractionData): Promise<SubmitInteractionResponse> {
  return request.post<SubmitInteractionResponse>('/play/interaction', data)
}

/**
 * 获取播放历史
 */
export async function getPlayHistory(childId: string, params?: {
  limit?: number
  offset?: number
  content_type?: string
}): Promise<{
  items: PlayHistoryItem[]
  total: number
  has_more: boolean
}> {
  // 手动构建查询字符串，微信小程序不支持 URLSearchParams
  const queryParts: string[] = []
  if (params?.limit) queryParts.push(`limit=${params.limit}`)
  if (params?.offset) queryParts.push(`offset=${params.offset}`)
  if (params?.content_type) queryParts.push(`content_type=${encodeURIComponent(params.content_type)}`)

  const queryString = queryParts.join('&')
  const url = `/play/history/${childId}${queryString ? '?' + queryString : ''}`

  return request.get(url, {
    useCache: true,
    cacheTTL: 60 * 1000
  })
}
