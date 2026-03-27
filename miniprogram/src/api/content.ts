/**
 * 内容生成相关 API
 */
import request from './request'

// 主题项接口
export interface ThemeItem {
  id: string
  name: string
  subcategory: string
  age_range: [number, number]
  keywords: string[]
}

// 主题分类接口
export interface ThemeCategory {
  name: string
  themes: ThemeItem[]
}

// 主题列表接口
export interface ThemeList {
  habit: ThemeCategory
  cognition: ThemeCategory
  emotion: ThemeCategory
  [key: string]: ThemeCategory
}

// 绘本页面接口
export interface PictureBookPage {
  page_number: number
  text: string
  image_url: string
  image_thumb_url?: string  // 256px 缩略图 URL（用于渐进式加载）
  audio_url: string
  duration: number
  interaction?: {
    type: 'tap' | 'drag' | 'shake'
    prompt: string
  }
}

// 绘本接口
export interface PictureBook {
  id: string
  title: string
  theme_topic: string
  theme_category?: string  // 主题分类（后端返回时可能包含）
  educational_goal: string
  pages: PictureBookPage[]
  total_duration: number
  total_interactions: number
  personalization: {
    child_name: string
    characters: string[]
  }
  cover_url?: string
  cover_thumb_url?: string  // 封面缩略图 URL（用于列表页快速加载）
  created_at: string
}

// 艺术风格类型（扩展支持 Gemini 服务的更多风格）
export type ArtStyle =
  // 3D 风格
  | 'pixar_3d' | 'pixar' | 'clay' | 'figurine' | 'dreamworks' | 'disney_3d' | 'low_poly'
  // 插画风格
  | 'storybook' | 'watercolor' | 'cartoon' | 'flat' | 'flat_vector' | 'crayon' | 'colored_pencil'
  // 动漫风格
  | 'anime' | 'chibi' | 'manga' | 'ghibli' | 'shinkai' | 'comic_book'
  // 艺术风格
  | 'oil_painting' | 'sketch' | 'ink_wash' | 'pixel_art' | 'impressionist' | 'pop_art' | 'art_nouveau'
  // 特色风格
  | 'papercut' | 'embroidery' | 'mosaic' | 'stained_glass' | 'felt_craft' | 'origami'
  // 其他
  | 'none' | string  // 支持自定义风格字符串

// 主角动物类型
export type ProtagonistAnimal = 'bunny' | 'bear' | 'cat' | 'dog' | 'panda' | 'fox' | 'elephant' | 'penguin' | 'monkey'

// 色调类型
export type ColorPalette = 'pastel' | 'vibrant' | 'warm' | 'cool' | 'monochrome'

// Qwen TTS 音色（当前默认）
export type QwenVoiceId = 'Cherry' | 'Jennifer' | 'Kiki' | 'Ethan' | 'Ryan' | 'Nofish'

// Gemini TTS 音色（后端支持）
export type GeminiVoiceId = 'Kore' | 'Leda' | 'Aoede' | 'Puck' | 'Charon' | 'Fenrir'

// TTS 音色 ID（支持两套音色系统）
export type VoiceId = QwenVoiceId | GeminiVoiceId

// TTS 音色配置
export interface VoiceOption {
  id: VoiceId
  name: string        // 中文名
  gender: 'female' | 'male' | 'neutral'
  style: string       // 风格描述
  emoji?: string      // 展示图标
  recommended?: boolean
}

// 主角配置
export interface ProtagonistConfig {
  animal: ProtagonistAnimal
  color?: string
  accessory?: string
}

// 创作模式类型
export type CreationMode = 'smart' | 'preset'

// 生成绘本参数
export interface GeneratePictureBookParams {
  child_name: string
  age_months: number
  theme_topic: string
  theme_category: string
  favorite_characters?: string[]
  voice_id?: string
  // 新增风格参数
  art_style?: ArtStyle
  protagonist?: ProtagonistConfig
  color_palette?: ColorPalette
  // 智能创作参数
  creation_mode?: CreationMode      // 创作模式：smart=智能创作, preset=预设主题
  custom_prompt?: string            // 用户自定义描述（creation_mode='smart' 时必填）
}

// 音乐情绪类型
export type MusicMood = 'cheerful' | 'gentle' | 'playful' | 'lullaby' | 'educational' | 'energetic' | 'mysterious' | 'inspiring' | 'relaxed'

// 视频动效类型
export type MotionStyle = 'gentle' | 'dynamic' | 'static'

// 艺术风格选项
export interface ArtStyleOption {
  id: ArtStyle
  name: string
  name_en: string
  description: string
  preview_url?: string
  recommended?: boolean
}

// 主角选项
export interface ProtagonistOption {
  animal: ProtagonistAnimal
  name: string
  default_color: string
  default_accessory: string
  preview_url?: string
}

// 色彩风格选项
export interface ColorPaletteOption {
  id: ColorPalette
  name: string
  description: string
  colors: string[]
}

// 配饰选项
export interface AccessoryOption {
  id: string
  name: string
  name_en: string
}

