import request from './request'
import type { Content, ContentListResponse, PictureBook, NurseryRhyme, Video } from './types'

// 获取内容列表
export function getContentList(params?: {
  type?: 'picture_book' | 'nursery_rhyme' | 'video'
  limit?: number
  offset?: number
}): Promise<ContentListResponse> {
  return request.get('/content/list', { params })
}

// 获取内容详情
export function getContentDetail(contentId: string): Promise<PictureBook | NurseryRhyme | Video> {
  return request.get(`/content/${contentId}`)
}

// 删除内容
export function deleteContent(contentId: string): Promise<void> {
  return request.delete(`/content/${contentId}`)
}

// 导出类型供外部使用
export type { Content, ContentListResponse, PictureBook, NurseryRhyme, Video }
