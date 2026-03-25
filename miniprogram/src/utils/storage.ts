/**
 * 本地存储工具
 * 统一管理本地存储的 key 和操作
 */

// 存储 key 常量
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  CURRENT_CHILD_ID: 'current_child_id',
  THEME_CACHE: 'theme_cache',
  LAST_PLAY_CONTENT: 'last_play_content',
  CHILD_MODE_PIN: 'child_mode_pin'
} as const

/**
 * 获取存储值
 */
export function getStorage<T = any>(key: string, defaultValue?: T): T {
  try {
    const value = uni.getStorageSync(key)
    if (value === '' || value === null || value === undefined) {
      return defaultValue as T
    }
    return value as T
  } catch (e) {
    console.error(`读取存储失败 [${key}]:`, e)
    return defaultValue as T
  }
}

/**
 * 设置存储值
 */
export function setStorage(key: string, value: any): boolean {
  try {
    uni.setStorageSync(key, value)
    return true
  } catch (e) {
    console.error(`写入存储失败 [${key}]:`, e)
    return false
  }
}

/**
 * 删除存储值
 */
export function removeStorage(key: string): boolean {
  try {
    uni.removeStorageSync(key)
    return true
  } catch (e) {
    console.error(`删除存储失败 [${key}]:`, e)
    return false
  }
}

/**
 * 清除所有存储
 */
export function clearStorage(): boolean {
  try {
    uni.clearStorageSync()
    return true
  } catch (e) {
    console.error('清除存储失败:', e)
    return false
  }
}

/**
 * 带过期时间的存储
 */
export function setStorageWithExpiry(key: string, value: any, ttlMinutes: number): boolean {
  const item = {
    value,
    expiry: Date.now() + ttlMinutes * 60 * 1000
  }
  return setStorage(key, item)
}

/**
 * 获取带过期时间的存储
 */
export function getStorageWithExpiry<T = any>(key: string): T | null {
  const item = getStorage<{ value: T; expiry: number } | null>(key, null)

  if (!item) return null

  if (Date.now() > item.expiry) {
    removeStorage(key)
    return null
  }

  return item.value
}
