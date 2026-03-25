/**
 * 反馈相关 API
 */
import request from './request'

export interface FeedbackParams {
  type: 'bug' | 'content' | 'suggest' | 'other'
  content: string
  contact?: string
}

export interface FeedbackResponse {
  id: string
  message: string
}

/**
 * 提交用户反馈
 */
export async function submitFeedback(params: FeedbackParams): Promise<FeedbackResponse> {
  return request.post<FeedbackResponse>('/feedback', params)
}
