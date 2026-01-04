/**
 * 创作相关 API
 * 从小程序移植，用于网页版创作功能
 */
import request from './request'

// ========== 类型定义 ==========

// 主题项
export interface ThemeItem {
  id: string
  name: string
  subcategory: string
  age_range: [number, number]
  keywords: string[]
}

// 主题分类
export interface ThemeCategory {
  name: string
  themes: ThemeItem[]
}

// 主题列表
export interface ThemeList {
  habit: ThemeCategory
  cognition: ThemeCategory
  emotion: ThemeCategory
  [key: string]: ThemeCategory
}

// 艺术风格
export type ArtStyle =
  | 'pixar_3d' | 'pixar' | 'clay' | 'figurine' | 'dreamworks' | 'disney_3d' | 'low_poly'
  | 'storybook' | 'watercolor' | 'cartoon' | 'flat' | 'flat_vector' | 'crayon' | 'colored_pencil'
  | 'anime' | 'chibi' | 'manga' | 'ghibli' | 'shinkai' | 'comic_book'
  | 'oil_painting' | 'sketch' | 'ink_wash' | 'pixel_art' | 'impressionist' | 'pop_art' | 'art_nouveau'
  | 'papercut' | 'embroidery' | 'mosaic' | 'stained_glass' | 'felt_craft' | 'origami'
  | 'none' | string

// 主角动物
export type ProtagonistAnimal = 'bunny' | 'bear' | 'cat' | 'dog' | 'panda' | 'fox'

// 色调
export type ColorPalette = 'pastel' | 'vibrant' | 'warm' | 'cool' | 'monochrome'

// 音色
export type VoiceId = 'Cherry' | 'Jennifer' | 'Kiki' | 'Ethan' | 'Ryan' | 'Nofish'
  | 'Kore' | 'Leda' | 'Aoede' | 'Puck' | 'Charon' | 'Fenrir'

// 主角配置
export interface ProtagonistConfig {
  animal: ProtagonistAnimal
  color?: string
  accessory?: string
}

// 艺术风格选项
export interface ArtStyleOption {
  id: ArtStyle
  name: string
  name_en: string
  description: string
  preview_url?: string
  recommended?: boolean
  category?: string
}

// 艺术风格分类
export interface ArtStyleCategory {
  id: string
  name: string
  icon: string
  styles: ArtStyleOption[]
}

// 主角选项
export interface ProtagonistOption {
  animal: ProtagonistAnimal
  name: string
  default_color: string
  default_accessory: string
  preview_url?: string
}

// 色彩选项
export interface ColorPaletteOption {
  id: ColorPalette
  name: string
  description: string
  colors: string[]
}

// 音色选项
export interface VoiceOption {
  id: VoiceId
  name: string
  gender: 'female' | 'male' | 'neutral'
  style: string
  description?: string  // 详细说明
  emoji?: string
  recommended?: boolean
}

// 音乐情绪选项
export interface MusicMoodOption {
  id: string
  name: string
  description: string
  detail?: string  // 详细说明
  bpm?: string     // 节拍范围
  emoji?: string
}

// 动效选项
export interface MotionStyleOption {
  id: string
  name: string
  description: string
  icon?: string
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

// 风格选项响应
export interface StyleOptions {
  art_styles: ArtStyleOption[]
  art_style_categories: ArtStyleCategory[]
  protagonists: ProtagonistOption[]
  color_palettes: ColorPaletteOption[]
  accessories: { id: string; name: string; name_en: string }[]
  music_moods: MusicMoodOption[]
  video_motion_styles: MotionStyleOption[]
  tts_voices: VoiceOption[]
  video_options: {
    models: VideoModelOption[]
    resolutions: { id: string; name: string; sizes: string[] }[]
    durations: { value: number; label: string }[]
    shot_types: { id: string; name: string; description: string }[]
  }
}

// ========== 绘本相关 ==========

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
  educational_goal: string
  pages: PictureBookPage[]
  total_duration: number
  total_interactions: number
  personalization: {
    child_name: string
    characters: string[]
  }
  cover_url?: string
  cover_thumb_url?: string
  created_at: string
}

// 故事增强参数
export interface StoryEnhancement {
  narrative_pace?: string | null
  interaction_density?: string | null
  educational_focus?: string | null
  language_style?: string | null
  plot_complexity?: string | null
  ending_style?: string | null
}

// 视觉增强参数
export interface VisualEnhancement {
  time_atmosphere?: string | null
  scene_environment?: string | null
  emotional_tone?: string | null
  composition_style?: string | null
  lighting_effect?: string | null
}

// 生成绘本参数
export interface GeneratePictureBookParams {
  child_name: string
  age_months: number
  theme_topic: string
  theme_category: string
  favorite_characters?: string[]
  voice_id?: string
  art_style?: ArtStyle
  protagonist?: ProtagonistConfig
  color_palette?: ColorPalette
  creation_mode?: 'smart' | 'preset'
  custom_prompt?: string
  // 增强参数
  story_enhancement?: StoryEnhancement
  visual_enhancement?: VisualEnhancement
}

