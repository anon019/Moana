// miniprogram/src/config/nurseryRhymeConfig.ts

/**
 * 儿歌创作增强参数配置
 * 基于 Suno V5 能力设计
 *
 * 大型数据数组已拆分到独立文件，此文件保留类型定义、核心配置和工具函数
 */

// ============================================
// 类型定义
// ============================================

// 场景预设
export interface ScenePreset {
  id: string
  name: string
  icon: string
  category: 'time' | 'function' | 'mood'
  description?: string
  params: Partial<NurseryRhymeFullParams>
}

// 完整参数接口
export interface NurseryRhymeFullParams {
  // 核心参数
  theme_topic: string
  theme_category: string
  music_mood: string
  vocal_type: string

  // 音乐风格
  music_genre: string[]
  tempo: number
  energy_level: number

  // 人声演唱
  vocal_range: string
  vocal_emotion: string
  vocal_style: string[]
  vocal_effects: string[]
  vocal_regional: string

  // 乐器配置
  instruments: string[]

  // 音效元素
  sound_effects: string[]

  // 歌词设置
  lyric_complexity: number
  repetition_level: number

  // 歌曲结构
  song_structure: string
  duration_preference: number
  action_types: string[]

  // 语言文化
  language: string
  cultural_style: string

  // 个性化
  favorite_characters: string[]
  favorite_animals: string[]
  favorite_colors: string[]
  educational_focus: string[]

  // Suno 进阶
  style_weight: number
  creativity: number
  negative_tags: string
  style_description: string
  seed?: number

  // 智能模式
  custom_prompt?: string
  inspiration_keywords: string[]
}

// 选项项接口
export interface OptionItem {
  value: string
  label: string
  icon?: string
  description?: string
}

// 分组选项接口
export interface GroupedOptions {
  group: string
  icon?: string
  options: OptionItem[]
}

// ============================================
// 从拆分文件重新导出
// ============================================

export { INSTRUMENTS_BY_FAMILY, INSTRUMENTS_BY_MOOD } from './nurseryRhymeInstruments'
export { SOUND_EFFECTS } from './nurseryRhymeSoundEffects'
export { MUSIC_GENRES } from './nurseryRhymeGenres'
export { FAVORITE_CHARACTERS, FAVORITE_ANIMALS, FAVORITE_COLORS, EDUCATIONAL_FOCUS, INSPIRATION_KEYWORDS } from './nurseryRhymePersonalization'
export { LANGUAGES, CULTURAL_STYLES } from './nurseryRhymeCulture'

// ============================================
// 场景预设（16个）
// ============================================