// 音乐情绪选项
export interface MusicMoodOption {
  id: MusicMood
  name: string
  description: string
}

// 动效风格选项
export interface MotionStyleOption {
  id: MotionStyle
  name: string
  description: string
}

// 视频模型选项
export interface VideoModelOption {
  id: string
  description: string
  resolutions: string[]
  durations: number[]
  has_audio: boolean
  shot_types: string[]
  recommended?: boolean
}

// 分辨率选项
export interface ResolutionOption {
  id: string
  name: string
  sizes: string[]
}

// 时长选项
export interface DurationOption {
  value: number
  label: string
}

// 镜头类型选项
export interface ShotTypeOption {
  id: string
  name: string
  description: string
}

// 视频选项
export interface VideoOptionsConfig {
  models: VideoModelOption[]
  resolutions: ResolutionOption[]
  durations: DurationOption[]
  shot_types: ShotTypeOption[]
}

// 风格选项响应（完整版，匹配后端 API）
export interface StyleOptions {
  art_styles: ArtStyleOption[]
  protagonists: ProtagonistOption[]
  color_palettes: ColorPaletteOption[]
  accessories: AccessoryOption[]
  music_moods: MusicMoodOption[]
  video_motion_styles: MotionStyleOption[]
  tts_voices: VoiceOption[]
  video_options: VideoOptionsConfig
}

// 儿歌音乐风格（兼容旧版）
export type MusicStyle = MusicMood

// 生成儿歌参数（V2 增强版，支持 31 个参数）
export interface GenerateNurseryRhymeParams {
  // === 必填参数 ===
  child_name: string
  age_months: number

  // === 主题参数 ===
  theme_topic: string
  theme_category: string
  educational_focus?: string              // 教育目标（单选）

  // === 创作模式 ===
  creation_mode?: CreationMode           // 'preset'（预设模式）或 'smart'（智能模式）
  custom_prompt?: string                 // 智能模式下的自由创作描述
  inspiration_keywords?: string[]        // 灵感关键词

  // === 音乐风格 ===
  music_mood?: string                    // 音乐氛围：cheerful/gentle/playful/lullaby/energetic/mysterious/inspiring/relaxed
  music_genre?: string                   // 音乐流派（单选）
  tempo?: number                         // 节奏速度 (60-180 BPM)
  energy_level?: number                  // 能量强度 (1-10)

  // === 人声演唱 ===
  vocal_type?: string                    // 人声类型：soft_female/warm_male/child/chorus/duet/instrumental
  vocal_range?: string                   // 音域：high/mid/low
  vocal_emotion?: string                 // 情感表达：happy/tender/playful/calm/dreamy/passionate/gentle/mysterious
  vocal_style?: string                   // 演唱技巧（单选）
  vocal_effects?: string[]               // 声音效果（支持多选）
  vocal_regional?: string                // 地域特色：american/british/japanese/korean/chinese/latin

  // === 乐器与音效 ===
  instruments?: string[]                 // 乐器偏好（支持多选）
  sound_effects?: string[]               // 音效元素（支持多选）

  // === 歌词设置 ===
  lyric_complexity?: number              // 歌词复杂度 (1-10)
  repetition_level?: number              // 重复程度 (1-10)

  // === 歌曲结构 ===
  song_structure?: string                // 歌曲结构：simple/standard/full/chorus_only/progressive/narrative/call_response/rap/aaba/custom
  duration_preference?: number           // 时长偏好（秒）
  has_actions?: boolean                  // 是否包含动作指引
  action_types?: string                  // 动作类型（单选）

  // === 语言文化 ===
  language?: string                      // 歌曲语言
  cultural_style?: string                // 文化风格

  // === 个性化 ===
  favorite_characters?: string[]         // 喜欢的角色
  favorite_animals?: string[]            // 喜欢的动物
  favorite_colors?: string[]             // 喜欢的颜色

  // === Suno 高级控制 ===
  style_weight?: number                  // 风格引导权重 (0-1)
  creativity?: number                    // 创意程度 (0-1)
  negative_tags?: string                 // 排除的风格标签
  style_description?: string             // 自定义风格描述
  seed?: number                          // 随机种子（复现结果）

  // === 兼容旧参数 ===
  music_style?: MusicStyle
  art_style?: ArtStyle
  protagonist?: ProtagonistConfig
  color_palette?: ColorPalette
}

// 歌词段落接口
export interface LyricsSection {
  content: string
}

// 时间戳歌词项（Suno 精确时间戳）
export interface TimestampedLyricItem {
  word: string
  start_s: number
  end_s: number
}

// 歌词接口（新版本包含时间戳）
export interface LyricsObject {
  full_text: string
  sections?: LyricsSection[]
  timestamped?: TimestampedLyricItem[]  // Suno 精确时间戳
}

// 歌曲轨道接口
export interface SongTrack {
  id: string
  audio_url: string
  cover_url?: string
  video_url?: string
  lyric?: string
  timestamped_lyrics?: TimestampedLyricItem[]
  duration: number
  title: string
}