// 异步响应
export interface AsyncResponse {
  task_id: string
  message: string
}

// 任务状态
export interface TaskStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  stage: string
  message?: string
  content_id?: string
  error?: string
}

// 绘本任务状态
export interface PictureBookTaskStatus extends TaskStatus {
  result?: PictureBook
}

// ========== 儿歌相关 ==========

// 歌词对象
export interface LyricsObject {
  full_text: string
  sections?: { content: string }[]
  timestamped?: { word: string; start_s: number; end_s: number }[]
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
  music_style: string
  personalization: {
    child_name: string
  }
  created_at: string
}

// 生成儿歌参数
export interface GenerateNurseryRhymeParams {
  child_name: string
  age_months: number
  theme_topic: string
  theme_category: string
  creation_mode?: 'preset' | 'smart'
  custom_prompt?: string
  favorite_characters?: string[]
  // 音乐风格
  music_mood?: string
  music_genre?: string
  tempo?: number
  energy_level?: number
  // 人声
  vocal_type?: string
  vocal_emotion?: string
  vocal_range?: string
  vocal_style?: string
  // 乐器和音效
  instruments?: string[]
  sound_effects?: string[]
  // 歌词
  lyric_complexity?: number
  repetition_level?: number
  // 结构
  song_structure?: string
  action_types?: string
  // 语言文化
  language?: string
  cultural_style?: string
  // 个性化
  educational_focus?: string
  favorite_colors?: string[]
  // Suno 进阶
  style_weight?: number
  creativity?: number
  negative_tags?: string
  duration_preference?: number
}

// 儿歌任务状态
export interface NurseryRhymeTaskStatus extends TaskStatus {
  result?: NurseryRhyme
}

// ========== 视频相关 ==========

// 视频
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

// 生成独立视频参数
export interface GenerateStandaloneVideoParams {
  child_name: string
  age_months: number
  custom_prompt: string
  first_frame_url?: string
  generate_first_frame?: boolean
  aspect_ratio?: '16:9' | '9:16' | '4:3' | '3:4' | '1:1'
  resolution?: '720P' | '1080P'
  duration_seconds?: 4 | 5 | 6 | 8
  motion_mode?: 'static' | 'slow' | 'normal' | 'dynamic' | 'cinematic'
  enable_audio?: boolean
  art_style?: ArtStyle
  auto_enhance_prompt?: boolean
  negative_prompt?: string
}

// 视频任务状态
export interface VideoTaskStatus extends TaskStatus {
  result?: Video
}

// ========== 默认风格选项 ==========

