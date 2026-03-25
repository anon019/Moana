import type { GroupedOptions } from './nurseryRhymeConfig'

// 语言选项
export const LANGUAGES: GroupedOptions[] = [
  {
    group: '常用语言',
    options: [
      { value: 'chinese', label: '中文' },
      { value: 'english', label: '英文' },
      { value: 'mixed', label: '中英混合' },
      { value: 'cantonese', label: '粤语' }
    ]
  },
  {
    group: '亚洲语言',
    options: [
      { value: 'japanese', label: '日语' },
      { value: 'korean', label: '韩语' },
      { value: 'thai', label: '泰语' },
      { value: 'vietnamese', label: '越南语' },
      { value: 'hindi', label: '印地语' }
    ]
  },
  {
    group: '欧洲语言',
    options: [
      { value: 'french', label: '法语' },
      { value: 'german', label: '德语' },
      { value: 'spanish', label: '西班牙语' },
      { value: 'italian', label: '意大利语' },
      { value: 'portuguese', label: '葡萄牙语' },
      { value: 'russian', label: '俄语' }
    ]
  },
  {
    group: '其他语言',
    options: [
      { value: 'arabic', label: '阿拉伯语' },
      { value: 'hebrew', label: '希伯来语' },
      { value: 'turkish', label: '土耳其语' }
    ]
  }
] as const

// 文化风格
export const CULTURAL_STYLES: GroupedOptions[] = [
  {
    group: '中华文化',
    options: [
      { value: 'chinese_traditional', label: '中国传统' },
      { value: 'chinese_modern', label: '中国现代' },
      { value: 'hk_tw', label: '港台风' },
      { value: 'guofeng', label: '古风国潮' }
    ]
  },
  {
    group: '东亚文化',
    options: [
      { value: 'japanese_healing', label: '日系治愈' },
      { value: 'korean_trend', label: '韩流时尚' },
      { value: 'japanese_traditional', label: '和风' },
      { value: 'anime', label: '动漫风' }
    ]
  },
  {
    group: '欧美文化',
    options: [
      { value: 'american_pop', label: '美式流行' },
      { value: 'british', label: '英伦优雅' },
      { value: 'french', label: '法式浪漫' },
      { value: 'nordic', label: '北欧极简' }
    ]
  },
  {
    group: '拉丁文化',
    options: [
      { value: 'latin', label: '拉丁热情' },
      { value: 'brazilian', label: '巴西桑巴' },
      { value: 'mexican', label: '墨西哥' },
      { value: 'flamenco', label: '西班牙弗拉明戈' }
    ]
  },
  {
    group: '其他文化',
    options: [
      { value: 'african', label: '非洲节奏' },
      { value: 'bollywood', label: '印度宝莱坞' },
      { value: 'middle_eastern', label: '中东异域' },
      { value: 'celtic', label: '凯尔特神秘' },
      { value: 'southeast_asian', label: '东南亚热带' },
      { value: 'mediterranean', label: '地中海阳光' },
      { value: 'hawaiian', label: '夏威夷风情' }
    ]
  }
] as const
