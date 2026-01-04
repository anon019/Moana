import request from './request'
import type { LearningStats } from './types'

// 获取今日时长
export function getTodayStats(childId: string): Promise<{ today_duration: number }> {
  return request.get(`/play/stats/${childId}`)
}

// 获取学习统计
export function getLearningStats(childId: string, days?: number): Promise<LearningStats> {
  return request.get(`/play/learning-stats/${childId}`, { params: { days } })
}