// 完整的艺术风格分类配置（参考小程序）
const ART_STYLE_CATEGORIES: ArtStyleCategory[] = [
  {
    id: 'threed',
    name: '3D风格',
    icon: '🎬',
    styles: [
      { id: 'pixar_3d', name: '皮克斯3D', name_en: 'Pixar 3D', description: '温馨可爱的皮克斯风格', category: 'threed', recommended: true },
      { id: 'pixar', name: '皮克斯电影', name_en: 'Pixar Film', description: '电影级别的精致渲染', category: 'threed' },
      { id: 'dreamworks', name: 'DreamWorks', name_en: 'DreamWorks', description: '梦工厂动画风格', category: 'threed' },
      { id: 'disney_3d', name: '迪士尼3D', name_en: 'Disney 3D', description: '迪士尼经典3D风格', category: 'threed' },
      { id: 'clay', name: '粘土动画', name_en: 'Clay', description: '手工粘土质感', category: 'threed' },
      { id: 'figurine', name: '手办模型', name_en: 'Figurine', description: '精致的手办质感', category: 'threed' },
      { id: 'low_poly', name: '低多边形', name_en: 'Low Poly', description: '简约几何风格', category: 'threed' }
    ]
  },
  {
    id: 'illustration',
    name: '手绘风格',
    icon: '🖌️',
    styles: [
      { id: 'storybook', name: '故事书', name_en: 'Storybook', description: '经典绘本插画风格', category: 'illustration' },
      { id: 'watercolor', name: '水彩手绘', name_en: 'Watercolor', description: '柔和温馨的水彩画风', category: 'illustration', recommended: true },
      { id: 'cartoon', name: '卡通插画', name_en: 'Cartoon', description: '活泼可爱的卡通风格', category: 'illustration' },
      { id: 'flat_vector', name: '扁平插画', name_en: 'Flat Vector', description: '现代简约的扁平设计', category: 'illustration' },
      { id: 'crayon', name: '蜡笔涂鸦', name_en: 'Crayon', description: '童趣十足的蜡笔画风', category: 'illustration' },
      { id: 'colored_pencil', name: '彩铅', name_en: 'Colored Pencil', description: '细腻的彩铅质感', category: 'illustration' }
    ]
  },
  {
    id: 'anime',
    name: '动漫风格',
    icon: '✨',
    styles: [
      { id: 'anime', name: '日系动漫', name_en: 'Anime', description: '可爱细腻的日系风格', category: 'anime', recommended: true },
      { id: 'chibi', name: 'Q版萌系', name_en: 'Chibi', description: '可爱的Q版造型', category: 'anime' },
      { id: 'ghibli', name: '吉卜力', name_en: 'Ghibli', description: '宫崎骏工作室风格', category: 'anime' },
      { id: 'shinkai', name: '新海诚', name_en: 'Shinkai', description: '唯美的新海诚风格', category: 'anime' },
      { id: 'manga', name: '漫画', name_en: 'Manga', description: '日式漫画风格', category: 'anime' },
      { id: 'comic_book', name: '欧美漫画', name_en: 'Comic Book', description: '欧美漫画风格', category: 'anime' }
    ]
  },
  {
    id: 'artistic',
    name: '绘画风格',
    icon: '🎨',
    styles: [
      { id: 'oil_painting', name: '油画', name_en: 'Oil Painting', description: '经典油画质感', category: 'artistic' },
      { id: 'impressionist', name: '印象派', name_en: 'Impressionist', description: '印象派绘画风格', category: 'artistic' },
      { id: 'sketch', name: '素描', name_en: 'Sketch', description: '铅笔素描风格', category: 'artistic' },
      { id: 'ink_wash', name: '水墨', name_en: 'Ink Wash', description: '中国水墨画风格', category: 'artistic' },
      { id: 'pop_art', name: '波普艺术', name_en: 'Pop Art', description: '波普艺术风格', category: 'artistic' },
      { id: 'art_nouveau', name: '新艺术', name_en: 'Art Nouveau', description: '新艺术运动风格', category: 'artistic' },
      { id: 'pixel_art', name: '像素', name_en: 'Pixel Art', description: '复古像素风格', category: 'artistic' }
    ]
  },
  {
    id: 'craft',
    name: '工艺风格',
    icon: '🧵',
    styles: [
      { id: 'papercut', name: '剪纸', name_en: 'Papercut', description: '中国剪纸艺术风格', category: 'craft' },
      { id: 'felt_craft', name: '毛毡', name_en: 'Felt Craft', description: '温暖的毛毡手工风格', category: 'craft' },
      { id: 'origami', name: '折纸', name_en: 'Origami', description: '日式折纸艺术', category: 'craft' },
      { id: 'embroidery', name: '刺绣', name_en: 'Embroidery', description: '精美的刺绣质感', category: 'craft' },
      { id: 'mosaic', name: '马赛克', name_en: 'Mosaic', description: '马赛克拼贴风格', category: 'craft' },
      { id: 'stained_glass', name: '彩绘玻璃', name_en: 'Stained Glass', description: '教堂彩绘玻璃风格', category: 'craft' }
    ]
  }
]

// 展开所有风格为扁平列表
const ALL_ART_STYLES: ArtStyleOption[] = ART_STYLE_CATEGORIES.flatMap(cat => cat.styles)

// Gemini TTS 音色配置（增强描述）
const ALL_TTS_VOICES: VoiceOption[] = [
  {
    id: 'Kore',
    name: '柯瑞',
    gender: 'female',
    style: '温柔女声',
    description: '语调柔和亲切，如妈妈般温暖。适合睡前故事、温馨家庭主题，给孩子满满安全感',
    emoji: '👩',
    recommended: true
  },
  {
    id: 'Leda',
    name: '蕾达',
    gender: 'female',
    style: '优雅女声',
    description: '咬字清晰有韵律，声音优雅动听。适合经典童话、公主王子故事、文学性较强的内容',
    emoji: '👩'
  },
  {
    id: 'Aoede',
    name: '艾欧德',
    gender: 'female',
    style: '清新女声',
    description: '声音明快自然，充满活力。适合自然探索、户外冒险、动植物科普主题',
    emoji: '👩'
  },
  {
    id: 'Puck',
    name: '帕克',
    gender: 'male',
    style: '活泼男声',
    description: '语调俏皮有趣，富有表现力。适合调皮角色、搞笑故事、互动性强的内容',
    emoji: '👦'
  },
  {
    id: 'Charon',
    name: '卡戎',
    gender: 'male',
    style: '沉稳男声',
    description: '声音低沉有力，沉着冷静。适合冒险故事、神秘探索、需要可靠感的场景',
    emoji: '👨'
  },
  {
    id: 'Fenrir',
    name: '芬里尔',
    gender: 'male',
    style: '雄浑男声',
    description: '气势磅礴，充满力量感。适合史诗故事、英雄传说、勇气主题的内容',
    emoji: '👨'
  }
]

// 乐器配置
export interface InstrumentOption {
  id: string
  name: string
  category: string
  description: string
  emoji: string
}

