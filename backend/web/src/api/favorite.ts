import request from './request'
import type { Content } from './types'

// 获取收藏列表
export function getFavorites(params?: {
  limit?: number
  offset?: number
}): Promise<{ items: Content[]; total: number; has_more: boolean }> {
  return request.get('/library/favorites', { params })
}

// 添加收藏
export function addFavorite(contentId: string): Promise<void> {
  return request.post('/library/favorites', { content_id: contentId })
}

// 取消收藏
export function removeFavorite(contentId: string): Promise<void> {
  return request.delete(`/library/favorites/${contentId}`)
}

// 检查是否已收藏
export function checkFavorite(contentId: string): Promise<{ is_favorite: boolean }> {
  return request.get(`/library/favorites/check/${contentId}`)
}
