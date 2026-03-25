import request from './request'
import type { LearningStats } from './types'

// 获取今日时长
export async function getTodayStats(childId: string): Promise<{ today_duration: number }> {
  const stats = await request.get<LearningStats>(`/play/learning-stats/${childId}`, {
    params: { days: 1 },
  })

  return {
    today_duration: stats.summary.total_duration_minutes,
  }
}

// 获取学习统计
export function getLearningStats(childId: string, days?: number): Promise<LearningStats> {
  return request.get<LearningStats>(`/play/learning-stats/${childId}`, {
    params: { days },
  })
}