export const INSTRUMENT_OPTIONS: InstrumentOption[] = [
  // 键盘类
  { id: 'piano', name: '钢琴', category: 'keyboard', description: '经典温暖', emoji: '🎹' },
  { id: 'electric_piano', name: '电钢琴', category: 'keyboard', description: '现代明亮', emoji: '🎹' },
  { id: 'music_box', name: '音乐盒', category: 'keyboard', description: '梦幻童趣', emoji: '🔔' },
  { id: 'accordion', name: '手风琴', category: 'keyboard', description: '欧洲民谣风', emoji: '🎹' },
  { id: 'melodica', name: '口风琴', category: 'keyboard', description: '活泼校园感', emoji: '🎹' },
  // 弦乐类
  { id: 'acoustic_guitar', name: '木吉他', category: 'string', description: '温暖自然', emoji: '🎸' },
  { id: 'ukulele', name: '尤克里里', category: 'string', description: '夏威夷风情', emoji: '🎸' },
  { id: 'violin', name: '小提琴', category: 'string', description: '优雅抒情', emoji: '🎻' },
  { id: 'cello', name: '大提琴', category: 'string', description: '深沉感人', emoji: '🎻' },
  { id: 'harp', name: '竖琴', category: 'string', description: '仙境梦幻', emoji: '🪕' },
  { id: 'strings', name: '弦乐合奏', category: 'string', description: '史诗磅礴', emoji: '🎻' },
  // 管乐类
  { id: 'saxophone', name: '萨克斯', category: 'wind', description: '爵士慵懒', emoji: '🎷' },
  { id: 'trumpet', name: '小号', category: 'wind', description: '欢快明亮', emoji: '🎺' },
  { id: 'flute', name: '长笛', category: 'wind', description: '清新悠扬', emoji: '🎺' },
  { id: 'harmonica', name: '口琴', category: 'wind', description: '怀旧田园', emoji: '🎺' },
  { id: 'clarinet', name: '单簧管', category: 'wind', description: '古典优雅', emoji: '🎺' },
  { id: 'brass', name: '管乐合奏', category: 'wind', description: '节日庆典', emoji: '🎺' },
  // 打击类
  { id: 'drums', name: '架子鼓', category: 'percussion', description: '节奏强劲', emoji: '🥁' },
  { id: 'hand_drum', name: '手鼓', category: 'percussion', description: '非洲/拉丁风', emoji: '🥁' },
  { id: 'xylophone', name: '木琴/铁琴', category: 'percussion', description: '童趣叮咚', emoji: '🔔' },
  { id: 'triangle', name: '三角铁', category: 'percussion', description: '点缀闪亮', emoji: '🔔' },
  { id: 'shaker', name: '沙锤', category: 'percussion', description: '沙沙律动', emoji: '🥁' },
  { id: 'wind_chime', name: '风铃', category: 'percussion', description: '空灵自然', emoji: '🔔' },
  // 民族/特色
  { id: 'guzheng', name: '古筝', category: 'ethnic', description: '中国古典', emoji: '🪕' },
  { id: 'pipa', name: '琵琶', category: 'ethnic', description: '灵动婉转', emoji: '🪕' },
  { id: 'erhu', name: '二胡', category: 'ethnic', description: '深情悠扬', emoji: '🪕' },
  { id: 'dizi', name: '笛子', category: 'ethnic', description: '悠远空灵', emoji: '🪕' },
  { id: 'synth', name: '电子合成', category: 'ethnic', description: '现代科技感', emoji: '🎵' },
  { id: 'chiptune', name: '8-bit复古', category: 'ethnic', description: '游戏怀旧风', emoji: '🎵' }
]

// 乐器分类
export const INSTRUMENT_CATEGORIES = [
  { id: 'keyboard', name: '键盘类', icon: '🎹' },
  { id: 'string', name: '弦乐类', icon: '🎻' },
  { id: 'wind', name: '管乐类', icon: '🎷' },
  { id: 'percussion', name: '打击类', icon: '🥁' },
  { id: 'ethnic', name: '民族/特色', icon: '🪕' }
]

