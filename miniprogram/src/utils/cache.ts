/**
 * API 响应缓存管理
 * 减少重复请求，提升加载速度
 */

const CACHE_PREFIX = 'moana_cache_'
const DEFAULT_TTL = 5 * 60 * 1000  // 默认 5 分钟

interface CacheItem<T> {
  value: T
  expireAt: number
}

class CacheManager {
  private memoryCache = new Map<string, CacheItem<any>>()
  private readonly maxMemoryEntries = 80

  /**
   * 生成缓存 key
   */
  private getKey(url: string): string {
    const normalized = url.replace(/[^a-zA-Z0-9]/g, '_').slice(0, 32)
    return `${CACHE_PREFIX}${normalized}_${this.hash(url)}`
  }

  private hash(value: string): string {
    let hash = 5381

    for (let i = 0; i < value.length; i++) {
      hash = ((hash << 5) + hash) ^ value.charCodeAt(i)
    }

    return (hash >>> 0).toString(36)
  }

  private isExpired<T>(item: CacheItem<T> | null | undefined): item is CacheItem<T> {
    return !!item && Date.now() <= item.expireAt
  }

  private touchMemory<T>(key: string, item: CacheItem<T>) {
    if (this.memoryCache.has(key)) {
      this.memoryCache.delete(key)
    }

    this.memoryCache.set(key, item)

    if (this.memoryCache.size <= this.maxMemoryEntries) {
      return
    }

    const oldestKey = this.memoryCache.keys().next().value
    if (oldestKey) {
      this.memoryCache.delete(oldestKey)
    }
  }

  /**
   * 获取缓存
   */
  get<T>(url: string): T | null {
    try {
      const key = this.getKey(url)
      const memoryItem = this.memoryCache.get(key) as CacheItem<T> | undefined

      if (memoryItem) {
        if (this.isExpired(memoryItem)) {
          this.touchMemory(key, memoryItem)
          return memoryItem.value
        }

        this.memoryCache.delete(key)
      }

      const data = uni.getStorageSync(key) as CacheItem<T> | null

      if (!data) return null

      // 检查是否过期
      if (!this.isExpired(data)) {
        this.remove(url)
        return null
      }

      this.touchMemory(key, data)
      return data.value
    } catch (e) {
      return null
    }
  }

  /**
   * 设置缓存
   */
  set<T>(url: string, value: T, ttl: number = DEFAULT_TTL): boolean {
    try {
      const key = this.getKey(url)
      const item: CacheItem<T> = {
        value,
        expireAt: Date.now() + ttl
      }
      this.touchMemory(key, item)
      uni.setStorageSync(key, item)
      return true
    } catch (e) {
      console.warn('[Cache] 写入失败:', e)
      return false
    }
  }

  /**
   * 删除缓存
   */
  remove(url: string): void {
    try {
      const key = this.getKey(url)
      this.memoryCache.delete(key)
      uni.removeStorageSync(key)
    } catch (e) {
      // ignore
    }
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    try {
      this.memoryCache.clear()
      const info = uni.getStorageInfoSync()
      info.keys.forEach(key => {
        if (key.startsWith(CACHE_PREFIX)) {
          uni.removeStorageSync(key)
        }
      })
    } catch (e) {
      console.warn('[Cache] 清空失败:', e)
    }
  }
}

// 导出单例
export const cache = new CacheManager()
export default cache
