/**
 * Moana API 请求封装
 * 支持 Token 自动刷新、统一错误处理、响应缓存
 */

import cache from '@/utils/cache'

// API 基础配置
const BASE_URL = import.meta.env.VITE_API_URL || 'https://your-api.example.com/api/v1'

// 请求配置接口
interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  params?: Record<string, any>
  header?: Record<string, string>
  showLoading?: boolean
  showError?: boolean
  timeout?: number // 超时时间（毫秒），默认 60000
  useCache?: boolean // 是否使用缓存（仅 GET 请求有效）
  cacheTTL?: number  // 缓存过期时间（毫秒），默认 5 分钟
}

// 响应接口
interface ApiResponse<T = any> {
  data: T
  statusCode: number
}

// 是否正在刷新 Token
let isRefreshing = false
// 等待刷新的请求队列
let refreshSubscribers: Array<(token: string) => void> = []
// GET 请求并发复用，避免同一资源同时被重复请求
const inflightGetRequests = new Map<string, Promise<any>>()

function isPlainObject(value: unknown): value is Record<string, any> {
  return Object.prototype.toString.call(value) === '[object Object]'
}

function normalizeQueryValue(value: any): any {
  if (Array.isArray(value)) {
    return value.map(normalizeQueryValue)
  }

  if (isPlainObject(value)) {
    return Object.keys(value)
      .sort()
      .reduce<Record<string, any>>((acc, key) => {
        const normalized = normalizeQueryValue(value[key])
        if (normalized !== undefined) {
          acc[key] = normalized
        }
        return acc
      }, {})
  }

  return value
}

function buildRequestKey(url: string, query?: Record<string, any>): string {
  if (!query || Object.keys(query).length === 0) {
    return url
  }

  return `${url}?${JSON.stringify(normalizeQueryValue(query))}`
}

/**
 * 添加请求到等待队列
 */
function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

/**
 * Token 刷新完成，执行等待队列
 */
function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

/**
 * 刷新 Token
 */
async function refreshToken(): Promise<string> {
  const refreshToken = uni.getStorageSync('refresh_token')

  if (!refreshToken) {
    throw new Error('No refresh token')
  }

  const res = await uni.request({
    url: `${BASE_URL}/auth/refresh`,
    method: 'POST',
    data: { refresh_token: refreshToken },
    header: { 'Content-Type': 'application/json' }
  })

  if (res.statusCode === 200) {
    const data = res.data as any
    uni.setStorageSync('access_token', data.access_token)
    uni.setStorageSync('refresh_token', data.refresh_token)
    return data.access_token
  }

  throw new Error('Token refresh failed')
}

/**
 * 核心请求函数
 */