// ========== 默认主题数据（前端维护，不依赖后端）==========
export const DEFAULT_THEMES: ThemeList = {
  habit: {
    name: '生活习惯',
    themes: [
      { id: 'brushing_teeth', name: '刷牙小卫士', subcategory: '卫生习惯', age_range: [24, 72], keywords: ['刷牙', '牙齿', '卫生'] },
      { id: 'eating_vegetables', name: '爱吃蔬菜', subcategory: '饮食习惯', age_range: [24, 60], keywords: ['蔬菜', '健康', '营养'] },
      { id: 'sleeping_well', name: '乖乖睡觉', subcategory: '作息习惯', age_range: [18, 48], keywords: ['睡觉', '晚安', '作息'] },
      { id: 'tidy_up', name: '收拾玩具', subcategory: '整理习惯', age_range: [24, 60], keywords: ['整理', '玩具', '收拾'] },
      { id: 'washing_hands', name: '勤洗小手', subcategory: '卫生习惯', age_range: [18, 48], keywords: ['洗手', '卫生', '细菌'] },
      { id: 'potty_training', name: '自己上厕所', subcategory: '自理能力', age_range: [18, 42], keywords: ['如厕', '自理', '独立'] },
      { id: 'dressing_self', name: '自己穿衣服', subcategory: '自理能力', age_range: [24, 60], keywords: ['穿衣', '独立', '自理'] },
      { id: 'bath_time', name: '快乐洗澡', subcategory: '卫生习惯', age_range: [18, 48], keywords: ['洗澡', '泡泡', '干净'] },
      { id: 'healthy_snacks', name: '健康小零食', subcategory: '饮食习惯', age_range: [36, 72], keywords: ['零食', '健康', '选择'] },
      { id: 'screen_time', name: '少看电视', subcategory: '生活习惯', age_range: [36, 84], keywords: ['电视', '眼睛', '户外'] }
    ]
  },
  cognition: {
    name: '认知学习',
    themes: [
      { id: 'counting', name: '数字游戏', subcategory: '数学启蒙', age_range: [24, 60], keywords: ['数字', '计数', '数学'] },
      { id: 'colors', name: '认识颜色', subcategory: '感知认知', age_range: [18, 48], keywords: ['颜色', '彩虹', '辨别'] },
      { id: 'shapes', name: '形状王国', subcategory: '几何启蒙', age_range: [24, 60], keywords: ['形状', '圆形', '方形'] },
      { id: 'letters', name: '字母冒险', subcategory: '语言启蒙', age_range: [36, 72], keywords: ['字母', 'ABC', '英语'] },
      { id: 'seasons', name: '四季变换', subcategory: '自然认知', age_range: [30, 72], keywords: ['四季', '春夏秋冬', '天气'] },
      { id: 'time', name: '认识时间', subcategory: '生活认知', age_range: [48, 84], keywords: ['时钟', '时间', '早晚'] },
      { id: 'body_parts', name: '认识身体', subcategory: '身体认知', age_range: [18, 48], keywords: ['身体', '器官', '功能'] },
      { id: 'animals', name: '动物朋友', subcategory: '自然认知', age_range: [18, 60], keywords: ['动物', '特征', '习性'] },
      { id: 'vehicles', name: '交通工具', subcategory: '生活认知', age_range: [24, 60], keywords: ['汽车', '飞机', '交通'] },
      { id: 'opposites', name: '相反概念', subcategory: '逻辑思维', age_range: [30, 60], keywords: ['大小', '高低', '对比'] }
    ]
  },
  emotion: {
    name: '情感社交',
    themes: [
      { id: 'sharing', name: '学会分享', subcategory: '社交技能', age_range: [24, 60], keywords: ['分享', '友谊', '快乐'] },
      { id: 'managing_anger', name: '控制愤怒', subcategory: '情绪管理', age_range: [30, 72], keywords: ['愤怒', '冷静', '情绪'] },
      { id: 'overcoming_fear', name: '勇敢面对', subcategory: '情绪管理', age_range: [30, 72], keywords: ['害怕', '勇敢', '克服'] },
      { id: 'making_friends', name: '交新朋友', subcategory: '社交技能', age_range: [30, 72], keywords: ['朋友', '社交', '友谊'] },
      { id: 'saying_sorry', name: '学会道歉', subcategory: '社交技能', age_range: [24, 60], keywords: ['道歉', '原谅', '错误'] },
      { id: 'accepting_loss', name: '接受失败', subcategory: '情绪管理', age_range: [36, 84], keywords: ['失败', '坚持', '成长'] },
      { id: 'expressing_love', name: '表达爱', subcategory: '情感表达', age_range: [24, 60], keywords: ['爱', '拥抱', '感谢'] },
      { id: 'dealing_sadness', name: '面对悲伤', subcategory: '情绪管理', age_range: [36, 84], keywords: ['悲伤', '安慰', '释怀'] },
      { id: 'being_patient', name: '学会等待', subcategory: '品格培养', age_range: [30, 72], keywords: ['耐心', '等待', '坚持'] },
      { id: 'gratitude', name: '感恩之心', subcategory: '品格培养', age_range: [30, 72], keywords: ['感恩', '谢谢', '珍惜'] }
    ]
  },
  social: {
    name: '社会交往',
    themes: [
      { id: 'politeness', name: '礼貌用语', subcategory: '礼仪规范', age_range: [24, 60], keywords: ['请', '谢谢', '礼貌'] },
      { id: 'taking_turns', name: '轮流玩耍', subcategory: '社交规则', age_range: [24, 60], keywords: ['轮流', '排队', '公平'] },
      { id: 'teamwork', name: '团队合作', subcategory: '合作能力', age_range: [36, 84], keywords: ['合作', '团队', '共同'] },
      { id: 'respecting_others', name: '尊重他人', subcategory: '品格培养', age_range: [36, 84], keywords: ['尊重', '倾听', '理解'] },
      { id: 'helping_others', name: '乐于助人', subcategory: '品格培养', age_range: [30, 72], keywords: ['帮助', '关心', '善良'] },
      { id: 'new_sibling', name: '迎接弟妹', subcategory: '家庭关系', age_range: [24, 72], keywords: ['弟弟', '妹妹', '家庭'] },
      { id: 'visiting_relatives', name: '走亲访友', subcategory: '社交礼仪', age_range: [30, 72], keywords: ['亲戚', '拜访', '礼物'] },
      { id: 'public_manners', name: '公共场合', subcategory: '礼仪规范', age_range: [30, 72], keywords: ['安静', '秩序', '公共'] },
      { id: 'conflict_resolution', name: '解决冲突', subcategory: '社交技能', age_range: [36, 84], keywords: ['冲突', '和解', '沟通'] },
      { id: 'stranger_safety', name: '陌生人安全', subcategory: '安全意识', age_range: [36, 84], keywords: ['陌生人', '安全', '保护'] }
    ]
  },
  creativity: {
    name: '创意想象',
    themes: [
      { id: 'space_adventure', name: '太空冒险', subcategory: '科幻想象', age_range: [36, 84], keywords: ['太空', '宇航员', '星球'] },
      { id: 'underwater_world', name: '海底世界', subcategory: '自然探索', age_range: [30, 72], keywords: ['海洋', '鱼', '潜水'] },
      { id: 'dinosaur_time', name: '恐龙时代', subcategory: '历史想象', age_range: [36, 84], keywords: ['恐龙', '远古', '探险'] },
      { id: 'fairy_tale', name: '童话王国', subcategory: '奇幻故事', age_range: [30, 72], keywords: ['公主', '王子', '魔法'] },
      { id: 'superhero', name: '小小超人', subcategory: '英雄故事', age_range: [36, 84], keywords: ['超人', '英雄', '拯救'] },
      { id: 'magic_garden', name: '魔法花园', subcategory: '奇幻故事', age_range: [24, 60], keywords: ['魔法', '花园', '精灵'] },
      { id: 'toy_adventure', name: '玩具历险', subcategory: '幻想故事', age_range: [24, 60], keywords: ['玩具', '冒险', '友谊'] },
      { id: 'dream_world', name: '梦境探险', subcategory: '幻想故事', age_range: [30, 72], keywords: ['梦', '想象', '奇遇'] },
      { id: 'time_travel', name: '时光旅行', subcategory: '科幻想象', age_range: [48, 96], keywords: ['时光', '历史', '未来'] },
      { id: 'robot_friend', name: '机器人朋友', subcategory: '科幻想象', age_range: [36, 84], keywords: ['机器人', '科技', '友谊'] }
    ]
  },
  nature: {
    name: '自然探索',
    themes: [
      { id: 'plant_growth', name: '植物生长', subcategory: '植物认知', age_range: [30, 72], keywords: ['种子', '发芽', '成长'] },
      { id: 'butterfly_life', name: '蝴蝶蜕变', subcategory: '昆虫认知', age_range: [30, 72], keywords: ['蝴蝶', '毛毛虫', '变化'] },
      { id: 'water_cycle', name: '水的旅行', subcategory: '自然现象', age_range: [48, 84], keywords: ['水', '雨', '循环'] },
      { id: 'bird_migration', name: '鸟类迁徙', subcategory: '动物认知', age_range: [48, 96], keywords: ['鸟', '迁徙', '旅行'] },
      { id: 'ant_colony', name: '蚂蚁王国', subcategory: '昆虫认知', age_range: [36, 72], keywords: ['蚂蚁', '勤劳', '团结'] },
      { id: 'weather', name: '天气变化', subcategory: '自然现象', age_range: [30, 72], keywords: ['天气', '晴天', '下雨'] },
      { id: 'moon_phases', name: '月亮变化', subcategory: '天文认知', age_range: [48, 96], keywords: ['月亮', '月相', '夜晚'] },
      { id: 'forest_animals', name: '森林动物', subcategory: '动物认知', age_range: [24, 60], keywords: ['森林', '动物', '生态'] },
      { id: 'ocean_life', name: '海洋生物', subcategory: '动物认知', age_range: [30, 72], keywords: ['海洋', '鱼类', '珊瑚'] },
      { id: 'day_night', name: '昼夜交替', subcategory: '自然现象', age_range: [30, 60], keywords: ['白天', '夜晚', '太阳'] }
    ]
  },
  safety: {
    name: '安全教育',
    themes: [
      { id: 'traffic_safety', name: '交通安全', subcategory: '出行安全', age_range: [36, 84], keywords: ['红绿灯', '斑马线', '交通'] },
      { id: 'fire_safety', name: '消防安全', subcategory: '应急安全', age_range: [36, 84], keywords: ['火', '消防', '逃生'] },
      { id: 'home_safety', name: '居家安全', subcategory: '日常安全', age_range: [30, 72], keywords: ['插座', '厨房', '危险'] },
      { id: 'water_safety', name: '水边安全', subcategory: '户外安全', age_range: [36, 84], keywords: ['游泳', '溺水', '救援'] },
      { id: 'playground_safety', name: '游乐场安全', subcategory: '户外安全', age_range: [24, 60], keywords: ['滑梯', '秋千', '安全'] },
      { id: 'food_safety', name: '食品安全', subcategory: '日常安全', age_range: [36, 72], keywords: ['食物', '过期', '卫生'] },
      { id: 'emergency_call', name: '紧急求助', subcategory: '应急安全', age_range: [48, 96], keywords: ['110', '120', '求助'] },
      { id: 'earthquake_drill', name: '地震演练', subcategory: '应急安全', age_range: [48, 96], keywords: ['地震', '躲避', '演练'] },
      { id: 'medicine_safety', name: '用药安全', subcategory: '日常安全', age_range: [36, 84], keywords: ['药品', '医生', '安全'] },
      { id: 'online_safety', name: '网络安全', subcategory: '数字安全', age_range: [60, 120], keywords: ['网络', '隐私', '安全'] }
    ]
  },
  festival: {
    name: '节日文化',
    themes: [
      { id: 'spring_festival', name: '欢乐春节', subcategory: '传统节日', age_range: [24, 84], keywords: ['春节', '红包', '团圆'] },
      { id: 'mid_autumn', name: '中秋月圆', subcategory: '传统节日', age_range: [30, 84], keywords: ['中秋', '月亮', '月饼'] },
      { id: 'dragon_boat', name: '端午龙舟', subcategory: '传统节日', age_range: [36, 84], keywords: ['端午', '龙舟', '粽子'] },
      { id: 'lantern_festival', name: '元宵灯会', subcategory: '传统节日', age_range: [24, 72], keywords: ['元宵', '灯笼', '汤圆'] },
      { id: 'birthday', name: '生日快乐', subcategory: '个人节日', age_range: [18, 84], keywords: ['生日', '蛋糕', '祝福'] },
      { id: 'mothers_day', name: '感恩母亲', subcategory: '感恩节日', age_range: [30, 84], keywords: ['妈妈', '母爱', '感恩'] },
      { id: 'fathers_day', name: '感恩父亲', subcategory: '感恩节日', age_range: [30, 84], keywords: ['爸爸', '父爱', '感谢'] },
      { id: 'teachers_day', name: '感谢老师', subcategory: '感恩节日', age_range: [36, 84], keywords: ['老师', '感恩', '教育'] },
      { id: 'childrens_day', name: '六一儿童节', subcategory: '欢庆节日', age_range: [24, 84], keywords: ['儿童节', '游戏', '快乐'] },
      { id: 'qingming', name: '清明踏青', subcategory: '传统节日', age_range: [36, 84], keywords: ['清明', '踏青', '春天'] }
    ]
  }
}