export const SCENE_PRESETS: ScenePreset[] = [
  // 按使用时段（6个）
  {
    id: 'morning',
    name: '早晨唤醒',
    icon: '🌅',
    category: 'time',
    params: {
      music_mood: 'cheerful',
      tempo: 120,
      energy_level: 7,
      vocal_type: 'energetic',
      music_genre: ['pop', 'children'],
      instruments: ['xylophone', 'ukulele', 'tambourine']
    }
  },
  {
    id: 'daytime',
    name: '白天玩耍',
    icon: '☀️',
    category: 'time',
    params: {
      music_mood: 'playful',
      tempo: 130,
      energy_level: 8,
      vocal_type: 'child',
      music_genre: ['children', 'dance'],
      sound_effects: ['laugh', 'cheer']
    }
  },
  {
    id: 'naptime',
    name: '午睡时间',
    icon: '😴',
    category: 'time',
    params: {
      music_mood: 'gentle',
      tempo: 75,
      energy_level: 2,
      vocal_type: 'soft_female',
      music_genre: ['lullaby', 'ambient'],
      instruments: ['piano', 'harp']
    }
  },
  {
    id: 'bathtime',
    name: '洗澡时光',
    icon: '🛁',
    category: 'time',
    params: {
      music_mood: 'cheerful',
      tempo: 100,
      energy_level: 5,
      vocal_type: 'child',
      sound_effects: ['water', 'splash'],
      action_types: ['clap', 'sway']
    }
  },
  {
    id: 'bedtime',
    name: '睡前安抚',
    icon: '🌙',
    category: 'time',
    params: {
      music_mood: 'lullaby',
      tempo: 65,
      energy_level: 1,
      vocal_type: 'soft_female',
      music_genre: ['lullaby'],
      instruments: ['piano', 'harp', 'music_box']
    }
  },
  {
    id: 'travel',
    name: '外出旅途',
    icon: '🚗',
    category: 'time',
    params: {
      music_mood: 'relaxed',
      tempo: 95,
      energy_level: 4,
      sound_effects: ['car_horn', 'train'],
      action_types: ['sway']
    }
  },

  // 按功能目的（5个）
  {
    id: 'habit',
    name: '习惯养成',
    icon: '🦷',
    category: 'function',
    params: {
      music_mood: 'cheerful',
      tempo: 105,
      repetition_level: 8,
      action_types: ['clap', 'stomp', 'finger'],
      educational_focus: ['hygiene', 'self_care']
    }
  },
  {
    id: 'learning',
    name: '认知学习',
    icon: '📚',
    category: 'function',
    params: {
      music_mood: 'cheerful',
      lyric_complexity: 5,
      vocal_type: 'clear_female',
      educational_focus: ['math', 'language', 'cognition']
    }
  },
  {
    id: 'comfort',
    name: '情绪安抚',
    icon: '🤗',
    category: 'function',
    params: {
      music_mood: 'gentle',
      tempo: 80,
      energy_level: 3,
      vocal_emotion: 'tender',
      instruments: ['strings', 'piano'],
      educational_focus: ['emotion']
    }
  },
  {
    id: 'bonding',
    name: '亲子互动',
    icon: '👨‍👩‍👧',
    category: 'function',
    params: {
      music_mood: 'cheerful',
      vocal_type: 'duet',
      song_structure: 'call_response',
      action_types: ['parent_child']
    }
  },
  {
    id: 'dance',
    name: '律动游戏',
    icon: '💃',
    category: 'function',
    params: {
      music_mood: 'energetic',
      tempo: 135,
      energy_level: 8,
      instruments: ['drums', 'percussion'],
      action_types: ['jump', 'spin', 'sway']
    }
  },

  // 按情绪氛围（5个）
  {
    id: 'party',
    name: '欢快派对',
    icon: '🎉',
    category: 'mood',
    params: {
      music_mood: 'cheerful',
      tempo: 140,
      energy_level: 9,
      music_genre: ['pop', 'dance'],
      sound_effects: ['cheer', 'fireworks']
    }
  },
  {
    id: 'sweet',
    name: '温柔甜蜜',
    icon: '🌸',
    category: 'mood',
    params: {
      music_mood: 'gentle',
      tempo: 70,
      energy_level: 3,
      music_genre: ['folk', 'acoustic'],
      vocal_type: 'soft_female',
      instruments: ['piano', 'guitar']
    }
  },
  {
    id: 'funny',
    name: '俏皮搞怪',
    icon: '🎪',
    category: 'mood',
    params: {
      music_mood: 'playful',
      tempo: 115,
      energy_level: 6,
      vocal_type: 'child',
      sound_effects: ['funny', 'boing', 'whistle']
    }
  },
  {
    id: 'magical',
    name: '神秘探索',
    icon: '✨',
    category: 'mood',
    params: {
      music_mood: 'mysterious',
      tempo: 95,
      energy_level: 5,
      music_genre: ['new_age', 'cinematic'],
      sound_effects: ['magic', 'fairy'],
      song_structure: 'narrative'
    }
  },
  {
    id: 'active',
    name: '活力四射',
    icon: '🏃',
    category: 'mood',
    params: {
      music_mood: 'energetic',
      tempo: 145,
      energy_level: 9,
      music_genre: ['electronic', 'dance'],
      action_types: ['jump', 'run']
    }
  }
] as const

// ============================================
// 核心参数选项
// ============================================

// 音乐氛围（8种）
export const MUSIC_MOODS: OptionItem[] = [
  { value: 'cheerful', label: '欢快活泼', icon: '🎉', description: '节奏明快，充满活力' },
  { value: 'gentle', label: '温柔舒缓', icon: '🌸', description: '轻柔优美，温馨甜蜜' },
  { value: 'playful', label: '俏皮可爱', icon: '🎈', description: '趣味十足，朗朗上口' },
  { value: 'lullaby', label: '摇篮曲风', icon: '🌙', description: '安静柔和，适合入睡' },
  { value: 'energetic', label: '活力动感', icon: '⚡', description: '热情奔放，动感十足' },
  { value: 'mysterious', label: '神秘奇幻', icon: '✨', description: '梦幻探险，充满想象' },
  { value: 'inspiring', label: '励志温暖', icon: '💪', description: '正能量，鼓励成长' },
  { value: 'relaxed', label: '悠闲放松', icon: '🍃', description: '轻松自在，无压力' }
] as const