// 儿歌接口
export interface NurseryRhyme {
  id: string
  title: string
  theme_topic: string
  // lyrics 可能是字符串或对象，取决于后端版本
  lyrics: string | LyricsObject
  audio_url: string
  video_url?: string           // Suno 音乐视频
  cover_url?: string           // Imagen 主封面
  suno_cover_url?: string      // Suno 封面（备用）
  duration: number
  music_style: MusicStyle
  personalization: {
    child_name: string
  }
  all_tracks?: SongTrack[]     // 所有歌曲版本（Suno 返回 2 首）
  created_at: string
}

/**
 * 获取主题列表
 */
export async function getThemes(): Promise<ThemeList> {
  return request.get<ThemeList>('/content/themes')
}

// 默认风格选项（后端未返回时使用）
const DEFAULT_STYLE_OPTIONS: StyleOptions = {
  art_styles: [
    { id: 'pixar_3d', name: '皮克斯3D', name_en: 'Pixar 3D', description: '使用皮克斯3D风格绘制', recommended: true },
    { id: 'watercolor', name: '水彩手绘', name_en: 'Watercolor', description: '柔和温馨的水彩画风' },
    { id: 'flat_vector', name: '扁平插画', name_en: 'Flat Vector', description: '现代简约的扁平设计' },
    { id: 'crayon', name: '蜡笔涂鸦', name_en: 'Crayon', description: '童趣十足的蜡笔画风' },
    { id: 'anime', name: '日系动漫', name_en: 'Anime', description: '可爱细腻的日系风格' }
  ],
  protagonists: [
    { animal: 'bunny', name: '小兔子', default_color: 'white', default_accessory: 'blue overalls' },
    { animal: 'bear', name: '小熊', default_color: 'brown', default_accessory: 'red scarf' },
    { animal: 'cat', name: '小猫咪', default_color: 'orange', default_accessory: 'bell collar' },
    { animal: 'dog', name: '小狗狗', default_color: 'golden', default_accessory: 'blue bandana' },
    { animal: 'panda', name: '熊猫', default_color: 'black and white', default_accessory: 'bamboo' },
    { animal: 'fox', name: '小狐狸', default_color: 'orange', default_accessory: 'green scarf' }
  ],
  color_palettes: [
    { id: 'pastel', name: '马卡龙色', description: '柔和温馨', colors: ['#FFB5BA', '#B5D8FF', '#C5F0A4', '#FFF5BA'] },
    { id: 'vibrant', name: '活力鲜艳', description: '明快活泼', colors: ['#FF4757', '#3742FA', '#2ED573', '#FFA502'] },
    { id: 'warm', name: '暖暖阳光', description: '温暖舒适', colors: ['#FF6B35', '#F7C566', '#E8A87C', '#FFE4C4'] },
    { id: 'cool', name: '清新冷调', description: '清爽宁静', colors: ['#74B9FF', '#81ECEC', '#A29BFE', '#DFE6E9'] },
    { id: 'monochrome', name: '简约单色', description: '优雅简洁', colors: ['#2D3436', '#636E72', '#B2BEC3', '#DFE6E9'] }
  ],
  accessories: [
    { id: 'blue_overalls', name: '蓝色背带裤', name_en: 'blue overalls' },
    { id: 'red_scarf', name: '红色围巾', name_en: 'red scarf' },
    { id: 'yellow_raincoat', name: '黄色雨衣', name_en: 'yellow raincoat' },
    { id: 'pink_bow', name: '粉色蝴蝶结', name_en: 'pink bow' },
    { id: 'green_hat', name: '绿色小帽', name_en: 'green hat' }
  ],
  music_moods: [
    { id: 'cheerful', name: '欢快活泼', description: '适合日常活动主题' },
    { id: 'gentle', name: '温柔舒缓', description: '适合睡前或安静时刻' },
    { id: 'playful', name: '调皮有趣', description: '适合游戏互动主题' },
    { id: 'lullaby', name: '摇篮曲', description: '适合哄睡' },
    { id: 'educational', name: '教育启蒙', description: '适合认知学习主题' }
  ],
  video_motion_styles: [
    { id: 'gentle', name: '柔和过渡', description: '轻柔自然的动画效果' },
    { id: 'dynamic', name: '活泼生动', description: '充满活力的动态效果' },
    { id: 'static', name: '静态展示', description: '稳定清晰的展示效果' }
  ],
  tts_voices: [
    { id: 'Cherry', name: '芊悦', gender: 'female', style: '温柔亲切', recommended: true },
    { id: 'Jennifer', name: '詹妮弗', gender: 'female', style: '清晰标准' },
    { id: 'Kiki', name: '阿清', gender: 'female', style: '粤语' },
    { id: 'Ethan', name: '晨煦', gender: 'male', style: '成熟稳重' },
    { id: 'Ryan', name: '甜茶', gender: 'male', style: '温暖亲和' },
    { id: 'Nofish', name: '不吃鱼', gender: 'male', style: '活泼有趣' }
  ],
  video_options: {
    models: [
      { id: 'wan2.1-i2v-plus', description: '专业版（推荐）', resolutions: ['480P', '720P'], durations: [5], has_audio: false, shot_types: ['single'], recommended: true },
      { id: 'wan2.1-i2v-turbo', description: '极速版', resolutions: ['480P', '720P'], durations: [5], has_audio: false, shot_types: ['single'] }
    ],
    resolutions: [
      { id: '480P', name: '480P 标清', sizes: ['832*480', '480*832', '624*624'] },
      { id: '720P', name: '720P 高清', sizes: ['1280*720', '720*1280', '960*960'] }
    ],
    durations: [
      { value: 5, label: '5秒' }
    ],
    shot_types: [
      { id: 'single', name: '单镜头', description: '单一场景连贯运动' }
    ]
  }
}