const DEFAULT_STYLE_OPTIONS: StyleOptions = {
  art_styles: ALL_ART_STYLES,
  art_style_categories: ART_STYLE_CATEGORIES,
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
    { id: 'green_hat', name: '绿色小帽', name_en: 'green hat' },
    { id: 'purple_hat', name: '紫色帽子', name_en: 'purple hat' },
    { id: 'orange_backpack', name: '橙色小书包', name_en: 'orange backpack' },
    { id: 'pink_dress', name: '粉色连衣裙', name_en: 'pink dress' },
    { id: 'green_vest', name: '绿色小马甲', name_en: 'green vest' }
  ],
  music_moods: [
    { id: 'cheerful', name: '欢乐活泼', emoji: '😄', description: '适合日常活动', detail: '节奏明快 (120-140BPM)，旋律跳跃，充满活力。适合早晨起床、户外活动、游戏时间', bpm: '120-140' },
    { id: 'gentle', name: '温柔舒缓', emoji: '😊', description: '适合安静时刻', detail: '节奏缓慢 (60-80BPM)，旋律流畅，轻柔安抚。适合睡前、午休、安静阅读', bpm: '60-80' },
    { id: 'playful', name: '俏皮可爱', emoji: '🤪', description: '适合游戏互动', detail: '节奏活泼带跳跃感，加入趣味音效。适合搞笑故事、动物模仿、亲子互动', bpm: '100-120' },
    { id: 'lullaby', name: '摇篮曲风', emoji: '🌙', description: '适合哄睡', detail: '3/4拍轻柔摇摆，如妈妈怀抱般温暖。专为哄睡、安抚情绪设计', bpm: '50-70' },
    { id: 'festival', name: '节日欢庆', emoji: '🎪', description: '适合节日派对', detail: '热闹喜庆，加入打击乐和欢呼声。适合生日、节日、派对场景', bpm: '110-130' },
    { id: 'nature', name: '自然清新', emoji: '🌿', description: '适合自然主题', detail: '融入鸟鸣、流水等自然音效，空灵治愈。适合自然探索、放松冥想', bpm: '70-90' },
    { id: 'narrative', name: '故事叙述', emoji: '🎭', description: '适合故事歌曲', detail: '旋律有起伏变化，配合情节发展。适合有剧情的故事型歌曲', bpm: '90-110' },
    { id: 'energetic', name: '律动运动', emoji: '🏃', description: '适合运动场景', detail: '强节奏感，适合跟着动起来。适合早操、舞蹈、运动歌曲', bpm: '120-150' }
  ],
  video_motion_styles: [
    { id: 'static', name: '静态微动', icon: '🖼️', description: '画面几乎静止，仅有微风、眨眼等细微动效。适合绘本插图动态化、封面展示' },
    { id: 'slow', name: '缓慢舒缓', icon: '🐢', description: '慢速平移或轻微缩放，节奏悠闲。适合睡前故事、自然风光、抒情场景' },
    { id: 'normal', name: '正常自然', icon: '🚶', description: '适中的运动速度，符合日常观感。适合大部分故事场景、日常活动' },
    { id: 'dynamic', name: '活泼动感', icon: '🏃', description: '较快节奏，角色动作明显。适合追逐游戏、运动场景、欢乐时刻' },
    { id: 'cinematic', name: '电影质感', icon: '🎬', description: '专业运镜，推拉摇移，景深变化。适合史诗场景、重要时刻、高潮片段' },
    { id: 'action', name: '动作冒险', icon: '🎢', description: '快速切换，动态张力强。适合冒险故事、紧张刺激的情节' },
    { id: 'dreamy', name: '梦幻漂浮', icon: '🌊', description: '轻盈飘动感，如在水中或云端。适合梦境、幻想世界、魔法场景' }
  ],
  tts_voices: ALL_TTS_VOICES,
  video_options: {
    models: [
      { id: 'wan2.1-i2v-plus', description: '专业版（推荐）', resolutions: ['480P', '720P'], durations: [5], has_audio: false, shot_types: ['single'], recommended: true }
    ],
    resolutions: [
      { id: '480P', name: '480P 标清', sizes: ['832*480', '480*832', '624*624'] },
      { id: '720P', name: '720P 高清', sizes: ['1280*720', '720*1280', '960*960'] },
      { id: '1080P', name: '1080P 全高清', sizes: ['1920*1080', '1080*1920', '1440*1440'] }
    ],
    durations: [
      { value: 4, label: '4秒' },
      { value: 5, label: '5秒' },
      { value: 6, label: '6秒' },
      { value: 8, label: '8秒' }
    ],
    shot_types: [
      { id: 'single', name: '单镜头', description: '单一场景连贯运动' }
    ]
  }
}