async function request<T = any>(options: RequestOptions): Promise<T> {
  const {
    url,
    method = 'GET',
    data,
    params,
    header = {},
    showLoading = false,
    showError = true,
    timeout = 60000,
    useCache = false,
    cacheTTL = 5 * 60 * 1000  // 默认 5 分钟
  } = options

  const queryParams = method === 'GET'
    ? (isPlainObject(params) ? params : isPlainObject(data) ? data : undefined)
    : undefined
  const cacheKey = buildRequestKey(url, queryParams)
  const requestData = method === 'GET' ? queryParams : data

  // GET 请求且启用缓存时，先尝试从缓存获取
  if (method === 'GET' && useCache) {
    const cached = cache.get<T>(cacheKey)
    if (cached) {
      console.log(`[Request] 缓存命中: ${cacheKey}`)
      return cached
    }
  }

  // 复用相同 GET 请求，减少并发重复拉取
  if (method === 'GET') {
    const pendingRequest = inflightGetRequests.get(cacheKey)
    if (pendingRequest) {
      console.log(`[Request] 复用进行中请求: ${cacheKey}`)
      return pendingRequest as Promise<T>
    }
  }

  const executeRequest = async (): Promise<T> => {
    // 显示加载
    if (showLoading) {
      uni.showLoading({ title: '加载中...', mask: true })
    }

    // 获取 Token
    const token = uni.getStorageSync('access_token')

    // 构建请求头
    const requestHeader: Record<string, string> = {
      'Content-Type': 'application/json',
      ...header
    }

    if (token) {
      requestHeader['Authorization'] = `Bearer ${token}`
    }

    try {
      console.log(`[request] ${method} ${url} - timeout: ${timeout}ms`)
      const res = await uni.request({
        url: BASE_URL + url,
        method,
        data: requestData,
        header: requestHeader,
        timeout
      }) as unknown as ApiResponse<T>

      // 隐藏加载
      if (showLoading) {
        uni.hideLoading()
      }

      // Token 过期处理
      if (res.statusCode === 401) {
        // 如果正在刷新，加入等待队列
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            subscribeTokenRefresh(async (newToken: string) => {
              try {
                requestHeader['Authorization'] = `Bearer ${newToken}`
                const retryRes = await uni.request({
                  url: BASE_URL + url,
                  method,
                  data: requestData,
                  header: requestHeader
                }) as unknown as ApiResponse<T>
                resolve(retryRes.data)
              } catch (e) {
                reject(e)
              }
            })
          })
        }

        // 开始刷新 Token
        isRefreshing = true

        try {
          const newToken = await refreshToken()
          isRefreshing = false
          onTokenRefreshed(newToken)

          // 重试原请求
          requestHeader['Authorization'] = `Bearer ${newToken}`
          const retryRes = await uni.request({
            url: BASE_URL + url,
            method,
            data: requestData,
            header: requestHeader
          }) as unknown as ApiResponse<T>

          return retryRes.data
        } catch (e) {
          isRefreshing = false
          // 刷新失败，清除登录状态
          uni.removeStorageSync('access_token')
          uni.removeStorageSync('refresh_token')

          // 跳转到登录
          uni.reLaunch({ url: '/pages/index/index' })
          throw new Error('登录已过期，请重新登录')
        }
      }

      // 其他错误
      if (res.statusCode >= 400) {
        const errorData = res.data as any
        // 处理各种错误格式
        let errorMsg = '请求失败'
        if (typeof errorData?.detail === 'string') {
          errorMsg = errorData.detail
        } else if (Array.isArray(errorData?.detail)) {
          // FastAPI 验证错误格式: [{loc: [...], msg: "...", type: "..."}]
          errorMsg = errorData.detail.map((e: any) => e.msg).join('; ')
        } else if (typeof errorData?.message === 'string') {
          errorMsg = errorData.message
        } else if (typeof errorData === 'string') {
          errorMsg = errorData
        }

        console.error('API Error:', res.statusCode, errorData)

        if (showError) {
          uni.showToast({ title: errorMsg, icon: 'none' })
        }

        throw new Error(errorMsg)
      }

      // GET 请求成功且启用缓存时，写入缓存
      if (method === 'GET' && useCache) {
        cache.set(cacheKey, res.data, cacheTTL)
        console.log(`[Request] 已缓存: ${cacheKey}`)
      }

      return res.data
    } catch (err: any) {
      if (showLoading) {
        uni.hideLoading()
      }

      if (showError && err.message) {
        uni.showToast({ title: err.message, icon: 'none' })
      }

      throw err
    }
  }

  const requestPromise = executeRequest()

  if (method === 'GET') {
    inflightGetRequests.set(cacheKey, requestPromise)
    requestPromise.finally(() => {
      inflightGetRequests.delete(cacheKey)
    })
  }

  return requestPromise
}

// 导出便捷方法
export default {
  get<T = any>(url: string, options?: Partial<RequestOptions>) {
    return request<T>({ url, method: 'GET', ...options })
  },

  post<T = any>(url: string, data?: any, options?: Partial<RequestOptions>) {
    return request<T>({ url, method: 'POST', data, ...options })
  },

  put<T = any>(url: string, data?: any, options?: Partial<RequestOptions>) {
    return request<T>({ url, method: 'PUT', data, ...options })
  },

  delete<T = any>(url: string, options?: Partial<RequestOptions>) {
    return request<T>({ url, method: 'DELETE', ...options })
  }
}