/**
 * 获取风格选项
 * 优先从后端获取，失败时使用本地默认值
 */
export async function getStyleOptions(): Promise<StyleOptions> {
  try {
    const result = await request.get<StyleOptions>('/content/style-options', {
      showError: false,
      timeout: 10000
    })
    // 合并后端返回和本地默认值，确保字段完整
    return {
      ...DEFAULT_STYLE_OPTIONS,
      ...result,
      // 如果后端返回的数组为空，使用默认值
      art_styles: result.art_styles?.length ? result.art_styles : DEFAULT_STYLE_OPTIONS.art_styles,
      protagonists: result.protagonists?.length ? result.protagonists : DEFAULT_STYLE_OPTIONS.protagonists,
      color_palettes: result.color_palettes?.length ? result.color_palettes : DEFAULT_STYLE_OPTIONS.color_palettes,
      music_moods: result.music_moods?.length ? result.music_moods : DEFAULT_STYLE_OPTIONS.music_moods,
      tts_voices: result.tts_voices?.length ? result.tts_voices : DEFAULT_STYLE_OPTIONS.tts_voices,
      video_options: result.video_options?.models?.length ? result.video_options : DEFAULT_STYLE_OPTIONS.video_options
    }
  } catch (e) {
    console.warn('[getStyleOptions] 获取后端风格选项失败，使用本地默认值:', e)
    return DEFAULT_STYLE_OPTIONS
  }
}

/**
 * 生成绘本（同步版，已废弃）
 * @deprecated 使用 generatePictureBookAsync 代替，避免 Cloudflare 524 超时
 */
export async function generatePictureBook(params: GeneratePictureBookParams): Promise<PictureBook> {
  console.log('[generatePictureBook] 开始请求，超时设置: 180000ms (3分钟)')
  const startTime = Date.now()

  try {
    const result = await request.post<PictureBook>('/content/picture-book', params, {
      showLoading: false, // 使用自定义加载动画
      showError: true,
      timeout: 180000 // 3 分钟超时，AI 生成需要较长时间
    })
    console.log(`[generatePictureBook] 请求成功，耗时: ${(Date.now() - startTime) / 1000}秒`)
    return result
  } catch (e: any) {
    console.error(`[generatePictureBook] 请求失败，耗时: ${(Date.now() - startTime) / 1000}秒，错误:`, e)
    throw e
  }
}

// 异步生成绘本响应
export interface AsyncPictureBookResponse {
  task_id: string
  message: string
}

// 绘本任务状态响应
export interface PictureBookTaskStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number  // 0-100
  stage: string     // 生成阶段描述
  message?: string
  content_id?: string  // 完成后返回
  result?: PictureBook  // 完成后返回完整结果
  error?: string
}

/**
 * 异步生成绘本（新版 API，立即返回 task_id）
 * 避免 Cloudflare 524 超时
 */
export async function generatePictureBookAsync(params: GeneratePictureBookParams): Promise<AsyncPictureBookResponse> {
  console.log('[generatePictureBookAsync] 发起异步请求')
  return request.post<AsyncPictureBookResponse>('/content/picture-book/async', params, {
    showLoading: false,
    showError: true,
    timeout: 30000  // 只是提交任务，30秒足够
  })
}

/**
 * 获取绘本生成任务状态
 */
export async function getPictureBookTaskStatus(taskId: string): Promise<PictureBookTaskStatus> {
  return request.get<PictureBookTaskStatus>(`/content/picture-book/status/${taskId}`, {
    timeout: 30000,  // 30秒超时
    showError: false  // 不显示错误提示，由调用方处理
  })
}

/**
 * 生成儿歌
 * AI 生成需要较长时间，设置 3 分钟超时
 */
export async function generateNurseryRhyme(params: GenerateNurseryRhymeParams): Promise<NurseryRhyme> {
  console.log('[generateNurseryRhyme] 开始请求，超时设置: 180000ms (3分钟)')
  const startTime = Date.now()

  try {
    const result = await request.post<NurseryRhyme>('/content/nursery-rhyme', params, {
      showLoading: false,
      showError: true,
      timeout: 180000
    })
    console.log(`[generateNurseryRhyme] 请求成功，耗时: ${(Date.now() - startTime) / 1000}秒`)
    return result
  } catch (e: any) {
    console.error(`[generateNurseryRhyme] 请求失败，耗时: ${(Date.now() - startTime) / 1000}秒，错误:`, e)
    throw e
  }
}

