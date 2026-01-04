import request from './request'
import type { Child, ChildSettings } from './types'

// 获取孩子列表
export function getChildren(): Promise<Child[]> {
  return request.get('/child/list')
}

// 添加孩子
export function addChild(data: {
  name: string
  birth_date: string
  avatar_url?: string
  interests?: string[]
  favorite_characters?: string[]
}): Promise<Child> {
  return request.post('/child', data)
}

// 获取孩子设置
export function getChildSettings(childId: string): Promise<ChildSettings> {
  return request.get(`/child/${childId}/settings`)
}

// 更新孩子设置
export function updateChildSettings(childId: string, settings: Partial<ChildSettings>): Promise<ChildSettings> {
  return request.put(`/child/${childId}/settings`, settings)
}

// 更新孩子信息
export function updateChild(childId: string, data: {
  name?: string
  birth_date?: string
  interests?: string[]
  favorite_characters?: string[]
}): Promise<Child> {
  return request.put(`/child/${childId}`, data)
}
