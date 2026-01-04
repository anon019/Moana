// 孩子信息
export interface Child {
  id: string
  name: string
  birth_date: string
  avatar_url?: string | null
  interests: string[]
  favorite_characters: string[]
  current_stage?: string | null
}

// 时间设置
export interface ChildSettings {
  child_id: string
  daily_limit_minutes: number
  session_limit_minutes: number
  rest_reminder_enabled: boolean
}

// 绘本页面
export interface PictureBookPage {
  page_number: number
  text: string
  image_url: string
  image_thumb_url?: string
  audio_url: string
  duration: number
}

// 绘本
export interface PictureBook {
  id: string
  title: string
  theme_topic: string
  theme_category?: string
  pages: PictureBookPage[]
  total_duration: number
  cover_url?: string
  cover_thumb_url?: string
  created_at: string
  content_type?: 'picture_book'
}

// 时间戳歌词
export interface TimestampedLyricItem {
  word: string
  start_s: number
  end_s: number
}

// 歌词对象
export interface LyricsObject {
  full_text: string
  sections?: { content: string }[]
  timestamped?: TimestampedLyricItem[]
}

// 儿歌
export interface NurseryRhyme {
  id: string
  title: string
  theme_topic: string
  lyrics: string | LyricsObject
  audio_url: string
  video_url?: string
  cover_url?: string
  suno_cover_url?: string
  duration: number
  created_at: string
  content_type?: 'nursery_rhyme'
}

// 视频
export interface Video {
  id: string
  title: string
  video_url: string
  cover_url?: string
  duration: number
  created_at: string
  content_type?: 'video'
}

// 内容联合类型
export type Content = PictureBook | NurseryRhyme | Video

// 内容列表响应
export interface ContentListResponse {
  items: Content[]
  total: number
  has_more: boolean
}

// 学习统计
export interface LearningStats {
  total_duration_minutes: number
  total_books: number
  total_songs: number
  total_videos: number
  streak_days: number
  daily_activity: Array<{
    date: string
    has_activity: boolean
    duration_minutes: number
  }>
}