// Suno 任务状态阶段（后端回调实际值）
// text: 歌词生成完成, first: 第一首歌曲完成, complete: 全部完成
export type SunoTaskStage = 'waiting' | 'text' | 'first' | 'complete' | 'error'

// Suno 任务状态响应
export interface SunoTaskStatus {
  task_id: string
  progress: number  // 0-100
  stage: SunoTaskStage
  message?: string
  tracks?: Array<{
    id: string
    title: string
    audio_url: string
    cover_url?: string
    duration: number
    lyrics?: string  // Suno 生成的歌词
  }>
  lyrics?: string  // 也可能在顶层返回歌词
  error?: string
}

/**
 * 轮询 Suno 任务状态（旧版，兼容保留）
 */
export async function getSunoTaskStatus(taskId: string): Promise<SunoTaskStatus> {
  return request.get<SunoTaskStatus>(`/callback/suno/status/${taskId}`)
}

// 异步生成儿歌响应
export interface AsyncNurseryRhymeResponse {
  task_id: string
  message: string
}

// 儿歌任务状态响应（新版异步 API）
export interface NurseryRhymeTaskStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number  // 0-100
  stage: string     // 'text' | 'first' | 'complete' | 'error' 等
  message?: string
  content_id?: string  // 完成后返回
  result?: NurseryRhyme  // 完成后返回完整结果
  error?: string
}

/**
 * 异步生成儿歌（新版 API，立即返回 task_id）
 * 避免 Cloudflare 524 超时
 */
export async function generateNurseryRhymeAsync(params: GenerateNurseryRhymeParams): Promise<AsyncNurseryRhymeResponse> {
  console.log('[generateNurseryRhymeAsync] 发起异步请求')
  return request.post<AsyncNurseryRhymeResponse>('/content/nursery-rhyme/async', params, {
    showLoading: false,
    showError: true,
    timeout: 30000  // 只是提交任务，30秒足够
  })
}

/**
 * 获取儿歌生成任务状态（新版 API）
 */
export async function getNurseryRhymeTaskStatus(taskId: string): Promise<NurseryRhymeTaskStatus> {
  return request.get<NurseryRhymeTaskStatus>(`/content/nursery-rhyme/status/${taskId}`)
}

/**
 * 获取已生成的内容列表
 */
export async function getGeneratedList(params?: {
  type?: 'picture_book' | 'nursery_rhyme' | 'video'
  limit?: number
  offset?: number
}): Promise<{
  items: PictureBook[]
  total: number
  has_more: boolean
}> {
  return request.get('/content/list', {
    data: params,
    useCache: true,
    cacheTTL: 3 * 60 * 1000
  })
}

/**
 * 获取内容详情（带缓存，24小时有效期 — 绘本生成后不可变）
 */
export async function getContentDetail(contentId: string): Promise<PictureBook> {
  return request.get<PictureBook>(`/content/${contentId}`, {
    useCache: true,
    cacheTTL: 24 * 60 * 60 * 1000  // 24 小时缓存
  })
}

/**
 * 删除内容
 */
export async function deleteContent(contentId: string): Promise<void> {
  return request.delete(`/content/${contentId}`)
}

// 视频页面接口
export interface VideoPage {
  page_num: number
  text: string
  image_url: string
  audio_url: string
}

// 场景模板类型
export type SceneTemplateId = 'cover_subtle' | 'character_dialogue' | 'scene_transition' | 'action_scene' | 'emotional_moment'

// 场景模板配置 (Veo 3.1 专版)
export interface SceneTemplate {
  id: SceneTemplateId
  name: string
  icon: string
  description: string
  preset: {
    duration: number
    resolution: string
    motion_mode: string
  }
}

// 负面提示词预设类型
export type NegativePresetId = 'realistic' | 'blur' | 'style_change' | 'shaky' | 'dark' | 'fast' | 'distortion'

// 负面提示词预设配置
export interface NegativePreset {
  id: NegativePresetId
  label: string
  value: string
}

// 生成视频参数 (Veo 3.1 专版)
export interface GenerateVideoParams {
  picture_book: {
    title: string
    pages: VideoPage[]
  }
  child_name: string
  theme_topic: string
  theme_category: string
  // Veo 3.1 基础参数
  aspect_ratio?: '16:9' | '9:16' | '4:3' | '3:4' | '1:1'  // 默认 16:9
  resolution?: '720P' | '1080P'                           // 默认 720P
  duration_seconds?: 4 | 5 | 6 | 8                        // Veo 3.1 支持 4-8 秒，默认 5
  motion_mode?: 'static' | 'slow' | 'normal' | 'dynamic' | 'cinematic'  // 默认 normal
  enable_audio?: boolean                                  // 是否生成原生音效，默认 true
  // Veo 3.1 增强参数
  image_url?: string              // 首帧图片 URL
  prompt?: string                 // 动作描述（使用绘本页面文字）
  reference_images?: string[]     // 角色参考图 URL 列表（最多3张）
  scene_template?: SceneTemplateId // 场景模板 ID
  auto_enhance_prompt?: boolean   // AI 自动优化提示词（默认 true）
  negative_prompt?: string        // 负面提示词
  last_frame_url?: string         // 结束帧图片 URL
  // 旧参数（兼容）
  motion_style?: MotionStyle
}