// 人声类型（6种）
export const VOCAL_TYPES: OptionItem[] = [
  { value: 'soft_female', label: '甜美女声', icon: '👩', description: '温柔清亮，适合大多数儿歌' },
  { value: 'warm_male', label: '温暖男声', icon: '👨', description: '稳重亲切，适合励志/教育类' },
  { value: 'child', label: '可爱童声', icon: '👧', description: '稚嫩天真，代入感强' },
  { value: 'chorus', label: '欢乐合唱', icon: '👨‍👩‍👧', description: '多人声，氛围感强' },
  { value: 'duet', label: '亲子对唱', icon: '👩‍👦', description: '一大一小，互动感强' },
  { value: 'instrumental', label: '纯音乐', icon: '🎵', description: '无人声，纯乐器演奏' }
] as const

// 节奏速度提示
export const TEMPO_HINTS = [
  { min: 60, max: 80, label: '极慢', description: '适合摇篮曲/冥想' },
  { min: 80, max: 100, label: '慢速', description: '适合舒缓放松' },
  { min: 100, max: 120, label: '中速', description: '适合日常儿歌' },
  { min: 120, max: 140, label: '中快', description: '适合活泼欢快' },
  { min: 140, max: 180, label: '快速', description: '适合动感舞蹈' }
] as const

// 能量强度提示
export const ENERGY_HINTS = [
  { min: 1, max: 2, label: '静谧' },
  { min: 3, max: 4, label: '轻柔' },
  { min: 5, max: 6, label: '温和' },
  { min: 7, max: 8, label: '活力' },
  { min: 9, max: 10, label: '激昂' }
] as const

// ============================================
// 高级参数 - 人声演唱
// ============================================

// 音域选择
export const VOCAL_RANGES: OptionItem[] = [
  { value: 'high', label: '高音', description: '明亮清澈，穿透力强' },
  { value: 'mid', label: '中音', description: '自然舒适，适用广泛' },
  { value: 'low', label: '低音', description: '沉稳温暖，有安全感' }
] as const

// 情感表达
export const VOCAL_EMOTIONS: OptionItem[] = [
  { value: 'happy', label: '欢快' },
  { value: 'tender', label: '深情' },
  { value: 'playful', label: '俏皮' },
  { value: 'calm', label: '沉稳' },
  { value: 'dreamy', label: '梦幻' },
  { value: 'passionate', label: '激昂' },
  { value: 'gentle', label: '温柔' },
  { value: 'mysterious', label: '神秘' }
] as const

// 演唱技巧
export const VOCAL_TECHNIQUES: OptionItem[] = [
  { value: 'clear', label: '清唱' },
  { value: 'harmony', label: '和声伴唱' },
  { value: 'rap', label: '说唱段落' },
  { value: 'chant', label: '吟唱' },
  { value: 'hum', label: '哼唱' },
  { value: 'breathy', label: '气声' },
  { value: 'vibrato', label: '颤音' }
] as const

// 声音效果
export const VOCAL_EFFECTS: OptionItem[] = [
  { value: 'reverb', label: '混响', description: '增加空间感' },
  { value: 'delay', label: '延迟', description: '回声效果' },
  { value: 'autotune', label: '电音处理', description: '机器人效果' },
  { value: 'vintage', label: '复古质感', description: '老唱片温暖感' }
] as const

// 地域特色
export const VOCAL_REGIONALS: OptionItem[] = [
  { value: 'american', label: '美式' },
  { value: 'british', label: '英伦' },
  { value: 'japanese', label: '日系' },
  { value: 'korean', label: '韩系' },
  { value: 'chinese', label: '中国风' },
  { value: 'latin', label: '拉丁' }
] as const

// ============================================
// 高级参数 - 歌词设置
// ============================================

// 歌词复杂度提示
export const LYRIC_COMPLEXITY_HINTS = [
  { min: 1, max: 2, label: '极简', description: '单词重复，适合 1-2 岁' },
  { min: 3, max: 4, label: '简单', description: '短句为主，适合 2-3 岁' },
  { min: 5, max: 6, label: '中等', description: '完整句子，适合 3-4 岁' },
  { min: 7, max: 8, label: '丰富', description: '多段落，适合 4-5 岁' },
  { min: 9, max: 10, label: '复杂', description: '故事性强，适合 5-6 岁' }
] as const

// 重复程度提示
export const REPETITION_HINTS = [
  { min: 1, max: 2, label: '极少', description: '几乎不重复，变化丰富' },
  { min: 3, max: 4, label: '较少', description: '少量重复，保持新鲜' },
  { min: 5, max: 6, label: '适中', description: '适度重复，平衡变化' },
  { min: 7, max: 8, label: '较多', description: '副歌多次重复，易记忆' },
  { min: 9, max: 10, label: '洗脑循环', description: '高度重复，过耳不忘' }
] as const

