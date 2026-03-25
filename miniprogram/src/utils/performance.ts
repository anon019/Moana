/**
 * 性能监控工具
 * 用于埋点和分析加载性能
 */

interface PerfMeasurement {
  name: string
  duration: number
  timestamp: number
}

class PerformanceMonitor {
  private marks: Record<string, number> = {}
  private measurements: PerfMeasurement[] = []

  /**
   * 标记时间点
   */
  mark(name: string): void {
    this.marks[name] = Date.now()
  }

  /**
   * 计算两个标记之间的时间差
   */
  measure(name: string, startMark: string, endMark?: string): number | null {
    const start = this.marks[startMark]
    const end = endMark ? this.marks[endMark] : Date.now()

    if (!start) {
      console.warn(`[Perf] 未找到起始标记: ${startMark}`)
      return null
    }

    const duration = end - start
    console.log(`[Perf] ${name}: ${duration}ms`)

    // 记录测量结果
    this.measurements.push({
      name,
      duration,
      timestamp: Date.now()
    })

    return duration
  }

  /**
   * 获取所有测量结果
   */
  getMeasurements(): PerfMeasurement[] {
    return [...this.measurements]
  }

  /**
   * 清除所有标记和测量
   */
  clear(): void {
    this.marks = {}
    this.measurements = []
  }

  /**
   * 输出性能报告
   */
  report(): void {
    if (this.measurements.length === 0) {
      console.log('[Perf] 暂无性能数据')
      return
    }

    console.log('╔══════════════════════════════════════╗')
    console.log('║        性能监控报告                   ║')
    console.log('╠══════════════════════════════════════╣')
    this.measurements.forEach(m => {
      const padded = `${m.name}:`.padEnd(20)
      console.log(`║ ${padded} ${m.duration}ms`)
    })
    console.log('╚══════════════════════════════════════╝')
  }
}

export const perf = new PerformanceMonitor()
export default perf