// ========== API 函数 ==========

/**
 * 获取风格选项
 */
export async function getStyleOptions(): Promise<StyleOptions> {
  try {
    const result = await request.get<StyleOptions>('/content/style-options')
    return {
      ...DEFAULT_STYLE_OPTIONS,
      ...result,
      art_styles: result.art_styles?.length ? result.art_styles : DEFAULT_STYLE_OPTIONS.art_styles,
      art_style_categories: result.art_style_categories?.length ? result.art_style_categories : DEFAULT_STYLE_OPTIONS.art_style_categories,
      protagonists: result.protagonists?.length ? result.protagonists : DEFAULT_STYLE_OPTIONS.protagonists,
      color_palettes: result.color_palettes?.length ? result.color_palettes : DEFAULT_STYLE_OPTIONS.color_palettes,
      music_moods: DEFAULT_STYLE_OPTIONS.music_moods, // 强制使用前端配置
      tts_voices: DEFAULT_STYLE_OPTIONS.tts_voices,   // 强制使用前端配置（Gemini TTS）
      video_options: result.video_options?.models?.length ? result.video_options : DEFAULT_STYLE_OPTIONS.video_options,
      video_motion_styles: DEFAULT_STYLE_OPTIONS.video_motion_styles // 强制使用前端配置
    }
  } catch {
    console.warn('[getStyleOptions] 获取后端风格选项失败，使用本地默认值')
    return DEFAULT_STYLE_OPTIONS
  }
}