// 视频接口
export interface Video {
  id: string
  title: string
  video_url: string
  cover_url?: string
  duration: number
  source_book_id?: string
  personalization: {
    child_name: string
  }
  created_at: string
}

/**
 * 生成视频（同步版，已废弃）
 * @deprecated 使用 generateVideoAsync 代替，避免 Cloudflare 524 超时
 */
export async function generateVideo(params: GenerateVideoParams): Promise<Video> {
  console.log('[generateVideo] 开始请求，超时设置: 300000ms (5分钟)')
  const startTime = Date.now()

  try {
    const result = await request.post<Video>('/content/video', params, {
      showLoading: false,
      showError: true,
      timeout: 300000 // 5 分钟超时，视频生成需要更长时间
    })
    console.log(`[generateVideo] 请求成功，耗时: ${(Date.now() - startTime) / 1000}秒`)
    return result
  } catch (e: any) {
    console.error(`[generateVideo] 请求失败，耗时: ${(Date.now() - startTime) / 1000}秒，错误:`, e)
    throw e
  }
}

// 异步生成视频响应
export interface AsyncVideoResponse {
  task_id: string
  message: string
}

// 视频任务状态响应
export interface VideoTaskStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number  // 0-100
  stage: string     // 生成阶段描述
  message?: string
  content_id?: string  // 完成后返回
  result?: Video       // 完成后返回完整结果
  error?: string
}

/**
 * 异步生成视频（新版 API，立即返回 task_id）
 * 避免 Cloudflare 524 超时
 */
export async function generateVideoAsync(params: GenerateVideoParams): Promise<AsyncVideoResponse> {
  console.log('[generateVideoAsync] 发起异步请求')
  return request.post<AsyncVideoResponse>('/content/video/async', params, {
    showLoading: false,
    showError: true,
    timeout: 30000  // 只是提交任务，30秒足够
  })
}

/**
 * 获取视频生成任务状态
 */
export async function getVideoTaskStatus(taskId: string): Promise<VideoTaskStatus> {
  return request.get<VideoTaskStatus>(`/content/video/status/${taskId}`, {
    timeout: 30000,
    showError: false  // 不显示错误提示，由调用方处理
  })
}

// ========== 智能创作 - 首帧生成 ==========

// 首帧生成参数
export interface GenerateFirstFrameParams {
  prompt: string                    // 场景描述
  child_name: string                // 宝贝名称
  art_style?: ArtStyle              // 艺术风格
  aspect_ratio?: '16:9' | '9:16' | '1:1'  // 画面比例
}

// 首帧生成响应
export interface FirstFrameResponse {
  image_url: string                 // 生成的首帧图片 URL
  prompt_enhanced?: string          // AI 优化后的提示词
}

/**
 * 生成视频首帧图片
 * 用于视频独立创作模式，先生成首帧预览
 */
export async function generateFirstFrame(params: GenerateFirstFrameParams): Promise<FirstFrameResponse> {
  console.log('[generateFirstFrame] 开始生成首帧')
  return request.post<FirstFrameResponse>('/content/video/first-frame', params, {
    showLoading: false,
    showError: true,
    timeout: 60000  // 1分钟超时，图片生成较快
  })
}

// ========== 智能创作 - 独立视频创作 ==========

// 独立视频创作参数
export interface GenerateStandaloneVideoParams {
  child_name: string
  age_months: number
  custom_prompt: string             // 视频场景描述
  // 首帧（二选一）
  first_frame_url?: string          // 已有首帧 URL
  generate_first_frame?: boolean    // 是否自动生成首帧，默认 true
  // Veo 3.1 参数
  aspect_ratio?: '16:9' | '9:16' | '4:3' | '3:4' | '1:1'
  resolution?: '720P' | '1080P'
  duration_seconds?: 4 | 5 | 6 | 8
  motion_mode?: 'static' | 'slow' | 'normal' | 'dynamic' | 'cinematic'
  enable_audio?: boolean
  // 高级参数
  art_style?: ArtStyle              // 艺术风格
  auto_enhance_prompt?: boolean     // AI 优化提示词
  negative_prompt?: string          // 负面提示词
  scene_template?: SceneTemplateId  // 场景模板
}

/**
 * 独立创作视频（不依赖绘本）
 * 用户输入描述 → 生成首帧 → 生成视频
 */
