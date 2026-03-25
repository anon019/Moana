import type { GroupedOptions } from './nurseryRhymeConfig'

// 喜欢的角色
export const FAVORITE_CHARACTERS: GroupedOptions[] = [
  {
    group: '童话角色',
    options: [
      { value: 'princess', label: '公主' },
      { value: 'prince', label: '王子' },
      { value: 'fairy', label: '仙女' },
      { value: 'elf', label: '精灵' },
      { value: 'dwarf', label: '小矮人' },
      { value: 'witch_good', label: '善良巫婆' },
      { value: 'giant', label: '巨人' }
    ]
  },
  {
    group: '动画角色',
    options: [
      { value: 'superhero', label: '超级英雄' },
      { value: 'robot', label: '机器人' },
      { value: 'magical_girl', label: '魔法少女' },
      { value: 'monster', label: '小怪兽' },
      { value: 'cartoon_animal', label: '卡通动物' }
    ]
  },
  {
    group: '职业角色',
    options: [
      { value: 'doctor', label: '医生' },
      { value: 'firefighter', label: '消防员' },
      { value: 'police', label: '警察' },
      { value: 'teacher', label: '老师' },
      { value: 'astronaut', label: '宇航员' },
      { value: 'chef', label: '厨师' },
      { value: 'scientist', label: '科学家' }
    ]
  },
  {
    group: '奇幻生物',
    options: [
      { value: 'unicorn', label: '独角兽' },
      { value: 'dragon_friendly', label: '友善龙' },
      { value: 'phoenix', label: '凤凰' },
      { value: 'mermaid', label: '美人鱼' },
      { value: 'dinosaur', label: '小恐龙' },
      { value: 'alien', label: '外星人' }
    ]
  }
] as const

// 喜欢的动物
export const FAVORITE_ANIMALS: GroupedOptions[] = [
  {
    group: '哺乳动物',
    options: [
      { value: 'rabbit', label: '兔子' },
      { value: 'bear', label: '小熊' },
      { value: 'cat', label: '小猫' },
      { value: 'dog', label: '小狗' },
      { value: 'panda', label: '熊猫' },
      { value: 'fox', label: '狐狸' },
      { value: 'lion', label: '狮子' },
      { value: 'tiger', label: '老虎' },
      { value: 'elephant', label: '大象' },
      { value: 'monkey', label: '猴子' },
      { value: 'squirrel', label: '松鼠' }
    ]
  },
  {
    group: '鸟类',
    options: [
      { value: 'bird', label: '小鸟' },
      { value: 'parrot', label: '鹦鹉' },
      { value: 'owl', label: '猫头鹰' },
      { value: 'penguin', label: '企鹅' },
      { value: 'chicken', label: '小鸡' },
      { value: 'swan', label: '天鹅' },
      { value: 'peacock', label: '孔雀' }
    ]
  },
  {
    group: '海洋生物',
    options: [
      { value: 'fish', label: '小鱼' },
      { value: 'dolphin', label: '海豚' },
      { value: 'whale', label: '鲸鱼' },
      { value: 'turtle', label: '海龟' },
      { value: 'octopus', label: '章鱼' },
      { value: 'crab', label: '螃蟹' },
      { value: 'starfish', label: '海星' }
    ]
  },
  {
    group: '昆虫',
    options: [
      { value: 'butterfly', label: '蝴蝶' },
      { value: 'bee', label: '蜜蜂' },
      { value: 'ladybug', label: '瓢虫' },
      { value: 'dragonfly', label: '蜻蜓' },
      { value: 'firefly', label: '萤火虫' }
    ]
  },
  {
    group: '恐龙',
    options: [
      { value: 't_rex', label: '霸王龙' },
      { value: 'triceratops', label: '三角龙' },
      { value: 'pterodactyl', label: '翼龙' },
      { value: 'stegosaurus', label: '剑龙' },
      { value: 'brachiosaurus', label: '腕龙' }
    ]
  },
  {
    group: '神话动物',
    options: [
      { value: 'dragon', label: '龙' },
      { value: 'phoenix', label: '凤凰' },
      { value: 'qilin', label: '麒麟' },
      { value: 'unicorn', label: '独角兽' }
    ]
  }
] as const