/**
 * 异步生成绘本
 */
export async function generatePictureBookAsync(params: GeneratePictureBookParams): Promise<AsyncResponse> {
  return request.post<AsyncResponse>('/content/picture-book/async', params, {
    timeout: 30000
  })
}

/**
 * 获取绘本生成任务状态
 */
export async function getPictureBookTaskStatus(taskId: string): Promise<PictureBookTaskStatus> {
  return request.get<PictureBookTaskStatus>(`/content/picture-book/status/${taskId}`)
}

/**
 * 异步生成儿歌
 */
export async function generateNurseryRhymeAsync(params: GenerateNurseryRhymeParams): Promise<AsyncResponse> {
  return request.post<AsyncResponse>('/content/nursery-rhyme/async', params, {
    timeout: 30000
  })
}

/**
 * 获取儿歌生成任务状态
 */
export async function getNurseryRhymeTaskStatus(taskId: string): Promise<NurseryRhymeTaskStatus> {
  return request.get<NurseryRhymeTaskStatus>(`/content/nursery-rhyme/status/${taskId}`)
}

/**
 * 异步生成独立视频
 */
export async function generateStandaloneVideoAsync(params: GenerateStandaloneVideoParams): Promise<AsyncResponse> {
  return request.post<AsyncResponse>('/content/video/standalone/async', params, {
    timeout: 30000
  })
}

/**
 * 获取视频生成任务状态
 */
export async function getVideoTaskStatus(taskId: string): Promise<VideoTaskStatus> {
  return request.get<VideoTaskStatus>(`/content/video/status/${taskId}`)
}

/**
 * 生成视频首帧
 */
export async function generateFirstFrame(params: {
  prompt: string
  child_name: string
  art_style?: ArtStyle
  aspect_ratio?: '16:9' | '9:16' | '1:1'
}): Promise<{ image_url: string; prompt_enhanced?: string }> {
  return request.post('/content/video/first-frame', params, {
    timeout: 60000
  })
}