export async function generateStandaloneVideoAsync(params: GenerateStandaloneVideoParams): Promise<AsyncVideoResponse> {
  console.log('[generateStandaloneVideoAsync] 发起独立视频创作请求')
  return request.post<AsyncVideoResponse>('/content/video/standalone/async', params, {
    showLoading: false,
    showError: true,
    timeout: 30000  // 只是提交任务
  })
}

// ========== TTS 音色列表 ==========

// 音色详情（带预览URL）
export interface TTSVoiceDetail {
  id: VoiceId
  name: string
  name_cn: string
  gender: 'female' | 'male' | 'neutral'
  style: string
  description: string
  recommended: boolean
  preview_url: string
}

// TTS 服务提供商
export interface TTSProvider {
  id: string
  name: string
  description: string
  voices: TTSVoiceDetail[]
}

// 音色列表响应
export interface TTSVoicesResponse {
  providers: TTSProvider[]
  default_provider: string
  default_voice: string
}

/**
 * 获取 TTS 音色列表
 * 每个音色自带 preview_url，可直接播放预览
 */
export async function getTTSVoices(): Promise<TTSVoicesResponse> {
  console.log('[getTTSVoices] 获取音色列表')
  return request.get<TTSVoicesResponse>('/content/tts/voices', {
    showLoading: false,
    showError: false,
    timeout: 10000
  })
}

// ========== 素材参数和生成日志 ==========

// 生成模型信息
export interface GeneratedByInfo {
  story_model: string       // 故事生成模型
  image_model: string       // 图片生成模型
  tts_model: string         // TTS 模型
}

// 用户输入信息
export interface UserInputsInfo {
  child_name: string
  age_months: number | null
  favorite_characters: string[]
  voice_id: string | null
  creation_mode: 'preset' | 'smart'
  custom_prompt: string | null
  theme_category: string
  theme_topic: string
}

// 增强参数
export interface EnhancementParams {
  story_enhancement: {
    narrative_pace?: string | null
    interaction_density?: string | null
    educational_focus?: string | null
    language_style?: string | null
    plot_complexity?: string | null
    ending_style?: string | null
  } | null
  visual_enhancement: {
    time_atmosphere?: string | null
    scene_environment?: string | null
    emotional_tone?: string | null
    composition_style?: string | null
    lighting_effect?: string | null
  } | null
}

// 主角信息
export interface ProtagonistInfo {
  animal: string
  color: string
  accessory: string
}

// 图片生成配置（通用参数）
export interface ImageGenerationConfig {
  model: string
  style: string
  width: number
  height: number
  protagonist: ProtagonistInfo
  color_palette: string
}

// 音频生成配置（通用参数）
export interface AudioGenerationConfig {
  model: string
  voice_id: string
}

// 生成配置（存储通用参数，避免每个素材重复）
export interface GenerationConfig {
  image: ImageGenerationConfig
  audio: AudioGenerationConfig
}

// 图片素材（精简版，通用参数在 generation_config 中）
export interface ImageAsset {
  type: 'image'
  page_num: number
  url: string
  prompt: string
}

// 音频素材（精简版，通用参数在 generation_config 中）
export interface AudioAsset {
  type: 'audio'
  page_num: number
  url: string
  text: string
  duration: number
}

// 素材类型
export type AssetDetail = ImageAsset | AudioAsset

// ========== 儿歌素材参数类型 ==========

// 提示词增强配置（儿歌专用）
export interface PromptEnhancementConfig {
  model: string
  user_prompt: string
  enhanced_prompt: string
}

// 音乐生成配置（儿歌专用）
export interface MusicGenerationConfig {
  model: string
  generation_mode?: string
  music_mood?: string
  music_genre?: string
  tempo?: number | string
  energy_level?: number | string
  vocal_type?: string
  vocal_range?: string
  vocal_emotion?: string
  vocal_style?: string
  vocal_effects?: string[]
  vocal_regional?: string
  instruments?: string[]
  sound_effects?: string[]
  lyric_complexity?: number | string
  repetition_level?: number | string
  song_structure?: string
  duration_preference?: number | string
  action_types?: string[]
  language?: string
  cultural_style?: string
  style_weight?: number | string
  creativity?: number | string
  negative_tags?: string[]
  style_description?: string
}

// 歌词配置（儿歌专用）
export interface LyricsGenerationConfig {
  full_text: string
  prompt_used?: string
  has_timestamps: boolean
}

// 儿歌生成配置
export interface NurseryRhymeGenerationConfig {
  prompt_enhancement?: PromptEnhancementConfig
  music?: MusicGenerationConfig
  lyrics?: LyricsGenerationConfig
}

// 儿歌素材类型
export interface CoverImageAsset {
  type: 'cover_image'
  url: string
  source?: string  // 'suno'
}

export interface SunoCoverAsset {
  type: 'suno_cover'
  url: string
}

export interface NurseryRhymeAudioAsset {
  type: 'audio'
  url: string
  duration: number
  format?: string
}

export interface NurseryRhymeVideoAsset {
  type: 'video'
  url: string
  duration: number
}

