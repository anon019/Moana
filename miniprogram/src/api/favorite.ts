/**
 * 收藏相关 API
 */
import request from './request'

export interface FavoriteItem {
  id: string
  content_id: string
  content_type: 'picture_book' | 'nursery_rhyme' | 'video'
  content_title: string
  cover_url?: string
  created_at: string
}

export interface FavoriteListResponse {
  items: FavoriteItem[]
  total: number
  page: number
  page_size: number
}

/**
 * 添加收藏
 */
export async function addFavorite(contentId: string): Promise<{ id: string }> {
  return request.post('/library/favorites', { content_id: contentId })
}

/**
 * 取消收藏
 */
export async function removeFavorite(contentId: string): Promise<void> {
  return request.delete(`/library/favorites/${contentId}`)
}

/**
 * 检查是否已收藏
 */
export async function checkFavorite(contentId: string): Promise<{ is_favorite: boolean }> {
  return request.get(`/library/favorites/check/${contentId}`)
}

/**
 * 获取收藏列表
 */
export async function getFavoriteList(params?: {
  page?: number
  page_size?: number
  content_type?: string
}): Promise<FavoriteListResponse> {
  return request.get('/library/favorites', { params })
}