// ============================================
// 高级参数 - 歌曲结构
// ============================================

// 歌曲结构类型
export const SONG_STRUCTURES: OptionItem[] = [
  { value: 'simple', label: '简单循环', description: 'A-A-A' },
  { value: 'standard', label: '标准结构', description: 'A-B-A-B' },
  { value: 'full', label: '完整结构', description: 'Intro-A-B-A-B-Outro' },
  { value: 'chorus_only', label: '纯副歌循环', description: 'B-B-B' },
  { value: 'progressive', label: '渐进式', description: "A-A'-A''-B" },
  { value: 'narrative', label: '故事叙事', description: 'A-B-C-D' },
  { value: 'call_response', label: '问答互动', description: 'Q-A-Q-A' },
  { value: 'rap', label: '说唱结构', description: 'Rap-B-Rap-B' },
  { value: 'aaba', label: 'AABA 曲式', description: 'A-A-B-A' },
  { value: 'custom', label: '自定义', description: '输入标签' }
] as const

// 可用的结构标签
export const STRUCTURE_TAGS = [
  '[Intro]', '[Verse]', '[Chorus]', '[Bridge]', '[Outro]',
  '[Pre-Chorus]', '[Interlude]', '[Solo]', '[Rap]', '[Whisper]'
] as const

// 动作指引类型
export const ACTION_TYPES: OptionItem[] = [
  { value: 'clap', label: '拍手', icon: '👏', description: '跟随节奏拍手' },
  { value: 'stomp', label: '跺脚', icon: '🦶', description: '跟随节奏跺脚' },
  { value: 'spin', label: '转圈', icon: '🔄', description: '原地转圈圈' },
  { value: 'sway', label: '摇摆', icon: '💃', description: '左右摇摆身体' },
  { value: 'jump', label: '跳跃', icon: '🦘', description: '跟随节奏跳跃' },
  { value: 'finger', label: '手指操', icon: '🖐️', description: '手指动作配合' },
  { value: 'expression', label: '表情互动', icon: '😊', description: '做各种表情' },
  { value: 'parent_child', label: '亲子配合', icon: '👨‍👩‍👧', description: '需要大人配合' }
] as const

// ============================================
// 高级参数 - Suno 进阶控制
// ============================================

// 预设组合
export const SUNO_PRESETS = [
  { id: 'safe', name: '安全稳定', icon: '🛡️', style_weight: 0.8, creativity: 0.2, description: '追求可控结果' },
  { id: 'balanced', name: '平衡推荐', icon: '⚖️', style_weight: 0.5, creativity: 0.5, description: '通用默认选择' },
  { id: 'explore', name: '大胆探索', icon: '🚀', style_weight: 0.3, creativity: 0.8, description: '期待惊喜创意' },
  { id: 'precise', name: '精准复刻', icon: '🎯', style_weight: 0.95, creativity: 0.1, description: '严格按描述生成' }
] as const

// 常用排除项
export const COMMON_NEGATIVE_TAGS: OptionItem[] = [
  { value: 'heavy_metal', label: '不要重金属' },
  { value: 'death_metal', label: '不要死亡金属' },
  { value: 'hardcore_rap', label: '不要硬核说唱' },
  { value: 'horror', label: '不要恐怖氛围' },
  { value: 'distortion', label: '不要电音失真' },
  { value: 'screaming', label: '不要嘶吼人声' }
] as const

// ============================================
// 智能联动规则
// ============================================

// 氛围 → 参数联动
export const MOOD_LINKAGE: Record<string, Partial<NurseryRhymeFullParams>> = {
  cheerful: {
    tempo: 130,
    energy_level: 7,
    music_genre: ['pop', 'dance'],
    vocal_emotion: 'happy',
    instruments: ['xylophone', 'tambourine']
  },
  gentle: {
    tempo: 80,
    energy_level: 3,
    music_genre: ['folk', 'classical'],
    vocal_emotion: 'tender',
    instruments: ['piano', 'guitar']
  },
  playful: {
    tempo: 110,
    energy_level: 6,
    music_genre: ['children'],
    vocal_type: 'child',
    instruments: ['ukulele', 'xylophone']
  },
  lullaby: {
    tempo: 70,
    energy_level: 1,
    music_genre: ['lullaby'],
    vocal_emotion: 'gentle',
    instruments: ['piano', 'harp', 'music_box']
  },
  energetic: {
    tempo: 145,
    energy_level: 9,
    music_genre: ['electronic', 'dance'],
    instruments: ['synth', 'drums']
  },
  mysterious: {
    tempo: 100,
    energy_level: 5,
    music_genre: ['new_age', 'cinematic'],
    vocal_emotion: 'dreamy',
    sound_effects: ['magic', 'fairy']
  },
  inspiring: {
    tempo: 110,
    energy_level: 7,
    music_genre: ['pop'],
    vocal_type: 'chorus',
    instruments: ['strings', 'piano']
  },
  relaxed: {
    tempo: 90,
    energy_level: 4,
    music_genre: ['bossa_nova', 'acoustic'],
    vocal_emotion: 'calm',
    instruments: ['guitar', 'harmonica']
  }
} as const