export interface AudioTrackAsset {
  type: 'audio_track'
  track_num: number
  url: string
  duration: number
  cover_url?: string
}

export type NurseryRhymeAsset = CoverImageAsset | SunoCoverAsset | NurseryRhymeAudioAsset | NurseryRhymeVideoAsset | AudioTrackAsset

// 儿歌生成模型信息
export interface NurseryRhymeGeneratedByInfo {
  prompt_model?: string
  music_model?: string
}

// 用户选择参数（儿歌专用）
export interface NurseryRhymeUserSelections {
  creation_mode?: string
  theme_category?: string
  theme_topic?: string
  age_months?: number
  music_mood?: string
  music_genre?: string
  tempo?: number
  energy_level?: number
  vocal_type?: string
  vocal_range?: string
  vocal_emotion?: string
  vocal_style?: string
  vocal_effects?: string[]
  vocal_regional?: string
  instruments?: string[]
  sound_effects?: string[]
  lyric_complexity?: number
  repetition_level?: number
  song_structure?: string
  duration_preference?: number
  action_types?: string[]
  language?: string
  cultural_style?: string
  educational_focus?: string
  favorite_characters?: string[]
  favorite_colors?: string[]
  style_weight?: number
  creativity?: number
  negative_tags?: string[]
  style_description?: string
}

// 儿歌用户输入
export interface NurseryRhymeUserInputsInfo {
  child_name: string
  age_months: number | null
  favorite_characters?: string[]
  voice_id?: string | null
  creation_mode: 'preset' | 'smart'
  custom_prompt?: string | null
  theme_category: string
  theme_topic: string
  user_selections?: NurseryRhymeUserSelections
}

// 儿歌增强参数
export interface NurseryRhymeEnhancementParams {
  story_enhancement?: null
  visual_enhancement?: null
  prompt_enhancement?: {
    original: string
    enhanced: string
    model: string
  }
}

// 儿歌素材参数响应
export interface NurseryRhymeAssetDetailsResponse {
  content_id: string
  content_type: 'nursery_rhyme'
  generated_by: NurseryRhymeGeneratedByInfo
  user_inputs: NurseryRhymeUserInputsInfo
  enhancement_params: NurseryRhymeEnhancementParams
  generation_config: NurseryRhymeGenerationConfig
  assets: NurseryRhymeAsset[]
  total_count: number
}

// ========== 绘本素材参数类型（原有）==========

// 绘本生成配置
export interface PictureBookGenerationConfig {
  image: ImageGenerationConfig
  audio: AudioGenerationConfig
}

// 绘本素材参数响应
export interface PictureBookAssetDetailsResponse {
  content_id: string
  content_type: 'picture_book'
  generated_by: GeneratedByInfo
  user_inputs: UserInputsInfo
  enhancement_params: EnhancementParams
  generation_config: PictureBookGenerationConfig
  assets: AssetDetail[]
  total_count: number
}

// 素材参数响应（联合类型，兼容两种内容类型）
export interface AssetDetailsResponse {
  content_id: string
  content_type: 'picture_book' | 'nursery_rhyme' | 'video'
  generated_by: GeneratedByInfo | NurseryRhymeGeneratedByInfo
  user_inputs: UserInputsInfo | NurseryRhymeUserInputsInfo
  enhancement_params: EnhancementParams | NurseryRhymeEnhancementParams
  generation_config: PictureBookGenerationConfig | NurseryRhymeGenerationConfig  // 根据 content_type 不同结构
  assets: (AssetDetail | NurseryRhymeAsset)[]
  total_count: number
}

/**
 * 获取内容素材参数详情
 * 查看图片 prompt、模型参数等
 */
export async function getAssetDetails(contentId: string): Promise<AssetDetailsResponse> {
  console.log('[getAssetDetails] 获取素材参数:', contentId)
  return request.get<AssetDetailsResponse>(`/content/${contentId}/asset-details`, {
    showLoading: false,
    showError: false,
    timeout: 10000
  })
}

// 生成日志条目
export interface GenerationLogEntry {
  timestamp?: string
  level?: 'info' | 'warning' | 'error'
  stage?: string             // 生成阶段: story, image, audio, video 等
  message?: string
  details?: Record<string, any>
  duration_ms?: number      // 该步骤耗时
}

// 生成日志响应（匹配后端实际返回格式）
export interface GenerationLogsResponse {
  content_id: string
  content_type?: 'picture_book' | 'nursery_rhyme' | 'video'
  title?: string
  created_at?: string
  total_duration_ms?: number
  status?: 'completed' | 'failed'
  logs: GenerationLogEntry[]
  total_count: number
  error?: string
}

/**
 * 获取内容生成日志
 * 用于排查生成过程中的问题
 */
export async function getGenerationLogs(contentId: string): Promise<GenerationLogsResponse> {
  console.log('[getGenerationLogs] 获取生成日志:', contentId)
  return request.get<GenerationLogsResponse>(`/content/${contentId}/generation-logs`, {
    showLoading: false,
    showError: false,
    timeout: 10000
  })
}
