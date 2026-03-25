/** 确保 URL 使用 HTTPS 协议 */
export function ensureHttps(url: string): string {
  return url.startsWith('http://') ? url.replace('http://', 'https://') : url
}
