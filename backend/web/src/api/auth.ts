import request from './request'

const ADMIN_PASSWORD = 'Jack@kids'

// 简单密码验证（前端验证）
export function verifyPassword(password: string): boolean {
  return password === ADMIN_PASSWORD
}

// 模拟登录（使用小程序的 mock 登录获取 token）
export async function login(): Promise<{ access_token: string; refresh_token: string }> {
  return request.post('/auth/mock-login')
}

// 登出
export function logout(): void {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('admin_token')
}