// 流派 → 乐器联动
export const GENRE_INSTRUMENT_LINKAGE: Record<string, string[]> = {
  children: ['xylophone', 'tambourine', 'ukulele', 'toy_piano'],
  classical: ['piano', 'violin', 'cello', 'flute'],
  jazz: ['saxophone', 'piano', 'bass', 'drums'],
  electronic: ['synth', 'drum_machine', '808'],
  folk: ['guitar', 'harmonica', 'bongo'],
  chinese_traditional: ['guzheng', 'dizi', 'erhu', 'pipa'],
  rock: ['electric_guitar', 'bass', 'drums']
} as const

// 人声 → 情感/技巧联动
export const VOCAL_LINKAGE: Record<string, { emotion: string; techniques: string[] }> = {
  soft_female: { emotion: 'tender', techniques: ['clear'] },
  warm_male: { emotion: 'calm', techniques: ['clear'] },
  child: { emotion: 'happy', techniques: ['clear', 'hum'] },
  chorus: { emotion: 'happy', techniques: ['harmony'] },
  duet: { emotion: 'tender', techniques: ['clear'] }
} as const

// ============================================
// 参数帮助说明
// ============================================

export const PARAM_HELP: Record<string, string> = {
  music_genre: '决定歌曲的整体风格，就像选择穿什么类型的衣服',
  tempo: '歌曲的快慢，数字越大越欢快动感，越小越安静舒缓',
  energy_level: '歌曲的"热闹程度"，睡前选低能量，玩耍选高能量',
  style_weight: 'Suno 有多听你的话，100%=完全按你说的，0%=它自由发挥',
  creativity: '允许 Suno 有多少"个人发挥"，高=惊喜多，低=更稳定',
  song_structure: '歌曲的"骨架"，决定主歌副歌怎么排列',
  repetition_level: '歌词重复多少次，重复多=容易记住，重复少=内容丰富',
  lyric_complexity: '歌词的难度，根据孩子年龄选择合适的复杂度'
} as const

// ============================================
// 默认参数值
// ============================================

export const DEFAULT_PARAMS: Partial<NurseryRhymeFullParams> = {
  music_mood: 'cheerful',
  vocal_type: 'soft_female',
  tempo: 100,
  energy_level: 5,
  lyric_complexity: 5,
  repetition_level: 6,
  duration_preference: 90,
  style_weight: 0.5,
  creativity: 0.5,
  language: 'chinese'
} as const

// ============================================
// 工具函数
// ============================================

/**
 * 获取场景预设的完整参数（合并默认值）
 */
export function getScenePresetParams(presetId: string): Partial<NurseryRhymeFullParams> {
  const preset = SCENE_PRESETS.find(p => p.id === presetId)
  if (!preset) return { ...DEFAULT_PARAMS }
  return { ...DEFAULT_PARAMS, ...preset.params }
}

/**
 * 根据氛围获取推荐参数
 */
export function getMoodLinkageParams(mood: string): Partial<NurseryRhymeFullParams> {
  return MOOD_LINKAGE[mood] || {}
}

/**
 * 获取节奏提示文字
 */
export function getTempoHint(tempo: number): string {
  const hint = TEMPO_HINTS.find(h => tempo >= h.min && tempo <= h.max)
  return hint ? `${hint.label} - ${hint.description}` : ''
}

/**
 * 获取能量提示文字
 */
export function getEnergyHint(energy: number): string {
  const hint = ENERGY_HINTS.find(h => energy >= h.min && energy <= h.max)
  return hint?.label || ''
}

/**
 * 获取歌词复杂度提示
 */
export function getLyricComplexityHint(complexity: number): string {
  const hint = LYRIC_COMPLEXITY_HINTS.find(h => complexity >= h.min && complexity <= h.max)
  return hint ? `${hint.label} - ${hint.description}` : ''
}

/**
 * 获取重复程度提示
 */
export function getRepetitionHint(repetition: number): string {
  const hint = REPETITION_HINTS.find(h => repetition >= h.min && repetition <= h.max)
  return hint ? `${hint.label} - ${hint.description}` : ''
}