// 喜欢的颜色
export const FAVORITE_COLORS: GroupedOptions[] = [
  {
    group: '基础色',
    options: [
      { value: 'red', label: '红', icon: '🔴' },
      { value: 'orange', label: '橙', icon: '🟠' },
      { value: 'yellow', label: '黄', icon: '🟡' },
      { value: 'green', label: '绿', icon: '🟢' },
      { value: 'blue', label: '蓝', icon: '🔵' },
      { value: 'purple', label: '紫', icon: '🟣' },
      { value: 'pink', label: '粉', icon: '💗' },
      { value: 'white', label: '白', icon: '⚪' },
      { value: 'black', label: '黑', icon: '⚫' },
      { value: 'brown', label: '棕', icon: '🟤' }
    ]
  },
  {
    group: '渐变色',
    options: [
      { value: 'rainbow', label: '彩虹', icon: '🌈' },
      { value: 'sunset', label: '日落渐变', icon: '🌅' },
      { value: 'ocean', label: '海洋渐变', icon: '🌊' },
      { value: 'sakura', label: '樱花渐变', icon: '🌸' }
    ]
  },
  {
    group: '特殊色',
    options: [
      { value: 'starry', label: '星空色', icon: '✨' },
      { value: 'candy', label: '糖果色', icon: '🍬' },
      { value: 'dreamy', label: '梦幻色', icon: '🦄' },
      { value: 'forest', label: '森林绿', icon: '🌿' },
      { value: 'beach', label: '沙滩金', icon: '🏖️' }
    ]
  }
] as const

// 教育目标
export const EDUCATIONAL_FOCUS: GroupedOptions[] = [
  {
    group: '认知发展',
    options: [
      { value: 'math', label: '数学启蒙' },
      { value: 'color', label: '颜色认知' },
      { value: 'shape', label: '形状认知' },
      { value: 'time', label: '时间概念' },
      { value: 'space', label: '空间感知' },
      { value: 'cause_effect', label: '因果关系' },
      { value: 'classify', label: '分类归纳' },
      { value: 'logic', label: '逻辑思维' },
      { value: 'problem_solving', label: '问题解决' }
    ]
  },
  {
    group: '语言发展',
    options: [
      { value: 'language', label: '语言表达' },
      { value: 'vocabulary', label: '词汇积累' },
      { value: 'pinyin', label: '拼音学习' },
      { value: 'english', label: '英语启蒙' },
      { value: 'reading', label: '阅读兴趣' },
      { value: 'story', label: '故事理解' }
    ]
  },
  {
    group: '社会情感',
    options: [
      { value: 'emotion', label: '情绪管理' },
      { value: 'social', label: '社交技能' },
      { value: 'sharing', label: '分享合作' },
      { value: 'empathy', label: '同理心' },
      { value: 'confidence', label: '自信心' },
      { value: 'manners', label: '礼仪礼貌' },
      { value: 'safety', label: '安全意识' }
    ]
  },
  {
    group: '身体运动',
    options: [
      { value: 'coordination', label: '肢体协调' },
      { value: 'fine_motor', label: '精细动作' },
      { value: 'gross_motor', label: '大肌肉运动' },
      { value: 'rhythm', label: '节奏感' },
      { value: 'balance', label: '平衡能力' }
    ]
  },
  {
    group: '生活习惯',
    options: [
      { value: 'eating', label: '饮食习惯' },
      { value: 'hygiene', label: '卫生习惯' },
      { value: 'sleep', label: '作息习惯' },
      { value: 'tidy', label: '整理习惯' },
      { value: 'self_care', label: '自理能力' }
    ]
  },
  {
    group: '艺术审美',
    options: [
      { value: 'music', label: '音乐欣赏' },
      { value: 'art', label: '艺术感知' },
      { value: 'creativity', label: '创造力' },
      { value: 'imagination', label: '想象力' },
      { value: 'aesthetic', label: '审美能力' }
    ]
  },
  {
    group: '自然科学',
    options: [
      { value: 'animals', label: '动物认知' },
      { value: 'plants', label: '植物认知' },
      { value: 'weather', label: '天气自然' },
      { value: 'environment', label: '环保意识' },
      { value: 'science', label: '科学探索' }
    ]
  }
] as const

// 灵感关键词推荐
export const INSPIRATION_KEYWORDS: GroupedOptions[] = [
  {
    group: '主题词',
    options: [
      { value: 'dream', label: '梦想' },
      { value: 'friendship', label: '友谊' },
      { value: 'courage', label: '勇气' },
      { value: 'growth', label: '成长' },
      { value: 'love', label: '爱' }
    ]
  },
  {
    group: '情感词',
    options: [
      { value: 'happy', label: '快乐' },
      { value: 'warm', label: '温暖' },
      { value: 'mysterious', label: '神秘' },
      { value: 'energetic', label: '活力' },
      { value: 'peaceful', label: '安静' }
    ]
  },
  {
    group: '场景词',
    options: [
      { value: 'forest', label: '森林' },
      { value: 'ocean', label: '海洋' },
      { value: 'space', label: '太空' },
      { value: 'castle', label: '城堡' },
      { value: 'garden', label: '花园' }
    ]
  },
  {
    group: '动作词',
    options: [
      { value: 'dance', label: '跳舞' },
      { value: 'run', label: '奔跑' },
      { value: 'fly', label: '飞翔' },
      { value: 'spin', label: '旋转' },
      { value: 'hug', label: '拥抱' }
    ]
  }
] as const
